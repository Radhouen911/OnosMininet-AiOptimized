#!/usr/bin/env python3
"""
Topologie réaliste de datacenter avec RAVEN
Simule un datacenter avec :
- Liens de différentes qualités (bande passante, latence, perte)
- Chemins redondants
- Points de défaillance potentiels
"""

from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

def datacenter_topology():
    """
    Topologie datacenter réaliste :
    
    Architecture à 3 niveaux (Spine-Leaf) :
    
                    [Core Switches]
                    s1 ----------- s2
                   /  \           /  \
                  /    \         /    \
                 /      \       /      \
            [Spine]    [Spine]
            s3          s4          s5          s6
            |  \      /  |  \      /  |  \      /  |
            |   \    /   |   \    /   |   \    /   |
            |    \  /    |    \  /    |    \  /    |
          [Leaf Switches - ToR]
          s7      s8      s9      s10     s11     s12
          |       |       |       |       |       |
        [Serveurs/Hôtes]
        h1      h2      h3      h4      h5      h6
    
    Caractéristiques réalistes :
    - Core: Liens 100Gbps, latence 1ms, fiabilité 99.9%
    - Spine: Liens 40Gbps, latence 2ms, fiabilité 99%
    - Leaf: Liens 10Gbps, latence 5ms, fiabilité 95%
    - Certains liens avec perte de paquets simulée
    """
    
    net = Mininet(controller=RemoteController, link=TCLink)
    
    info('*** Adding ONOS controller\n')
    net.addController('c0', controller=RemoteController, ip='onos', port=6653)
    
    info('*** Adding Core switches (haute performance)\n')
    s1 = net.addSwitch('s1', protocols='OpenFlow13')
    s2 = net.addSwitch('s2', protocols='OpenFlow13')
    
    info('*** Adding Spine switches (performance moyenne)\n')
    s3 = net.addSwitch('s3', protocols='OpenFlow13')
    s4 = net.addSwitch('s4', protocols='OpenFlow13')
    s5 = net.addSwitch('s5', protocols='OpenFlow13')
    s6 = net.addSwitch('s6', protocols='OpenFlow13')
    
    info('*** Adding Leaf switches / ToR (Top of Rack)\n')
    s7 = net.addSwitch('s7', protocols='OpenFlow13')
    s8 = net.addSwitch('s8', protocols='OpenFlow13')
    s9 = net.addSwitch('s9', protocols='OpenFlow13')
    s10 = net.addSwitch('s10', protocols='OpenFlow13')
    s11 = net.addSwitch('s11', protocols='OpenFlow13')
    s12 = net.addSwitch('s12', protocols='OpenFlow13')
    
    info('*** Adding hosts (serveurs)\n')
    h1 = net.addHost('h1', ip='10.0.1.1/24', mac='00:00:00:00:01:01')
    h2 = net.addHost('h2', ip='10.0.1.2/24', mac='00:00:00:00:01:02')
    h3 = net.addHost('h3', ip='10.0.1.3/24', mac='00:00:00:00:01:03')
    h4 = net.addHost('h4', ip='10.0.1.4/24', mac='00:00:00:00:01:04')
    h5 = net.addHost('h5', ip='10.0.1.5/24', mac='00:00:00:00:01:05')
    h6 = net.addHost('h6', ip='10.0.1.6/24', mac='00:00:00:00:01:06')
    
    info('*** Creating Core links (100Gbps, 1ms latency, très fiable)\n')
    # Lien principal entre cores - excellente qualité
    net.addLink(s1, s2, bw=100, delay='1ms', loss=0, use_htb=True)
    
    info('*** Creating Core-to-Spine links (40Gbps, 2ms latency)\n')
    # Core s1 vers Spines - bonne qualité
    net.addLink(s1, s3, bw=40, delay='2ms', loss=0, use_htb=True)
    net.addLink(s1, s4, bw=40, delay='2ms', loss=0, use_htb=True)
    
    # Core s2 vers Spines - bonne qualité
    net.addLink(s2, s5, bw=40, delay='2ms', loss=0, use_htb=True)
    net.addLink(s2, s6, bw=40, delay='2ms', loss=0, use_htb=True)
    
    info('*** Creating Spine-to-Leaf links (10Gbps, qualité variable)\n')
    # Spine s3 vers Leafs - qualité variable
    net.addLink(s3, s7, bw=10, delay='5ms', loss=0, use_htb=True)  # Bon lien
    net.addLink(s3, s8, bw=10, delay='8ms', loss=1, use_htb=True)  # Lien avec latence et perte
    
    # Spine s4 vers Leafs - qualité variable
    net.addLink(s4, s8, bw=10, delay='5ms', loss=0, use_htb=True)  # Bon lien
    net.addLink(s4, s9, bw=10, delay='10ms', loss=2, use_htb=True)  # Lien dégradé
    
    # Spine s5 vers Leafs - qualité variable
    net.addLink(s5, s9, bw=10, delay='5ms', loss=0, use_htb=True)  # Bon lien
    net.addLink(s5, s10, bw=10, delay='7ms', loss=1, use_htb=True)  # Lien moyen
    
    # Spine s6 vers Leafs - qualité variable
    net.addLink(s6, s10, bw=10, delay='5ms', loss=0, use_htb=True)  # Bon lien
    net.addLink(s6, s11, bw=10, delay='12ms', loss=3, use_htb=True)  # Lien très dégradé
    net.addLink(s6, s12, bw=10, delay='6ms', loss=0.5, use_htb=True)  # Lien correct
    
    # Liens supplémentaires pour redondance
    net.addLink(s3, s9, bw=10, delay='6ms', loss=0.5, use_htb=True)
    net.addLink(s4, s10, bw=10, delay='6ms', loss=0.5, use_htb=True)
    net.addLink(s5, s11, bw=10, delay='5ms', loss=0, use_htb=True)
    
    info('*** Creating Leaf-to-Host links (1Gbps, 10ms latency)\n')
    # Connexions serveurs - qualité standard
    net.addLink(h1, s7, bw=1, delay='10ms', loss=0, use_htb=True)
    net.addLink(h2, s8, bw=1, delay='10ms', loss=0, use_htb=True)
    net.addLink(h3, s9, bw=1, delay='10ms', loss=0, use_htb=True)
    net.addLink(h4, s10, bw=1, delay='10ms', loss=0, use_htb=True)
    net.addLink(h5, s11, bw=1, delay='10ms', loss=0, use_htb=True)
    net.addLink(h6, s12, bw=1, delay='10ms', loss=0, use_htb=True)
    
    info('*** Starting network\n')
    net.start()
    
    info('\n')
    info('=' * 70 + '\n')
    info('*** Topologie Datacenter créée avec succès!\n')
    info('=' * 70 + '\n')
    info('\n')
    info('Architecture:\n')
    info('  - 2 Core switches (s1, s2) - Liens 100Gbps\n')
    info('  - 4 Spine switches (s3-s6) - Liens 40Gbps\n')
    info('  - 6 Leaf/ToR switches (s7-s12) - Liens 10Gbps\n')
    info('  - 6 Serveurs (h1-h6)\n')
    info('\n')
    info('Caractéristiques des liens:\n')
    info('  ✓ Liens Core: 100Gbps, 1ms, 0% perte (excellents)\n')
    info('  ✓ Liens Core-Spine: 40Gbps, 2ms, 0% perte (bons)\n')
    info('  ⚠ Liens Spine-Leaf: 10Gbps, 5-12ms, 0-3% perte (variables)\n')
    info('  • Liens Leaf-Host: 1Gbps, 10ms, 0% perte (standard)\n')
    info('\n')
    info('RAVEN va choisir les meilleurs chemins en évitant:\n')
    info('  - Les liens avec haute latence (>10ms)\n')
    info('  - Les liens avec perte de paquets (>1%)\n')
    info('  - Les chemins avec trop de sauts\n')
    info('\n')
    info('Tests recommandés:\n')
    info('  1. pingall - Tester la connectivité\n')
    info('  2. iperf h1 h6 - Mesurer la bande passante\n')
    info('  3. h1 ping -c 10 h6 - Voir la latence\n')
    info('  4. link s3 s7 down - Simuler une panne\n')
    info('  5. Surveiller: docker logs -f raven-controller\n')
    info('\n')
    info('Chemins intéressants à observer:\n')
    info('  h1 -> h6: Plusieurs chemins possibles via différents Spines\n')
    info('  h1 -> h4: Chemins courts vs chemins fiables\n')
    info('=' * 70 + '\n')
    info('\n')
    
    info('*** Running CLI\n')
    CLI(net)
    
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    datacenter_topology()
