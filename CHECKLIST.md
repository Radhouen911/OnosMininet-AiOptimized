# Liste de Vérification Configuration RAVEN

Utilisez cette liste pour vérifier que votre configuration fonctionne correctement.

## ✅ Configuration Initiale

- [ ] Docker est installé et fonctionne
- [ ] Docker Compose est installé
- [ ] Les fichiers du projet sont téléchargés/clonés
- [ ] Vous êtes dans le répertoire du projet

## ✅ Démarrage de l'Environnement

```bash
docker-compose up -d
```

- [ ] La commande se termine sans erreurs
- [ ] Trois conteneurs sont créés :
  - [ ] `onos`
  - [ ] `mininet`
  - [ ] `raven-controller`

Vérifier :

```bash
docker-compose ps
# Les trois devraient afficher "Up" ou "running"
```

## ✅ Contrôleur ONOS

Attendez 60-90 secondes pour l'initialisation d'ONOS, puis vérifiez :

- [ ] Interface ONOS accessible sur http://localhost:8181/onos/ui
- [ ] Connexion possible avec `onos` / `rocks`
- [ ] L'API REST répond :
  ```bash
  curl -u onos:rocks http://localhost:8181/onos/v1/applications
  ```
- [ ] Pas d'erreurs dans les logs :
  ```bash
  docker logs onos | tail -20
  ```

## ✅ Contrôleur RAVEN

- [ ] Le conteneur fonctionne :
  ```bash
  docker ps | grep raven
  ```
- [ ] Les logs montrent "Starting RAVEN controller monitoring..." :
  ```bash
  docker logs raven-controller
  ```
- [ ] Pas d'erreurs de connexion dans les logs
- [ ] RAVEN interroge ONOS (vérifier les logs)

## ✅ Conteneur Mininet

- [ ] Le conteneur fonctionne :
  ```bash
  docker ps | grep mininet
  ```
- [ ] Peut entrer dans le conteneur :
  ```bash
  docker exec -it mininet bash
  ```
- [ ] OVS est disponible :
  ```bash
  docker exec -it mininet ovs-vsctl --version
  ```
- [ ] Les scripts Python sont montés :
  ```bash
  docker exec -it mininet ls /topologies
  ```

## ✅ Connectivité Réseau

- [ ] Les conteneurs peuvent communiquer :
  ```bash
  docker exec -it mininet ping -c 3 onos
  docker exec -it raven-controller ping -c 3 onos
  ```

## ✅ Exécution d'une Topologie

À l'intérieur du conteneur Mininet :

```bash
docker exec -it mininet bash
service openvswitch-switch start
python3 /topologies/simple_topology.py
```

