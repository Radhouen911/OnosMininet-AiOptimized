# RAVEN dans Docker Compose - Résumé Complet

## Oui, Vous Pouvez Exécuter RAVEN avec Docker Compose ! ✅

Voici exactement comment ça fonctionne :

## La Configuration

### Trois Conteneurs Travaillant Ensemble :

1. **Conteneur ONOS** (Contrôleur SDN)

   - Gère les commutateurs OpenFlow
   - Fournit une API REST pour les infos de topologie
   - Installe les règles de flux sur les commutateurs

2. **Conteneur Mininet** (Émulateur Réseau)

   - Crée des commutateurs et hôtes virtuels
   - Exécute vos scripts de topologie Python
   - Se connecte à ONOS via OpenFlow

3. **Conteneur Contrôleur RAVEN** (Sélection de Chemins)
   - Interroge ONOS pour les données de topologie
   - Calcule les meilleurs chemins avec l'algorithme RAVEN
   - Indique à ONOS quels chemins utiliser

## Comment RAVEN Fonctionne

### L'Algorithme :

```python
Score = α × Fiabilité + β × BandePassante - γ × NombreSauts

Où :
- α (alpha) = 0.6 = poids fiabilité
- β (beta) = 0.4 = poids bande passante
- γ (gamma) = 0.1 = pénalité sauts
```

### Exemple de Décision :

**Scénario :** Deux chemins de l'Hôte A à l'Hôte B

**Chemin 1 :**

- 3 sauts
- 100 Mbps bande passante
- 95% fiabilité
- Score = 0.6×0.95 + 0.4×1.0 - 0.1×3 = 0.97

**Chemin 2 :**

- 2 sauts (plus court !)
- 50 Mbps bande passante
- 70% fiabilité
- Score = 0.6×0.70 + 0.4×0.5 - 0.1×2 = 0.42

**RAVEN choisit le Chemin 1** même s'il est plus long, car il est plus fiable et a une meilleure bande passante.

Le routage traditionnel choisirait le Chemin 2 (moins de sauts).

## Ce Qui Rend Cette Implémentation Spéciale

### ✅ Avantages :

1. **Pas de Recompilation ONOS** - RAVEN fonctionne comme service séparé
2. **Facile à Modifier** - Éditez le code Python, redémarrez le conteneur
3. **Tests Rapides** - Les changements prennent des secondes, pas des minutes
4. **Flexibilité du Langage** - Python au lieu de Java
5. **Portable** - Fonctionne partout où Docker fonctionne

### ⚠️ Compromis :

1. **Surcharge API REST** - Légère latence vs application ONOS native
2. **Installation de Flux Simplifiée** - La production nécessite plus de logique
3. **Métriques Simulées** - Le déploiement réel nécessite une intégration de surveillance

## Structure des Fichiers Que Vous Avez

```
votre-projet/
├── docker-compose.yml              # Orchestre tout
│
├── mininet/
│   └── Dockerfile                  # Configuration Mininet
│
├── raven-controller/
│   ├── Dockerfile                  # Conteneur RAVEN
│   ├── raven_controller.py         # ⭐ Algorithme RAVEN (ÉDITEZ CECI)
│   └── requirements.txt            # Dépendances Python
│
├── topologies/
│   ├── simple_topology.py          # Test basique
│   ├── tree_topology.py            # Hiérarchique
│   ├── raven_test_topology.py      # Test multi-chemins
│   └── custom_topology.py          # Vos topologies personnalisées
│
├── scripts/
│   ├── setup.sh                    # Configuration rapide
│   ├── test-raven.sh               # Script de test
│   └── compare-routing.py          # Comparer RAVEN vs défaut
│
└── docs/
    ├── raven-explained.md          # Explication détaillée
    └── custom-routing.md           # Sujets avancés
```

## 🚀 Comment Ça Fonctionne :

1. Mininet crée la topologie réseau virtuelle
2. ONOS découvre les commutateurs via OpenFlow
3. RAVEN interroge ONOS pour la topologie (API REST)
4. RAVEN calcule les meilleurs chemins en utilisant : `Score = 0.6×Fiabilité + 0.4×BandePassante - 0.1×Sauts`
5. RAVEN indique à ONOS quels chemins utiliser
6. Le trafic circule via les chemins sélectionnés par RAVEN

