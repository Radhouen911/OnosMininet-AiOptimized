# Démarrage Rapide : RAVEN avec Docker Compose

## Ce Que Vous Obtenez

Un environnement SDN complet avec sélection de chemins RAVEN fonctionnant dans Docker :

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Mininet    │────▶│     ONOS     │◀────│    RAVEN     │
│   (Réseau)   │     │ (Contrôleur) │     │ (Algorithme) │
└──────────────┘     └──────────────┘     └──────────────┘
  Crée topologie     Gère commutateurs    Sélectionne chemins
  Lance commutateurs Contrôle OpenFlow    Requêtes API REST
  Hôtes virtuels     Installation flux    Routage intelligent
```

## 1. Tout Démarrer (Une Commande)

```bash
docker-compose up -d
```

Attendez ~60 secondes pour l'initialisation d'ONOS.

## 2. Vérifier Que Ça Fonctionne

```bash
# Vérifier les conteneurs
docker-compose ps

# Devrait afficher :
# - onos (running)
# - mininet (running)
# - raven-controller (running)
```

## 3. Créer un Réseau de Test

```bash
# Entrer dans le conteneur Mininet
docker exec -it mininet bash

# À l'intérieur du conteneur :
service openvswitch-switch start
python3 /topologies/raven_test_topology.py
```

Cela crée un réseau avec plusieurs chemins entre les hôtes.

## 4. Voir RAVEN en Action

Ouvrez un nouveau terminal :

```bash
docker logs -f raven-controller
```

Vous verrez RAVEN :

- Découvrir la topologie
- Calculer les scores de chemins
- Sélectionner les meilleurs chemins

Exemple de sortie :

```
INFO - Graph built: 10 nodes, 14 edges
INFO - Found 4 hosts
INFO - Path h1 -> s1 -> s2 -> s3 -> s4 -> h2: Score = 0.840
INFO - Path h1 -> s1 -> s5 -> s6 -> s4 -> h2: Score = 0.620
INFO - Selected path: h1 -> s1 -> s2 -> s3 -> s4 -> h2 (Score: 0.840)
```

## 5. Tester la Connectivité

Dans le CLI Mininet :

```bash
mininet> pingall
# Tous les hôtes devraient pouvoir se pinguer

mininet> iperf h1 h2
# Tester la bande passante entre h1 et h2
```

## 6. Tester l'Intelligence de RAVEN

Simuler une panne de lien :

```bash
mininet> link s1 s2 down
```

Regardez les logs RAVEN - il va :

1. Détecter le changement de topologie
2. Recalculer les chemins
3. Sélectionner une route alternative
4. Installer de nouveaux flux

Tester que la connectivité fonctionne toujours :

```bash
mininet> pingall
# Le trafic utilise maintenant un chemin alternatif
```

Restaurer le lien :

```bash
mininet> link s1 s2 up
```

## 7. Voir dans l'Interface ONOS

Ouvrir le navigateur : http://localhost:8181/onos/ui

Connexion : `onos` / `rocks`

Cliquer sur "Topology" pour voir :

- Commutateurs et hôtes
- Liens entre eux
- Flux actifs

## Comment RAVEN Prend ses Décisions

RAVEN note chaque chemin en utilisant :

```
Score = 0.6 × Fiabilité + 0.4 × BandePassante - 0.1 × NombreSauts
```

**Exemple :**

Chemin A : 5 sauts, 100 Mbps, 95% fiable

```
Score = 0.6 × 0.95 + 0.4 × 1.0 - 0.1 × 5 = 0.57 + 0.40 - 0.50 = 0.47
```

Chemin B : 5 sauts, 50 Mbps, 80% fiable

```
Score = 0.6 × 0.80 + 0.4 × 0.5 - 0.1 × 5 = 0.48 + 0.20 - 0.50 = 0.18
```

**RAVEN sélectionne le Chemin A** (score plus élevé)

## Personnaliser RAVEN

Éditez `raven-controller/raven_controller.py` :

### Changer les Poids

```python
# Ligne ~120
def compute_raven_score(self, path, alpha=0.6, beta=0.4):
    # alpha = poids fiabilité (augmenter pour prioriser la fiabilité)
    # beta = poids bande passante (augmenter pour prioriser la bande passante)