- [ ] OVS démarre sans erreurs
- [ ] Le script de topologie s'exécute
- [ ] Le CLI Mininet apparaît (`mininet>`)
- [ ] ONOS découvre les commutateurs (vérifier l'interface ou les logs)
- [ ] RAVEN détecte la topologie (vérifier les logs)

## ✅ Test de Connectivité

Dans le CLI Mininet :

```bash
mininet> pingall
```

- [ ] Tous les hôtes peuvent se pinguer
- [ ] Pas de perte de paquets
- [ ] Latence raisonnable (<100ms)

## ✅ Sélection de Chemins RAVEN

Pendant que la topologie fonctionne :

```bash
docker logs -f raven-controller
```

- [ ] Les logs montrent "Graph built: X nodes, Y edges"
- [ ] Les logs montrent "Found N hosts"
- [ ] Les logs montrent les calculs de chemins avec scores
- [ ] Les logs montrent "Selected path: ..."

## ✅ Test de l'Intelligence RAVEN

Dans le CLI Mininet :

```bash
mininet> link s1 s2 down
```

Puis vérifier les logs RAVEN :

- [ ] RAVEN détecte le changement de topologie
- [ ] RAVEN recalcule les chemins
- [ ] De nouveaux chemins sont sélectionnés

Tester que la connectivité fonctionne toujours :

```bash
mininet> pingall
```

- [ ] Les hôtes communiquent toujours (via un chemin alternatif)

Restaurer le lien :

```bash
mininet> link s1 s2 up
```

- [ ] RAVEN détecte la restauration du lien
- [ ] Les chemins sont mis à jour

## ✅ Vérification Interface ONOS

Dans le navigateur sur http://localhost:8181/onos/ui :

- [ ] Peut voir la vue topologie
- [ ] Les commutateurs sont affichés
- [ ] Les liens entre commutateurs sont montrés
- [ ] Les hôtes sont visibles
- [ ] Peut cliquer sur les périphériques pour les détails

## ✅ Tests Avancés

### Test de Bande Passante

```bash
mininet> iperf h1 h2
```

- [ ] Le test de bande passante se termine
- [ ] Débit raisonnable rapporté

### Topologies Multiples

```bash
# Quitter la topologie actuelle (Ctrl+D dans le CLI Mininet)
python3 /topologies/tree_topology.py
```

- [ ] Une topologie différente se charge
- [ ] RAVEN s'adapte à la nouvelle topologie

### Topologie Personnalisée

```bash
python3 /topologies/raven_test_topology.py
```

- [ ] La topologie multi-chemins fonctionne
- [ ] RAVEN sélectionne les meilleurs chemins

## ✅ Personnalisation

### Modifier les Poids RAVEN

Éditez `raven-controller/raven_controller.py` :

- [ ] Changer les valeurs alpha/beta
- [ ] Sauvegarder le fichier
- [ ] Redémarrer RAVEN :
  ```bash
  docker-compose restart raven-controller
  ```
- [ ] Les nouveaux poids prennent effet (vérifier les logs)

### Créer une Topologie Personnalisée

Éditez `topologies/custom_topology.py` :

- [ ] Ajouter vos commutateurs et hôtes
- [ ] Ajouter des liens
- [ ] Exécuter la topologie
- [ ] RAVEN la découvre

## ✅ Surveillance & Débogage

### Vérifier Tous les Logs

```bash
docker-compose logs
```

- [ ] Pas d'erreurs critiques
- [ ] Les services communiquent

### Logs des Conteneurs Individuels

```bash
docker logs onos
docker logs mininet
docker logs raven-controller
```

- [ ] Chacun montre la sortie attendue

### Accès CLI ONOS

```bash
docker exec -it onos /root/onos/apache-karaf-4.2.14/bin/client
```

- [ ] Peut accéder au CLI ONOS
- [ ] Les commandes fonctionnent : `devices`, `links`, `flows`

### Requêtes API REST

```bash
curl -u onos:rocks http://localhost:8181/onos/v1/devices | jq
curl -u onos:rocks http://localhost:8181/onos/v1/links | jq
curl -u onos:rocks http://localhost:8181/onos/v1/hosts | jq
```

- [ ] Tous retournent du JSON valide
- [ ] Les données correspondent à la topologie

## ✅ Nettoyage

### Arrêter l'Environnement

```bash
docker-compose down
```

- [ ] Tous les conteneurs s'arrêtent
- [ ] Pas d'erreurs

### Supprimer les Volumes (Optionnel)

```bash
docker-compose down -v
```

- [ ] Les volumes sont supprimés
- [ ] Démarrage propre la prochaine fois

### Redémarrer

```bash
docker-compose up -d
```

- [ ] Tout démarre proprement
- [ ] Pas de problèmes de l'exécution précédente

## 🎯 Critères de Succès

Vous êtes prêt à utiliser RAVEN quand :

✅ Les trois conteneurs fonctionnent
✅ Interface ONOS accessible
✅ Les logs RAVEN montrent la sélection de chemins
✅ Les topologies Mininet fonctionnent
✅ `pingall` réussit
✅ Les pannes de liens déclenchent le recalcul de chemins
✅ Le trafic circule via les chemins sélectionnés par RAVEN

## 🐛 Problèmes Courants

### ONOS ne répond pas

- Attendre plus longtemps (peut prendre 90 secondes)
- Vérifier les logs : `docker logs onos`
- Redémarrer : `docker-compose restart onos`

### RAVEN ne peut pas se connecter à ONOS

- S'assurer qu'ONOS est complètement démarré
- Vérifier le réseau : `docker exec -it raven-controller ping onos`
- Vérifier l'API ONOS : `curl -u onos:rocks http://localhost:8181/onos/v1/applications`

### Les commutateurs Mininet ne se connectent pas

- Démarrer OVS : `service openvswitch-switch start`
- Vérifier le contrôleur : `ovs-vsctl show`
- Définir le contrôleur : `ovs-vsctl set-controller s1 tcp:onos:6653`

### Aucun chemin trouvé

- S'assurer que la topologie fonctionne
- Vérifier qu'ONOS a découvert les périphériques : `curl -u onos:rocks http://localhost:8181/onos/v1/devices`
- Vérifier les logs RAVEN pour les erreurs

### Port déjà utilisé

- Arrêter les services en conflit
- Ou changer les ports dans `docker-compose.yml`

## 📚 Prochaines Étapes

Une fois que tout fonctionne :

1. [ ] Lire `RAVEN-SUMMARY.md` pour une explication détaillée
2. [ ] Essayer différentes topologies
3. [ ] Modifier l'algorithme RAVEN
4. [ ] Comparer avec le routage par défaut
5. [ ] Créer votre propre algorithme de sélection de chemins
6. [ ] Tester avec des réseaux plus grands
7. [ ] Implémenter la collecte de métriques réelles
8. [ ] Construire une version prête pour la production

## 🎓 Parcours d'Apprentissage

- [ ] Comprendre la création de topologie de base
- [ ] Apprendre l'algorithme RAVEN
- [ ] Expérimenter avec les poids
- [ ] Ajouter des métriques personnalisées
- [ ] Implémenter des algorithmes alternatifs
- [ ] Construire une application ONOS native (avancé)

## ✨ Vous Avez Terminé !

Si toutes les cases sont cochées, vous avez un environnement ONOS + Mininet + RAVEN entièrement fonctionnel !

Commencez à expérimenter avec différentes topologies et algorithmes de sélection de chemins.
