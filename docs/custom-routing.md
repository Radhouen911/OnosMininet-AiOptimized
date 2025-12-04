# Implémenter un Calcul de Chemin Personnalisé dans ONOS

Ce guide explique comment modifier les algorithmes de routage ONOS, y compris l'implémentation d'alternatives comme RAVEN ou des algorithmes de chemin le plus court personnalisés.

## Vue d'Ensemble

ONOS offre plusieurs façons de personnaliser le calcul de chemin :

1. **Modifier les applications de routage existantes** (fwd, reactive-routing)
2. **Créer des applications ONOS personnalisées**
3. **Utiliser le Framework Intent avec sélection de chemin personnalisée**
4. **Implémenter un PathService personnalisé**

## Option 1 : Créer une Application ONOS Personnalisée

### Étape 1 : Configurer l'Environnement de Développement ONOS

```bash
# Cloner la source ONOS
git clone https://github.com/opennetworkinglab/onos.git
cd onos

# Installer les dépendances (Java 11, Maven, etc.)
# Suivre : https://wiki.onosproject.org/display/ONOS/Developer+Quick+Start
```

### Étape 2 : Créer une Application Personnalisée

```bash
# Utiliser l'archétype ONOS pour créer l'application
onos-create-app app org.example.routing custom-routing 1.0-SNAPSHOT org.example.routing

cd custom-routing
```

### Étape 3 : Implémenter le Calcul de Chemin Personnalisé

Créer `src/main/java/org/example/routing/CustomPathService.java` :

```java
package org.example.routing;

import org.onosproject.net.DeviceId;
import org.onosproject.net.Path;
import org.onosproject.net.topology.PathService;
import org.onosproject.net.topology.TopologyService;
import org.osgi.service.component.annotations.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Set;

@Component(immediate = true, service = CustomPathService.class)
public class CustomPathService {

    private final Logger log = LoggerFactory.getLogger(getClass());

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected TopologyService topologyService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected PathService pathService;

    @Activate
    protected void activate() {
        log.info("Service de Chemin Personnalisé Démarré");
    }

    @Deactivate
    protected void deactivate() {
        log.info("Service de Chemin Personnalisé Arrêté");
    }

    /**
     * Calculer le chemin en utilisant un algorithme personnalisé (ex : type RAVEN)
     * RAVEN : Reliability-Aware Virtual Network Embedding
     */
    public Path computeReliablePath(DeviceId src, DeviceId dst) {
        // Obtenir tous les chemins possibles
        Set<Path> paths = pathService.getPaths(src, dst);

        if (paths.isEmpty()) {
            return null;
        }

        // Logique personnalisée : Sélectionner le chemin basé sur les métriques de fiabilité
        // Ceci est un exemple simplifié - implémentez votre algorithme spécifique
        Path bestPath = null;
        double bestScore = Double.MIN_VALUE;

        for (Path path : paths) {
            double score = computePathScore(path);
            if (score > bestScore) {
                bestScore = score;
                bestPath = path;
            }
        }

        return bestPath;
    }

    /**
     * Calculer le score du chemin basé sur des métriques personnalisées
     * Modifier ceci pour implémenter RAVEN ou d'autres algorithmes
     */
    private double computePathScore(Path path) {
        // Exemples de métriques à considérer :
        // - Fiabilité du lien
        // - Bande passante disponible
        // - Latence
        // - Nombre de sauts
        // - Taux de pannes historiques

        double score = 0.0;

        // Préférer les chemins plus courts (moins de sauts)
        score -= path.links().size() * 0.5;

        // Ajoutez votre logique de notation personnalisée ici
        // Pour RAVEN : considérer la fiabilité du lien, la bande passante, etc.

        return score;
    }
}
```

### Étape 4 : Compiler et Déployer

```bash
# Compiler l'application
mvn clean install

# Copier vers le conteneur ONOS
docker cp target/custom-routing-1.0-SNAPSHOT.oar onos:/root/

# Installer via CLI ONOS
docker exec -it onos /root/onos/apache-karaf-4.2.14/bin/client
# Dans le CLI ONOS :
app install /root/custom-routing-1.0-SNAPSHOT.oar
app activate org.example.routing
```

## Option 2 : Modifier l'Image Docker ONOS Existante

### Étape 1 : Créer un Dockerfile Personnalisé

Créer `onos-custom/Dockerfile` :

```dockerfile
FROM onosproject/onos:2.7.0

# Copier vos applications personnalisées
COPY apps/*.oar /root/onos/apache-karaf-4.2.14/deploy/

# Ou modifier les applications existantes
# COPY modified-fwd.oar /root/onos/apache-karaf-4.2.14/system/...
```

### Étape 2 : Mettre à Jour docker-compose.yml

```yaml
services:
  onos:
    build:
      context: ./onos-custom
      dockerfile: Dockerfile
    # ... reste de la config
```

