#!/usr/bin/env python3
"""
Diamond4 Topology - Leaf-Spine Architecture
Topologie pour examen TP - Firewall et Optimisation IA

Architecture:
    4 Spine Switches (s1, s2, s3, s4)
    4 Leaf Switches (s5, s6, s7, s8)
    8 Hosts (h1-h8, 2 hôtes par leaf)
    
    Full-mesh entre Leaf et Spine
    
           [Spine Layer]
        s1    s2    s3    s4
        |  \  /  \/  /  \  |
        |   \/   /\   \/  |
        |   /\  /  \  /\  |
        |  /  \/    \/  \ |
           [Leaf Layer]
        s5    s6    s7    s8
        |     |     |     |
       h1 h2 h3 h4 h5 h6 h7 h8
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

class Diamond4Topo(Topo):
    """
    Topologie Diamond4 - Leaf-Spine avec 4 spines, 4 leafs, 8 hôtes
    """
    
    def build(self):
        """
        Construction de la topologie Diamond4
        """
        
        info('*** Adding Spine switches (Core layer)\n')
        # 4 Spine switches - couche core
        s1 = self.addSwitch('s1', protocols='OpenFlow13')
        s2 = self.addSwitch('s2', protocols='OpenFlow13')
        s3 = self.addSwitch('s3', protocols='OpenFlow13')
        s4 = self.addSwitch('s4', protocols='OpenFlow13')
        
        info('*** Adding Leaf switches (Edge layer)\n')
        # 4 Leaf switches - couche edge
        s5 = self.addSwitch('s5', protocols='OpenFlow13')
        s6 = self.addSwitch('s6', protocols='OpenFlow13')
        s7 = self.addSwitch('s7', protocols='OpenFlow13')
        s8 = self.addSwitch('s8', protocols='OpenFlow13')
        
        info('*** Adding hosts (2 per leaf)\n')
        # 8 hôtes - 2 par leaf switch
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
        h3 = self.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03')
        h4 = self.addHost('h4', ip='10.0.0.4/24', mac='00:00:00:00:00:04')
        h5 = self.addHost('h5', ip='10.0.0.5/24', mac='00:00:00:00:00:05')
        h6 = self.addHost('h6', ip='10.0.0.6/24', mac='00:00:00:00:00:06')
        h7 = self.addHost('h7', ip='10.0.0.7/24', mac='00:00:00:00:00:07')
        h8 = self.addHost('h8', ip='10.0.0.8/24', mac='00:00:00:00:00:08')
        
        info('*** Creating Leaf-to-Host links\n')
        # Connexions Leaf-Host (2 hôtes par leaf)
        self.addLink(h1, s5)  # Leaf 1
        self.addLink(h2, s5)
        
        self.addLink(h3, s6)  # Leaf 2
        self.addLink(h4, s6)
        
        self.addLink(h5, s7)  # Leaf 3
        self.addLink(h6, s7)
        
        self.addLink(h7, s8)  # Leaf 4
        self.addLink(h8, s8)
        
        info('*** Creating Full-Mesh Leaf-to-Spine links\n')
        # Full-mesh entre tous les Leaf et tous les Spine
        # Chaque Leaf est connecté à tous les Spines (4 chemins possibles)
        
        # Leaf s5 vers tous les Spines
        self.addLink(s5, s1)
        self.addLink(s5, s2)
        self.addLink(s5, s3)
        self.addLink(s5, s4)
        
        # Leaf s6 vers tous les Spines
        self.addLink(s6, s1)
        self.addLink(s6, s2)
        self.addLink(s6, s3)
        self.addLink(s6, s4)
        
        # Leaf s7 vers tous les Spines
        self.addLink(s7, s1)
        self.addLink(s7, s2)
        self.addLink(s7, s3)
        self.addLink(s7, s4)
        
        # Leaf s8 vers tous les Spines
        self.addLink(s8, s1)
        self.addLink(s8, s2)
        self.addLink(s8, s3)
        self.addLink(s8, s4)

# Fonction pour lancer la topologie directement
def run_diamond4():
    """
    Lance la topologie Diamond4 avec le contrôleur ONOS
    """
    
    setLogLevel('info')
    
    # Créer la topologie
    topo = Diamond4Topo()
    
    # Créer le réseau avec contrôleur distant ONOS
    net = Mininet(
        topo=topo,
        controller=RemoteController,
        link=TCLink
    )
    
    info('*** Adding ONOS controller\n')
    net.addController('c0', controller=RemoteController, ip='onos', port=6653)
    
    info('*** Starting network\n')
    net.start()
    
    info('\n')
    info('=' * 80 + '\n')
    info('*** Topologie Diamond4 (Leaf-Spine) créée avec succès!\n')
    info('=' * 80 + '\n')
    info('\n')
    info('Architecture:\n')
    info('  - 4 Spine switches (s1, s2, s3, s4) - Couche Core\n')
    info('  - 4 Leaf switches (s5, s6, s7, s8) - Couche Edge\n')
    info('  - 8 Hosts (h1-h8) - 2 hôtes par leaf\n')
    info('\n')
    info('Connectivité:\n')
    info('  - Full-mesh Leaf-Spine: Chaque leaf connecté aux 4 spines\n')
    info('  - 4 chemins possibles entre chaque paire de leafs\n')
    info('  - Total: 16 liens Leaf-Spine + 8 liens Leaf-Host = 24 liens\n')
    info('\n')
    info('Distribution des hôtes:\n')
    info('  - Leaf s5: h1, h2\n')
    info('  - Leaf s6: h3, h4\n')
    info('  - Leaf s7: h5, h6\n')
    info('  - Leaf s8: h7, h8\n')
    info('\n')
    info('Tests recommandés:\n')
    info('  1. pingall                    - Tester la connectivité globale\n')
    info('  2. h1 ping -c 10 h3           - Tester un chemin spécifique\n')
    info('  3. iperf h1 h5                - Mesurer la bande passante\n')
    info('  4. link s5 s1 down            - Simuler une panne\n')
    info('  5. pingall                    - Vérifier la redondance\n')
    info('\n')
    info('Commandes ONOS utiles:\n')
    info('  - Voir les périphériques:     curl -u onos:rocks http://localhost:8181/onos/v1/devices\n')
    info('  - Voir les liens:             curl -u onos:rocks http://localhost:8181/onos/v1/links\n')
    info('  - Voir les flux:              curl -u onos:rocks http://localhost:8181/onos/v1/flows\n')
    info('  - Voir les chemins:           curl -u onos:rocks http://localhost:8181/onos/v1/paths/{src}/{dst}\n')
    info('\n')
    info('Pour l\'examen:\n')
    info('  - Application FWD doit utiliser les 4 chemins disponibles\n')
    info('  - Implémenter la sélection de chemin avec IA/optimisation\n')
    info('  - Comparer avec la méthode classique (Round-Robin, Random, etc.)\n')
    info('=' * 80 + '\n')
    info('\n')
    
    info('*** Running CLI\n')
    CLI(net)
    
    info('*** Stopping network\n')
    net.stop()

# Point d'entrée pour Mininet CLI
topos = {
    'diamond4': Diamond4Topo
}

# Lancement direct si exécuté comme script
if __name__ == '__main__':
    run_diamond4()
