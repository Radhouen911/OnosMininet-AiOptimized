# RAVEN dans Docker Compose - Explication Complète

## Qu'est-ce que RAVEN ?

**RAVEN** (Reliability-Aware Virtual Network Embedding) est un algorithme de sélection de chemins qui choisit les chemins réseau basés sur plusieurs critères :

1. **Fiabilité des Liens** - Ratios historiques de disponibilité/indisponibilité
2. **Bande Passante Disponible** - Capacité actuelle sur les liens
3. **Longueur du Chemin** - Nombre de sauts (plus court est meilleur)
4. **Exigences QoS** - Latence, gigue, perte de paquets

Le routage traditionnel (comme OSPF, Dijkstra) ne considère que le nombre de sauts ou le coût des liens. RAVEN considère la fiabilité et la bande passante pour prendre des décisions plus intelligentes.

## Comment Ça Fonctionne dans Cette Configuration

### Vue d'Ensemble de l'Architecture

```
┌─────────────────┐
│   Mininet       │  Crée la topologie réseau
│   Conteneur     │  Exécute commutateurs & hôtes
└────────┬────────┘
         │ OpenFlow
         ↓
┌─────────────────┐
│   ONOS          │  Contrôleur SDN
│   Conteneur     │  Gère les commutateurs
└────────┬────────┘
         │ API REST
         ↓
┌─────────────────┐
│   RAVEN         │  Logique de Sélection de Chemins
│   Contrôleur    │  Surveille & décide des chemins
└─────────────────┘
```

### Le Flux :

1. **Mininet** crée des commutateurs et hôtes virtuels
2. **ONOS** découvre la topologie via OpenFlow
3. **Contrôleur RAVEN** interroge ONOS pour les données de topologie
4. **RAVEN** calcule les meilleurs chemins avec son algorithme
5. **RAVEN** indique à ONOS quels chemins utiliser (via API REST)
6. **ONOS** installe les règles de flux sur les commutateurs
7. **Le trafic** circule via les chemins sélectionnés

## Comment RAVEN S'Exécute dans Docker

### Conteneur : `raven-controller`

Ce conteneur Python s'exécute en continu et :

