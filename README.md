# ONOS + Mininet + RAVEN dans Docker

Bienvenue ! Ce projet vous permet de jouer avec des réseaux SDN (Software-Defined Networking) directement sur votre machine. On a mis ensemble ONOS (le contrôleur SDN), Mininet (pour créer des réseaux virtuels) et RAVEN (un algorithme malin pour choisir les meilleurs chemins réseau).

En gros, vous allez pouvoir créer des topologies réseau complexes, les tester, et voir comment RAVEN choisit intelligemment les routes en fonction de la fiabilité et de la bande passante - pas juste le nombre de sauts comme le font les algos classiques.

## 🚀 Envie de commencer direct ?

Si vous êtes du genre impatient (on vous comprend), jetez un œil à [QUICKSTART-RAVEN.md](QUICKSTART-RAVEN.md) pour être opérationnel en 5 minutes.

Si vous préférez comprendre ce qui se passe sous le capot avant de vous lancer, allez voir [RAVEN-SUMMARY.md](RAVEN-SUMMARY.md).

## Ce dont vous avez besoin

Juste deux trucs :

- Docker (pour faire tourner les conteneurs)
- Docker Compose (pour orchestrer le tout)

## Lancer le tout

### Étape 1 : Démarrer les conteneurs

Une seule commande suffit :

```bash
docker-compose up -d
```

Ça va lancer trois conteneurs qui vont bosser ensemble :

- **ONOS** - Le cerveau qui gère vos commutateurs (interface web sur `localhost:8181`)
- **Mininet** - Votre labo réseau virtuel avec tous vos scripts Python
- **RAVEN** - L'algorithme qui choisit les meilleurs chemins

Attendez environ une minute qu'ONOS finisse de démarrer (il est un peu lent au réveil).

### Étape 2 : Jeter un œil à l'interface ONOS

Ouvrez votre navigateur et allez sur :

```
http://localhost:8181/onos/ui
```

Connectez-vous avec :

- Login : `onos`
- Mot de passe : `rocks`

Vous verrez une interface graphique où vous pourrez visualiser votre topologie réseau en temps réel.

### Étape 3 : Créer votre premier réseau

Entrez dans le conteneur Mininet :

```bash
docker exec -it mininet bash
```

Une fois dedans, lancez Open vSwitch et créez une topologie :

```bash
# Démarrer OVS
service openvswitch-switch start

# Lancer une topologie simple (4 commutateurs en anneau)
python3 /topologies/simple_topology.py

# Ou si vous préférez une topologie en arbre
python3 /topologies/tree_topology.py
```

## Les topologies qu'on vous a préparées

On a mis quelques topologies prêtes à l'emploi pour que vous puissiez tester rapidement :

**Topologie Simple** (`simple_topology.py`)

- 4 commutateurs connectés en anneau
- 4 hôtes (un par commutateur)
- Parfait pour vos premiers tests et comprendre comment ça marche

**Topologie en Arbre** (`tree_topology.py`)

- Une structure hiérarchique comme un vrai réseau d'entreprise
- Vous pouvez ajuster la profondeur et le nombre de branches
- Idéal pour tester comment RAVEN se débrouille avec plusieurs chemins possibles

**Topologie Personnalisée** (`custom_topology.py`)

- Un template vide pour créer ce que vous voulez
- Modifiez-le selon vos besoins et vos expériences

## Créer vos propres topologies

C'est super simple de créer votre propre réseau :

1. Créez un nouveau fichier Python dans le dossier `topologies/`
2. Utilisez l'API Mininet pour dessiner votre réseau (ajoutez des commutateurs, des hôtes, des liens)
3. Connectez tout ça à ONOS avec `ip='onos', port=6653`
4. Lancez votre script depuis le conteneur Mininet

Voici un exemple minimal pour vous lancer :

```python
from mininet.net import Mininet
from mininet.node import RemoteController

net = Mininet(controller=RemoteController)
net.addController('c0', controller=RemoteController, ip='onos', port=6653)

# Ajoutez vos commutateurs, hôtes et liens ici
# Par exemple : s1 = net.addSwitch('s1')
#              h1 = net.addHost('h1')
#              net.addLink(h1, s1)

net.start()
```

Après, laissez libre cours à votre imagination !

## Utiliser la ligne de commande ONOS