## 🔧 Changer les Méthodes de Reconnaissance de Chemins :

Vous pouvez facilement basculer entre les algorithmes en éditant `raven_controller.py` :

- **RAVEN** (par défaut) - Notation multi-métriques
- **Chemin le Plus Court** - Minimum de sauts
- **Chemin le Plus Large** - Bande passante maximale
- **Latence Minimale** - Délai le plus bas
- **Fiabilité Maximale** - Le plus stable
- **Équilibrage de Charge** - Distribuer le trafic
- **Votre algorithme personnalisé** - Implémentez ce que vous voulez !

Commencez simplement avec `docker-compose up -d` et suivez le guide QUICKSTART !

## Commandes de Démarrage Rapide

```bash
# 1. Tout démarrer
docker-compose up -d

# 2. Attendre ONOS (60 secondes)
sleep 60

# 3. Créer une topologie réseau
docker exec -it mininet bash
service openvswitch-switch start
python3 /topologies/raven_test_topology.py

# 4. Voir RAVEN fonctionner (nouveau terminal)
docker logs -f raven-controller

# 5. Voir dans le navigateur
# http://localhost:8181/onos/ui (onos/rocks)
```

## Tester l'Intelligence de RAVEN

### Test 1 : Connectivité de Base

```bash
mininet> pingall
# Tous les hôtes devraient communiquer
```

### Test 2 : Panne de Lien

```bash
mininet> link s1 s2 down
# RAVEN détecte le changement et recalcule les chemins
mininet> pingall
# Fonctionne toujours via un chemin alternatif !
```

### Test 3 : Test de Bande Passante

```bash
mininet> iperf h1 h2
# Mesurer le débit sur le chemin sélectionné par RAVEN
```

## Personnaliser RAVEN

### Changer les Poids de l'Algorithme

Éditez `raven-controller/raven_controller.py` ligne ~120 :

```python
def compute_raven_score(self, path, alpha=0.6, beta=0.4):
    # Augmenter alpha pour prioriser la fiabilité
    # Augmenter beta pour prioriser la bande passante
```

Exemples :

- `alpha=0.8, beta=0.2` → Préférer les chemins fiables
- `alpha=0.3, beta=0.7` → Préférer les chemins haute bande passante
- `alpha=0.5, beta=0.5` → Approche équilibrée

Puis redémarrer :

```bash
docker-compose restart raven-controller
```

### Ajouter des Métriques Personnalisées

Vous pouvez étendre RAVEN pour considérer :

- **Latence** - Préférer les chemins à faible latence
- **Gigue** - Important pour les applications temps réel
- **Perte de Paquets** - Critique pour la fiabilité
- **Consommation Énergétique** - Pour les réseaux verts
- **Coût** - Pour les réseaux multi-fournisseurs

Exemple :

```python
def compute_raven_score(self, path, alpha=0.4, beta=0.3, gamma=0.3):
    reliability = self.compute_path_reliability(path)
    bandwidth = self.compute_path_bandwidth(path)
    latency = self.compute_path_latency(path)  # Ajoutez ceci

    score = (alpha * reliability) +
            (beta * bandwidth) -
            (gamma * latency)
    return score
```

## Surveillance & Débogage

### Voir les Décisions RAVEN

```bash
docker logs -f raven-controller
```

### Vérifier la Topologie ONOS

```bash
curl -u onos:rocks http://localhost:8181/onos/v1/devices | jq
curl -u onos:rocks http://localhost:8181/onos/v1/links | jq
```

### CLI ONOS

```bash
docker exec -it onos /root/onos/apache-karaf-4.2.14/bin/client
# Mot de passe : rocks

onos> devices
onos> links
onos> flows
onos> paths
```

### Comparer avec le Routage Par Défaut

```bash
python3 scripts/compare-routing.py
```

## Prochaines Étapes : Changer les Méthodes de Reconnaissance de Chemins

Vous avez demandé comment changer les "méthodes de reconnaissance de chemins" - voici comment :

