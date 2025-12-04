# Scénarios de Test RAVEN - Topologies Réalistes

## Topologie 1 : Datacenter (datacenter_topology.py)

### Architecture

- **2 Core switches** : Liens ultra-rapides (100Gbps, 1ms)
- **4 Spine switches** : Liens rapides (40Gbps, 2ms)
- **6 Leaf switches** : Liens variables (10Gbps, 5-12ms, 0-3% perte)
- **6 Serveurs** : Connexions standard (1Gbps, 10ms)

### Lancer la topologie

```bash
docker exec -it mininet bash
service openvswitch-switch start
python3 /topologies/datacenter_topology.py
```

### Scénario 1 : Comparer les chemins

**Dans Mininet :**

```bash
mininet> h1 ping -c 10 h6
```

**Dans un autre terminal :**

```bash
docker logs -f raven-controller
```

**Ce que vous devriez voir :**

- RAVEN calcule plusieurs chemins possibles entre h1 et h6
- Les chemins via les bons liens (faible latence, pas de perte) ont des scores plus élevés
- RAVEN évite automatiquement les liens dégradés (s6-s11 avec 12ms et 3% perte)

### Scénario 2 : Panne d'un lien de qualité

**Couper un bon lien :**

```bash
mininet> link s3 s7 down
```

**Observer RAVEN :**

- Le graphe se reconstruit
- RAVEN recalcule les chemins
- Peut être forcé d'utiliser des liens moins bons
- Les scores des chemins diminuent

**Tester la connectivité :**

```bash
mininet> h1 ping -c 10 h2
```

Le trafic passe toujours, mais via un chemin alternatif.

### Scénario 3 : Mesurer la bande passante

```bash
mininet> iperf h1 h6
```

Comparez avec un chemin qui utilise des liens dégradés :

```bash
# Couper les bons liens pour forcer un mauvais chemin
mininet> link s3 s7 down
mininet> link s5 s9 down
mininet> iperf h1 h6
```

Vous devriez voir une différence de débit.

---

## Topologie 2 : Entreprise Multi-Sites (enterprise_multisite_topology.py)

### Architecture

- **3 Sites** : Paris, Londres, Berlin
- **LAN rapide** : 1Gbps, 1ms (intra-site)
- **WAN principal** : 50-100Mbps, 20-30ms, 0.5-2% perte
- **WAN backup** : 5-10Mbps, 100-150ms, 3-5% perte

### Lancer la topologie

```bash
docker exec -it mininet bash
service openvswitch-switch start
python3 /topologies/enterprise_multisite_topology.py
```

### Scénario 1 : Trafic local vs inter-sites

**Trafic local (Paris) :**

```bash
mininet> h1 ping -c 10 h2
```

Devrait être très rapide (~1-2ms).

**Trafic inter-sites (Paris -> Londres) :**

```bash
mininet> h1 ping -c 10 h4
```

Plus lent (~20-30ms) car passe par le WAN.

**Observer RAVEN :**

```bash
docker logs -f raven-controller
```

RAVEN devrait choisir le WAN principal (via s7) et éviter le backup direct.

### Scénario 2 : Panne du WAN principal

**Couper le WAN principal de Paris :**

```bash
mininet> link s1 s7 down
```

**Tester la connectivité Paris -> Londres :**

```bash
mininet> h1 ping -c 10 h4
```

**Ce qui se passe :**

- RAVEN détecte que le chemin via s7 n'existe plus
- Il bascule sur le lien backup direct s1-s4
- La latence explose (~100ms au lieu de ~20ms)
- Plus de perte de paquets (3% au lieu de 0.5%)

**Observer les scores RAVEN :**

- Avant panne : Score élevé pour chemin via s7
- Après panne : Score faible pour chemin backup, mais c'est le seul disponible

### Scénario 3 : Comparer les performances

**Mesurer la bande passante avec WAN principal :**

```bash
mininet> iperf h1 h4
```

Devrait donner ~100Mbps.

**Couper le WAN principal et mesurer avec backup :**

```bash
mininet> link s1 s7 down
mininet> iperf h1 h4
```