Si vous aimez la ligne de commande (et qui ne l'aime pas ?), vous pouvez accéder au CLI ONOS de deux façons :

**Directement depuis Docker :**

```bash
docker exec -it onos /root/onos/apache-karaf-4.2.14/bin/client
```

**Ou via SSH :**

```bash
ssh -p 8101 onos@localhost
# Mot de passe : rocks
```

Une fois dedans, voici quelques commandes pratiques :

```bash
apps -s              # Voir les applications installées
devices              # Lister vos commutateurs
links                # Voir les connexions entre commutateurs
hosts                # Afficher les hôtes connectés
flows                # Voir les règles de flux installées
```

Vous pouvez aussi activer des applications :

```bash
app activate org.onosproject.fwd    # Active le forwarding basique
```

## Personnaliser les algorithmes de routage

Vous voulez changer la façon dont RAVEN (ou ONOS) choisit les chemins ? Vous avez plusieurs options :

### Option 1 : Modifier le contrôleur RAVEN (le plus simple)

Le code de RAVEN est dans `raven-controller/raven_controller.py`. Vous pouvez :

- Changer les poids de l'algorithme (fiabilité vs bande passante)
- Ajouter de nouvelles métriques (latence, gigue, etc.)
- Implémenter un tout nouvel algorithme

Après vos modifs, redémarrez juste le conteneur :

```bash
docker-compose restart raven-controller
```

### Option 2 : Créer votre propre app ONOS

Si vous voulez aller plus loin et créer une vraie application ONOS :

1. Développez votre app en Java avec votre logique de routage
2. Compilez-la en fichier `.oar`
3. Copiez-la dans le conteneur : `docker cp votre-app.oar onos:/root/`
4. Installez-la via le CLI ONOS

### Option 3 : Utiliser les Intents ONOS

ONOS a un système d'Intents qui permet de définir des politiques de haut niveau sans coder :

```bash
# Dans le CLI ONOS
add-host-intent <mac-hote1> <mac-hote2>
add-point-intent <device1>/<port1> <device2>/<port2>
```

C'est pratique pour des tests rapides ou des démos.

## Comment tout ça communique

Les trois conteneurs sont sur le même réseau Docker (`onos-mininet-net`), ce qui leur permet de se parler facilement :

- Mininet se connecte à ONOS via OpenFlow
- RAVEN interroge ONOS via son API REST
- ONOS gère les commutateurs et installe les règles de flux

## Les ports à connaître

- `8181` - Interface web ONOS et API REST (c'est là que vous allez le plus souvent)
- `8101` - SSH/CLI ONOS (pour les commandes en ligne)
- `6653` - Port OpenFlow (communication ONOS ↔ commutateurs)
- `6640` - Port OVSDB (gestion des switches)

## Quand ça ne marche pas comme prévu

**ONOS ne voit pas les commutateurs ?**

Vérifiez d'abord qu'ONOS a bien fini de démarrer (ça peut prendre 1-2 minutes) :

```bash
docker logs onos
```

Testez aussi la connectivité réseau :

```bash
docker exec -it mininet ping onos
```

**OVS refuse de démarrer ?**

Entrez dans le conteneur Mininet et relancez-le manuellement :

```bash
docker exec -it mininet bash
service openvswitch-switch start
ovs-vsctl show    # Pour voir l'état
```

**Besoin de voir ce qui se passe ?**

Les logs sont vos amis :

```bash
docker-compose logs -f              # Tous les logs
docker logs -f raven-controller     # Juste RAVEN
docker logs -f onos                 # Juste ONOS
```

## Tout arrêter proprement

Quand vous avez fini de jouer :

```bash
docker-compose down
```

Si vous voulez aussi supprimer les données persistantes :

```bash
docker-compose down -v
```

## Et maintenant ?

Maintenant que tout tourne, voici quelques idées pour aller plus loin :

1. **Testez différentes topologies** - Créez des réseaux complexes et voyez comment RAVEN s'en sort
2. **Simulez des pannes** - Coupez des liens avec `link s1 s2 down` dans Mininet et regardez RAVEN recalculer les chemins
3. **Modifiez l'algorithme RAVEN** - Changez les poids, ajoutez de nouvelles métriques
4. **Comparez avec le routage classique** - Désactivez RAVEN et comparez les performances
5. **Créez votre propre algorithme** - Implémentez Dijkstra, ECMP, ou inventez le vôtre !

Amusez-vous bien ! 🚀