## Option 3 : Utiliser l'API REST ONOS pour la Sélection Dynamique de Chemin

Créer un script Python pour contrôler la sélection de chemin :

```python
import requests
import json

ONOS_URL = "http://localhost:8181/onos/v1"
AUTH = ("onos", "rocks")

def get_paths(src_device, dst_device):
    """Obtenir tous les chemins entre deux périphériques"""
    url = f"{ONOS_URL}/paths/{src_device}/{dst_device}"
    response = requests.get(url, auth=AUTH)
    return response.json()

def install_flow_for_path(device_id, path):
    """Installer des règles de flux pour un chemin spécifique"""
    url = f"{ONOS_URL}/flows/{device_id}"
    flow_rule = {
        "priority": 40000,
        "timeout": 0,
        "isPermanent": True,
        "treatment": {
            "instructions": [
                {"type": "OUTPUT", "port": path["port"]}
            ]
        },
        "selector": {
            "criteria": [
                {"type": "ETH_DST", "mac": path["dst_mac"]}
            ]
        }
    }
    response = requests.post(url, json=flow_rule, auth=AUTH)
    return response.status_code == 201

def select_best_path_raven(paths):
    """Sélectionner le meilleur chemin en utilisant un algorithme type RAVEN"""
    # Implémentez votre logique de sélection de chemin personnalisée
    # Considérer : fiabilité, bande passante, latence, etc.
    best_path = None
    best_score = float('-inf')

    for path in paths:
        score = compute_raven_score(path)
        if score > best_score:
            best_score = score
            best_path = path

    return best_path

def compute_raven_score(path):
    """Calculer le score RAVEN pour un chemin"""
    # Exemple de notation basé sur :
    # - Nombre de sauts (moins c'est mieux)
    # - Capacité du lien
    # - Fiabilité historique

    hop_penalty = len(path.get('links', [])) * -1
    # Ajoutez plus de métriques ici

    return hop_penalty
```

## Notes d'Implémentation de l'Algorithme RAVEN

RAVEN (Reliability-Aware Virtual Network Embedding) se concentre sur :

1. **Fiabilité du Lien** : Taux de pannes historiques
2. **Disponibilité de la Bande Passante** : Capacité actuelle et projetée
3. **Diversité des Chemins** : Plusieurs chemins disjoints pour la redondance
4. **Exigences QoS** : Latence, gigue, perte de paquets

### Métriques Clés à Suivre

```java
// Dans votre application ONOS personnalisée
public class LinkReliabilityMetrics {
    private Map<LinkKey, Double> reliabilityScores;
    private Map<LinkKey, Long> failureHistory;
    private Map<LinkKey, Double> availableBandwidth;

    public double computeLinkReliability(Link link) {
        // Suivre les événements de montée/descente du lien
        // Calculer : uptime / (uptime + downtime)
        return reliabilityScore;
    }

    public double computePathReliability(Path path) {
        // Produit de toutes les fiabilités de liens dans le chemin
        double reliability = 1.0;
        for (Link link : path.links()) {
            reliability *= computeLinkReliability(link);
        }
        return reliability;
    }
}
```

## Tester Votre Routage Personnalisé

### 1. Créer une Topologie de Test

```python
# Dans topologies/test_routing.py
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI

net = Mininet(controller=RemoteController)
c0 = net.addController('c0', ip='onos', port=6653)

# Créer une topologie avec plusieurs chemins
s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')
s3 = net.addSwitch('s3')
s4 = net.addSwitch('s4')

h1 = net.addHost('h1')
h2 = net.addHost('h2')

net.addLink(h1, s1)
net.addLink(s1, s2)
net.addLink(s1, s3)
net.addLink(s2, s4)
net.addLink(s3, s4)
net.addLink(s4, h2)

net.start()
CLI(net)
net.stop()
```

### 2. Surveiller la Sélection de Chemin

```bash
# Dans le CLI ONOS
flows
paths
intents
```

### 3. Simuler des Pannes de Liens

```bash
# Dans le CLI Mininet
mininet> link s1 s2 down
mininet> pingall
mininet> link s1 s2 up
```

## Ressources

- [Guide Développeur ONOS](https://wiki.onosproject.org/display/ONOS/Developer+Quick+Start)
- [Framework Intent ONOS](https://wiki.onosproject.org/display/ONOS/Intent+Framework)
- [Article RAVEN](https://ieeexplore.ieee.org/document/6847918)
- [API REST ONOS](https://wiki.onosproject.org/display/ONOS/The+ONOS+REST+API)

## Prochaines Étapes

1. Implémenter votre algorithme de calcul de chemin personnalisé
2. Tester avec diverses topologies
3. Comparer les performances avec le routage ONOS par défaut
4. Mesurer les métriques : latence, débit, fiabilité
5. Itérer et optimiser