Devrait donner ~10Mbps (10x plus lent !).

**Restaurer et comparer :**

```bash
mininet> link s1 s7 up
mininet> iperf h1 h4
```

Retour à ~100Mbps.

---

## Comprendre les Scores RAVEN

### Formule

```
Score = 0.6 × Fiabilité + 0.4 × (Bande_Passante/Max) - 0.1 × Nombre_Sauts
```

### Exemples de calcul

**Chemin 1 : Via bon lien**

- 3 sauts
- 100Mbps bande passante (normalisé = 1.0)
- 99% fiabilité (0.99)

```
Score = 0.6 × 0.99 + 0.4 × 1.0 - 0.1 × 3
      = 0.594 + 0.4 - 0.3
      = 0.694
```

**Chemin 2 : Via lien dégradé**

- 3 sauts
- 10Mbps bande passante (normalisé = 0.1)
- 95% fiabilité (0.95)

```
Score = 0.6 × 0.95 + 0.4 × 0.1 - 0.1 × 3
      = 0.57 + 0.04 - 0.3
      = 0.31
```

**RAVEN choisit le Chemin 1** (score 0.694 > 0.31)

---

## Tests Avancés

### Test 1 : Cascade de pannes

```bash
# Couper plusieurs liens progressivement
mininet> link s1 s7 down
mininet> link s4 s7 down
mininet> link s8 s7 down
```

Observer comment RAVEN s'adapte à chaque panne.

### Test 2 : Restauration progressive

```bash
# Restaurer les liens un par un
mininet> link s1 s7 up
# Observer RAVEN recalculer
mininet> link s4 s7 up
# Observer à nouveau
```

RAVEN devrait immédiatement préférer les meilleurs chemins restaurés.

### Test 3 : Trafic simultané

```bash
# Dans Mininet, ouvrir plusieurs xterms
mininet> xterm h1 h4 h7

# Dans h1
h1# ping h4

# Dans h4
h4# ping h7

# Dans h7
h7# ping h1
```

Observer comment RAVEN gère plusieurs flux simultanés.

---

## Indicateurs de Succès

### RAVEN fonctionne bien si :

✅ **Choix intelligent** : Préfère les chemins avec :

- Faible latence
- Haute bande passante
- Faible perte de paquets
- Moins de sauts

✅ **Adaptation rapide** : Détecte les pannes en ~10 secondes et recalcule

✅ **Évitement proactif** : N'utilise les liens backup que si nécessaire

✅ **Scores cohérents** : Les meilleurs chemins ont toujours les scores les plus élevés

### Comparer avec routage par défaut

Pour voir la différence, vous pouvez :

1. Noter les performances avec RAVEN actif
2. Arrêter RAVEN : `docker stop raven-controller`
3. Laisser ONOS utiliser son routage par défaut
4. Comparer les latences et débits

Le routage par défaut choisira souvent le chemin le plus court (moins de sauts) même s'il est de mauvaise qualité.

---

## Commandes Utiles

```bash
# Voir la topologie
mininet> net

# Voir tous les liens
mininet> links

# Tester tous les hôtes
mininet> pingall

# Mesurer latence
mininet> h1 ping -c 20 h6

# Mesurer bande passante
mininet> iperf h1 h6

# Couper/restaurer un lien
mininet> link s1 s2 down
mininet> link s1 s2 up

# Ouvrir un terminal sur un hôte
mininet> xterm h1

# Quitter
mininet> exit
```

---

## Logs RAVEN à Surveiller

```bash
# Voir en temps réel
docker logs -f raven-controller

# Voir les dernières lignes
docker logs raven-controller --tail 50

# Chercher un chemin spécifique
docker logs raven-controller | grep "h1.*h6"
```

**Ce que vous devriez voir :**

- `Graph built: X nodes, Y edges` - Topologie découverte
- `Found N hosts` - Hôtes détectés
- `Path ... Score = X.XXX` - Calcul des scores
- `Selected path: ...` - Meilleur chemin choisi
- `Best path ... -> ...` - Résumé de la décision
