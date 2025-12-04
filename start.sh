#!/bin/bash
# Script de démarrage automatique pour ONOS + Mininet + RAVEN

echo "=========================================="
echo "Démarrage de l'environnement ONOS + Mininet + RAVEN"
echo "=========================================="
echo ""

# Démarrer les conteneurs
echo "1. Démarrage des conteneurs..."
docker compose up -d

echo ""
echo "2. Attente du démarrage d'ONOS (90 secondes)..."
sleep 90

echo ""
echo "3. Vérification qu'ONOS est prêt..."
curl -s -u onos:rocks http://localhost:8181/onos/v1/applications > /dev/null
if [ $? -eq 0 ]; then
    echo "✓ ONOS est prêt!"
else
    echo "⚠ ONOS n'est pas encore prêt, attendez encore 30 secondes..."
    sleep 30
fi

echo ""
echo "=========================================="
echo "Environnement prêt!"
echo "=========================================="
echo ""
echo "Accès:"
echo "  - GUI ONOS:  http://localhost:8181/onos/ui/index.html"
echo "  - Login:     onos / rocks"
echo "  - API REST:  http://localhost:8181/onos/v1/"
echo ""
echo "Pour lancer la topologie Diamond4:"
echo "  docker exec -it mininet bash"
echo "  mn --custom /topologies/diamond4.py --topo diamond4 --controller remote,ip=onos,port=6653"
echo ""
echo "Logs RAVEN:"
echo "  docker logs -f raven-controller"
echo ""
echo "=========================================="