```

### Ajuster l'Intervalle de Surveillance

```python
# Ligne ~200
time.sleep(10)  # Changer pour mettre à jour plus/moins fréquemment
```

Après les modifications :

```bash
docker-compose restart raven-controller
```

## Dépannage

### ONOS ne répond pas

```bash
# Vérifier les logs
docker logs onos

# Attendre plus longtemps (peut prendre 60-90 secondes)
```

### RAVEN ne trouve pas de chemins

```bash
# S'assurer que la topologie fonctionne dans Mininet
docker exec -it mininet bash
service openvswitch-switch status

# Vérifier qu'ONOS a découvert les périphériques
curl -u onos:rocks http://localhost:8181/onos/v1/devices
```

### Les commutateurs ne se connectent pas

```bash
# Dans le conteneur Mininet
ovs-vsctl show
ovs-vsctl set-controller s1 tcp:onos:6653
```

## Et Ensuite ?

1. **Créer des topologies personnalisées** - Éditez les fichiers dans `topologies/`
2. **Modifier l'algorithme RAVEN** - Changez la notation dans `raven_controller.py`
3. **Ajouter des métriques** - Suivez la latence, la gigue, la perte de paquets
4. **Comparer avec le routage par défaut** - Désactivez RAVEN et testez
5. **Augmenter l'échelle** - Testez avec des réseaux plus grands

## Structure des Fichiers

```
.
├── docker-compose.yml          # Orchestre tous les conteneurs
├── mininet/
│   └── Dockerfile              # Configuration conteneur Mininet
├── raven-controller/
│   ├── Dockerfile              # Configuration conteneur RAVEN
│   ├── raven_controller.py     # Algorithme RAVEN (ÉDITEZ CECI)
│   └── requirements.txt        # Dépendances Python
├── topologies/
│   ├── simple_topology.py      # Topologie de test basique
│   ├── tree_topology.py        # Topologie hiérarchique
│   ├── raven_test_topology.py  # Topologie test multi-chemins
│   └── custom_topology.py      # Vos topologies personnalisées
└── docs/
    ├── raven-explained.md      # Explication détaillée
    └── custom-routing.md       # Sujets avancés
```

## Référence des Commandes Clés

```bash
# Démarrer l'environnement
docker-compose up -d

# Arrêter l'environnement
docker-compose down

# Voir les logs
docker logs -f raven-controller
docker logs -f onos

# Entrer dans les conteneurs
docker exec -it mininet bash
docker exec -it onos bash

# Redémarrer RAVEN après modifications
docker-compose restart raven-controller

# Reconstruire après modifications Dockerfile
docker-compose up -d --build
```

## Comprendre la Sortie

Quand RAVEN s'exécute, vous verrez :

```
INFO - Starting RAVEN controller monitoring...
```

RAVEN démarre

```
INFO - Graph built: 10 nodes, 14 edges
```

Topologie découverte (10 périphériques, 14 connexions)

```
INFO - Found 4 hosts
```

Périphériques finaux détectés

```
INFO - Path h1 -> s1 -> s2 -> s3 -> s4 -> h2: Score = 0.840
```

Chemin évalué avec score RAVEN

```
INFO - Selected path: h1 -> s1 -> s2 -> s3 -> s4 -> h2 (Score: 0.840)
```

Meilleur chemin choisi

## Indicateurs de Succès

✅ Les trois conteneurs fonctionnent
✅ Interface ONOS accessible sur localhost:8181
✅ Les logs RAVEN montrent "Graph built"
✅ Le CLI Mininet répond aux commandes
✅ `pingall` réussit dans Mininet

## Besoin d'Aide ?

Consultez les guides détaillés :

- `docs/raven-explained.md` - Comment RAVEN fonctionne
- `docs/custom-routing.md` - Personnalisation avancée
- `README.md` - Informations générales de configuration

Ou vérifiez les logs :

```bash
docker-compose logs
```