### Option 1 : Modifier l'Algorithme RAVEN (Facile)

Éditez `raven_controller.py` :

```python
def find_best_path_raven(self, src, dst, k=3):
    # Changer k pour considérer plus de chemins
    paths = list(nx.shortest_simple_paths(self.topology, src, dst))[:k]

    # Ou utiliser une recherche de chemin différente :
    # - Tous les chemins simples : nx.all_simple_paths()
    # - Chemins disjoints : nx.node_disjoint_paths()
    # - Disjoints par arête : nx.edge_disjoint_paths()
```

### Option 2 : Implémenter Différents Algorithmes

Remplacer RAVEN par :

**Dijkstra (chemin le plus court) :**

```python
path = nx.shortest_path(self.topology, src, dst, weight='weight')
```

**Chemin le Plus Large (bande passante max) :**

```python
path = nx.shortest_path(self.topology, src, dst, weight=lambda u,v,d: -d['bandwidth'])
```

**K-Chemins les Plus Courts :**

```python
paths = list(nx.shortest_simple_paths(self.topology, src, dst))[:k]
```

**Équilibrage de Charge :**

```python
# Distribuer le trafic sur plusieurs chemins
paths = self.find_k_disjoint_paths(src, dst, k=3)
for i, flow in enumerate(flows):
    path = paths[i % len(paths)]  # Round-robin
```

### Option 3 : Ajouter de Nouveaux Algorithmes

Créez de nouvelles méthodes dans `raven_controller.py` :

```python
def find_path_max_reliability(self, src, dst):
    """Sélectionner le chemin avec la plus haute fiabilité"""
    paths = nx.all_simple_paths(self.topology, src, dst)
    return max(paths, key=self.compute_path_reliability)

def find_path_min_latency(self, src, dst):
    """Sélectionner le chemin avec la latence la plus basse"""
    return nx.shortest_path(self.topology, src, dst,
                           weight=lambda u,v,d: d.get('latency', 1))

def find_path_load_balanced(self, src, dst):
    """Sélectionner le chemin le moins utilisé"""
    paths = list(nx.shortest_simple_paths(self.topology, src, dst))[:5]
    return min(paths, key=self.compute_path_utilization)
```

Puis basculez entre eux :

```python
# Dans monitor_and_update():
best_path = self.find_best_path_raven(src, dst)  # RAVEN
# OU
best_path = self.find_path_max_reliability(src, dst)  # Fiabilité max
# OU
best_path = self.find_path_min_latency(src, dst)  # Latence min
```

## Considérations pour la Production

Pour un déploiement réel, considérez :

1. **Application ONOS Native** - Meilleures performances, latence plus faible
2. **Métriques Réelles** - Intégrer avec la surveillance (Prometheus, etc.)
3. **Installation de Flux** - Interroger les numéros de ports réels depuis ONOS
4. **Évolutivité** - Optimiser pour les grands réseaux
5. **Haute Disponibilité** - Plusieurs instances de contrôleur RAVEN
6. **Sécurité** - Sécuriser la communication API REST

Voir `docs/custom-routing.md` pour construire des applications ONOS natives.

## Ressources

- **Article RAVEN :** [IEEE Xplore](https://ieeexplore.ieee.org/document/6847918)
- **Docs ONOS :** [wiki.onosproject.org](https://wiki.onosproject.org)
- **Docs Mininet :** [mininet.org](http://mininet.org)
- **Docs NetworkX :** [networkx.org](https://networkx.org)

## Support

Vérifiez les logs en cas de problèmes :

```bash
docker-compose logs
docker logs onos
docker logs mininet
docker logs raven-controller
```

Tout redémarrer :

```bash
docker-compose down
docker-compose up -d --build
```

## Résumé

✅ **Oui, RAVEN fonctionne dans Docker Compose**
✅ **Facile à modifier et tester**
✅ **Basé sur Python, pas besoin de Java**
✅ **Fonctionne avec n'importe quelle topologie Mininet**
✅ **Peut basculer entre différents algorithmes de chemins**
✅ **Prêt pour la production avec quelques améliorations**

Vous avez maintenant un banc de test SDN complet avec sélection intelligente de chemins !