1. **Se connecte à ONOS** via API REST (http://onos:8181)
2. **Récupère la topologie** toutes les 10 secondes
3. **Construit un graphe** en utilisant NetworkX
4. **Suit les métriques** pour chaque lien :
   - Score de fiabilité (0.0 à 1.0)
   - Bande passante disponible (Mbps)
   - Compteur de pannes
5. **Calcule les chemins** entre toutes les paires d'hôtes
6. **Note chaque chemin** en utilisant la formule RAVEN :
   ```
   Score = α × Fiabilité + β × (BandePassante/Max) - γ × NombreSauts
   ```
7. **Sélectionne le meilleur chemin** (score le plus élevé)
8. **Installe les flux** dans ONOS pour le chemin choisi

### Composants Clés du Code

#### 1. Récupération de Topologie

```python
def get_topology(self):
    # Interroge l'API REST ONOS pour :
    # - /onos/v1/devices (commutateurs)
    # - /onos/v1/links (connexions)
    # - /onos/v1/hosts (périphériques finaux)
```

#### 2. Calcul de Fiabilité du Chemin

```python
def compute_path_reliability(self, path):
    # Multiplie la fiabilité de tous les liens dans le chemin
    # R(chemin) = R(lien1) × R(lien2) × ... × R(lienN)
    # Fiabilité plus basse = chemin évité
```

#### 3. Notation RAVEN

```python
def compute_raven_score(self, path, alpha=0.6, beta=0.4):
    # alpha (0.6) = poids pour la fiabilité
    # beta (0.4) = poids pour la bande passante
    # Pénalise les chemins plus longs
    # Retourne le score pour comparaison
```

#### 4. Sélection de Chemin

```python
def find_best_path_raven(self, src, dst, k=3):
    # Trouve k chemins les plus courts (en utilisant NetworkX)
    # Note chacun avec l'algorithme RAVEN
    # Retourne le chemin avec le score le plus élevé
```

## Exécuter RAVEN

### Étape 1 : Tout Démarrer

```bash
docker-compose up -d
```

Cela démarre :

- ONOS (prend ~60 secondes pour s'initialiser)
- Mininet (prêt immédiatement)
- Contrôleur RAVEN (attend 30s pour ONOS, puis commence la surveillance)

### Étape 2 : Créer une Topologie

```bash
# Entrer dans le conteneur Mininet
docker exec -it mininet bash

# Démarrer OVS
service openvswitch-switch start

# Exécuter une topologie avec plusieurs chemins
python3 /topologies/simple_topology.py
```

### Étape 3 : Voir RAVEN Fonctionner

```bash
# Voir les logs du contrôleur RAVEN
docker logs -f raven-controller
```

Vous verrez une sortie comme :

```
INFO - Graph built: 8 nodes, 12 edges
INFO - Found 4 hosts
INFO - Path h1 -> h2: Reliability=0.900, BW=100.0, Hops=3, Score=0.840
INFO - Path h1 -> h2: Reliability=0.950, BW=80.0, Hops=4, Score=0.810
INFO - Selected path: h1 -> s1 -> s2 -> h2 (Score: 0.840)
```

### Étape 4 : Tester la Sélection de Chemin

Dans le CLI Mininet :

```bash
mininet> pingall  # Tester la connectivité

# Simuler une panne de lien
mininet> link s1 s2 down

# RAVEN détectera le changement de topologie et recalculera les chemins
# Vérifier les logs : docker logs -f raven-controller

mininet> pingall  # Le trafic utilise un chemin alternatif

mininet> link s1 s2 up  # Restaurer le lien
```

## Personnaliser RAVEN

### Ajuster les Poids

Éditez `raven-controller/raven_controller.py` :

```python
# Ligne ~120
def compute_raven_score(self, path, alpha=0.6, beta=0.4):
    # Augmenter alpha pour prioriser la fiabilité
    # Augmenter beta pour prioriser la bande passante
```

Exemples :

- `alpha=0.8, beta=0.2` - Préférer les chemins fiables
- `alpha=0.3, beta=0.7` - Préférer les chemins haute bande passante
- `alpha=0.5, beta=0.5` - Équilibré

### Ajouter des Métriques Personnalisées

```python
def compute_raven_score(self, path, alpha=0.5, beta=0.3, gamma=0.2):
    reliability = self.compute_path_reliability(path)
    bandwidth = self.compute_path_bandwidth(path)
    latency = self.compute_path_latency(path)  # Ajoutez ceci

    score = (alpha * reliability) +
            (beta * normalized_bandwidth) -
            (gamma * latency)
    return score
```

### Suivre les Pannes de Liens Réelles

```python
def update_link_failure(self, link_key):
    """Appelé quand un lien tombe"""
    self.link_failures[link_key] += 1
    # La fiabilité diminue automatiquement
```

## Surveillance & Débogage

### Voir la Topologie ONOS

```bash
# Ouvrir le navigateur
http://localhost:8181/onos/ui

# Connexion : onos / rocks
# Cliquer sur la vue "Topology"
```

### Vérifier l'État RAVEN

```bash
# Voir les logs
docker logs raven-controller

# Suivre les logs en temps réel
docker logs -f raven-controller

# Redémarrer RAVEN
docker-compose restart raven-controller
```

### Interroger ONOS Directement

```bash
# Obtenir les périphériques
curl -u onos:rocks http://localhost:8181/onos/v1/devices

# Obtenir les liens
curl -u onos:rocks http://localhost:8181/onos/v1/links

# Obtenir les flux
curl -u onos:rocks http://localhost:8181/onos/v1/flows
```

### CLI ONOS

```bash
docker exec -it onos /root/onos/apache-karaf-4.2.14/bin/client

# À l'intérieur du CLI ONOS :
onos> devices
onos> links
onos> flows
onos> paths
```

## Avantages de Cette Approche

✅ **Pas de recompilation ONOS** - RAVEN s'exécute en externe
✅ **Facile à modifier** - Éditez le code Python, redémarrez le conteneur
✅ **Flexibilité du langage** - Utilisez Python au lieu de Java
✅ **Itération rapide** - Testez les changements en secondes
✅ **Portable** - Fonctionne sur n'importe quel hôte Docker

## Limitations

⚠️ **Latence** - Les appels API REST ajoutent une surcharge
⚠️ **Évolutivité** - Pas adapté aux très grands réseaux
⚠️ **Installation de flux** - Simplifiée (nécessite une logique de mappage de ports)
⚠️ **Métriques** - Simulées (nécessite une intégration de surveillance réelle)

## Prochaines Étapes

1. **Tester avec des topologies complexes** - Créer des réseaux maillés
2. **Simuler des pannes** - Tester la réponse de RAVEN
3. **Ajouter des métriques réelles** - Intégrer avec des outils de surveillance
4. **Comparer les performances** - Comparer avec le routage ONOS par défaut
5. **Implémenter l'installation complète de flux** - Interroger les numéros de ports réels
6. **Ajouter une API REST** - Contrôler RAVEN via des points de terminaison HTTP

## Alternative : Application ONOS Native

Pour la production, considérez la construction d'une application ONOS native :

- Latence plus faible (pas de surcharge API REST)
- Meilleure intégration avec les services ONOS
- Plus évolutif
- Nécessite le développement Java et la reconstruction ONOS

Voir `docs/custom-routing.md` pour les détails sur la construction d'applications ONOS natives.
