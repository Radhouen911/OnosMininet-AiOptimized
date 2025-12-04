# Démarrage Rapide - ONOS + Mininet + RAVEN

## 🚀 Démarrage en 3 étapes

### Étape 1 : Démarrer l'environnement

**Windows :**

```bash
start.bat
```

**Linux/Mac :**

```bash
chmod +x start.sh
./start.sh
```

**Ou manuellement :**

```bash
docker compose up -d
```

Attendez 90 secondes pour qu'ONOS démarre complètement.

---

### Étape 2 : Vérifier que tout fonctionne

**Tester l'API ONOS :**

```bash
curl -u onos:rocks http://localhost:8181/onos/v1/applications
```

Si ça retourne du JSON → ✅ ONOS est prêt !

**Accéder à la GUI :**

```
http://localhost:8181/onos/ui/index.html
```

Login : `onos` / `rocks`

---

### Étape 3 : Lancer votre topologie

**Entrer dans Mininet :**

```bash
docker exec -it mininet bash
```

**Lancer Diamond4 (pour l'examen) :**

```bash
mn --custom /topologies/diamond4.py --topo diamond4 --controller remote,ip=onos,port=6653
```

**Dans Mininet CLI :**

```bash
mininet> pingall
mininet> net
mininet> links
```

---

## 📊 Voir les décisions RAVEN

**Dans un autre terminal :**

```bash
docker logs -f raven-controller
```

Vous verrez :

- Les chemins calculés
- Les scores RAVEN
- Les meilleurs chemins sélectionnés

---

## 🔍 Vérifier la topologie dans ONOS

**Via API REST :**

```bash
# Voir les switches
curl -u onos:rocks http://localhost:8181/onos/v1/devices

# Voir les liens
curl -u onos:rocks http://localhost:8181/onos/v1/links

# Voir les hôtes
curl -u onos:rocks http://localhost:8181/onos/v1/hosts

# Voir les flux
curl -u onos:rocks http://localhost:8181/onos/v1/flows
```

**Via GUI :**

- Ouvrir http://localhost:8181/onos/ui/index.html
- Cliquer sur "Topology"
- Voir votre réseau Diamond4 en temps réel

---

## 🧪 Tests pour l'examen

### Test 1 : Connectivité de base

```bash
mininet> pingall
```

### Test 2 : Mesurer la bande passante

```bash
mininet> iperf h1 h5
```

### Test 3 : Simuler une panne

```bash
mininet> link s5 s1 down
mininet> pingall
mininet> link s5 s1 up
```

### Test 4 : Voir les 4 chemins disponibles

Dans les logs RAVEN, vous verrez les différents chemins entre leafs via les 4 spines.

---

## 🛑 Arrêter l'environnement

```bash
docker compose down
```

Pour tout supprimer (y compris les volumes) :

```bash
docker compose down -v
```

---

## ❓ Problèmes courants

### ONOS ne démarre pas

- Attendez 2-3 minutes complètes
- Vérifiez les logs : `docker logs onos`
- Redémarrez : `docker compose restart onos`

### Mininet ne se connecte pas à ONOS

- Vérifiez qu'ONOS tourne : `docker compose ps`
- Utilisez la commande `mn` avec `--controller remote,ip=onos,port=6653`

### GUI ne fonctionne pas

- Essayez : http://localhost:8181/onos/ui/index.html
- Ou : http://localhost:8181
- L'API REST fonctionne toujours même si la GUI ne marche pas

---

## 📚 Topologies disponibles

- **diamond4.py** - Pour l'examen (4 spines, 4 leafs, 8 hôtes)
- **datacenter_topology.py** - Datacenter réaliste
- **enterprise_multisite_topology.py** - Multi-sites avec WAN
- **simple_topology.py** - Test basique

---

## ✅ Checklist pour l'examen

- [ ] `docker compose up -d` fonctionne
- [ ] ONOS GUI accessible
- [ ] Mininet lance diamond4.py
- [ ] `pingall` réussit
- [ ] RAVEN calcule les scores
- [ ] Les 4 chemins sont visibles
- [ ] Simulation de panne fonctionne

Bon courage pour votre examen ! 🎓
