#!/usr/bin/env python3
"""
Topologie réseau d'entreprise multi-sites
Simule une entreprise avec plusieurs sites connectés via WAN
RAVEN doit choisir entre chemins locaux rapides et chemins WAN lents
"""

from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

def enterprise_multisite_topology():
    """
    Topologie multi-sites :
    
    Site A (Paris)          WAN Links          Site B (Londres)
    ┌─────────────┐         (lents)           ┌─────────────┐
    │    h1       │                            │    h4       │
    │     |       │                            │     |       │
    │    s1       │                            │    s4       │
    │   /  \      │                            │   /  \      │
    │  s2  s3 ────┼────── s7 (WAN) ────────────┼─ s5  s6    │
    │  |    |     │      /  \                  │  |    |     │
    │  h2   h3    │     /    \                 │  h5   h6    │
    └─────────────┘    /      \                └─────────────┘
                      /        \
                     /          \
              Site C (Berlin)    Backup WAN
              ┌─────────────┐
              │    h7       │
              │     |       │
              │    s8       │
              │   /  \      │
              │  s9  s10    │
              │  |    |     │
              │  h8   h9    │
              └─────────────┘
    
    Scénarios réalistes :
    - Liens LAN rapides (1Gbps, 1ms)
    - Liens WAN lents (100Mbps, 50ms, perte 1%)
    - Backup WAN très lent (10Mbps, 100ms, perte 3%)
    """
    
    net = Mininet(controller=RemoteController, link=TCLink)
    
    info('*** Adding ONOS controller\n')
    net.addController('c0', controller=RemoteController, ip='onos', port=6653)
    
    info('*** Site A - Paris (LAN rapide)\n')
    s1 = net.addSwitch('s1', protocols='OpenFlow13')  # Core Paris
    s2 = net.addSwitch('s2', protocols='OpenFlow13')  # Access Paris
    s3 = net.addSwitch('s3', protocols='OpenFlow13')  # Access Paris
    
    h1 = net.addHost('h1', ip='10.1.0.1/16', mac='00:00:00:00:01:01')  # Serveur Paris
    h2 = net.addHost('h2', ip='10.1.0.2/16', mac='00:00:00:00:01:02')  # PC Paris 1
    h3 = net.addHost('h3', ip='10.1.0.3/16', mac='00:00:00:00:01:03')  # PC Paris 2
    
    info('*** Site B - Londres (LAN rapide)\n')
    s4 = net.addSwitch('s4', protocols='OpenFlow13')  # Core Londres
    s5 = net.addSwitch('s5', protocols='OpenFlow13')  # Access Londres
    s6 = net.addSwitch('s6', protocols='OpenFlow13')  # Access Londres
    
    h4 = net.addHost('h4', ip='10.2.0.1/16', mac='00:00:00:00:02:01')  # Serveur Londres
    h5 = net.addHost('h5', ip='10.2.0.2/16', mac='00:00:00:00:02:02')  # PC Londres 1
    h6 = net.addHost('h6', ip='10.2.0.3/16', mac='00:00:00:00:02:03')  # PC Londres 2
    
    info('*** Site C - Berlin (LAN rapide)\n')
    s8 = net.addSwitch('s8', protocols='OpenFlow13')  # Core Berlin
    s9 = net.addSwitch('s9', protocols='OpenFlow13')  # Access Berlin
    s10 = net.addSwitch('s10', protocols='OpenFlow13')  # Access Berlin
    
    h7 = net.addHost('h7', ip='10.3.0.1/16', mac='00:00:00:00:03:01')  # Serveur Berlin
    h8 = net.addHost('h8', ip='10.3.0.2/16', mac='00:00:00:00:03:02')  # PC Berlin 1
    h9 = net.addHost('h9', ip='10.3.0.3/16', mac='00:00:00:00:03:03')  # PC Berlin 2
    
    info('*** WAN Router\n')
    s7 = net.addSwitch('s7', protocols='OpenFlow13')  # Routeur WAN central
    
    info('*** Creating LAN links (Site A - Paris) - Rapides\n')
    net.addLink(h1, s1, bw=1000, delay='1ms', loss=0, use_htb=True)
    net.addLink(s1, s2, bw=1000, delay='1ms', loss=0, use_htb=True)
    net.addLink(s1, s3, bw=1000, delay='1ms', loss=0, use_htb=True)
    net.addLink(h2, s2, bw=1000, delay='1ms', loss=0, use_htb=True)
    net.addLink(h3, s3, bw=1000, delay='1ms', loss=0, use_htb=True)
    
    info('*** Creating LAN links (Site B - Londres) - Rapides\n')
    net.addLink(h4, s4, bw=1000, delay='1ms', loss=0, use_htb=True)
    net.addLink(s4, s5, bw=1000, delay='1ms', loss=0, use_htb=True)
    net.addLink(s4, s6, bw=1000, delay='1ms', loss=0, use_htb=True)
    net.addLink(h5, s5, bw=1000, delay='1ms', loss=0, use_htb=True)
    net.addLink(h6, s6, bw=1000, delay='1ms', loss=0, use_htb=True)
    
    info('*** Creating LAN links (Site C - Berlin) - Rapides\n')
    net.addLink(h7, s8, bw=1000, delay='1ms', loss=0, use_htb=True)
    net.addLink(s8, s9, bw=1000, delay='1ms', loss=0, use_htb=True)
    net.addLink(s8, s10, bw=1000, delay='1ms', loss=0, use_htb=True)
    net.addLink(h8, s9, bw=1000, delay='1ms', loss=0, use_htb=True)
    net.addLink(h9, s10, bw=1000, delay='1ms', loss=0, use_htb=True)
    
    info('*** Creating WAN links - Lents et variables\n')
    # Lien WAN principal Paris -> WAN Router (bon)
    net.addLink(s1, s7, bw=100, delay='20ms', loss=0.5, use_htb=True)
    
    # Lien WAN principal Londres -> WAN Router (moyen)
    net.addLink(s4, s7, bw=100, delay='25ms', loss=1, use_htb=True)
    
    # Lien WAN principal Berlin -> WAN Router (dégradé)
    net.addLink(s8, s7, bw=50, delay='30ms', loss=2, use_htb=True)
    
    # Lien WAN backup Paris -> Londres (très lent mais direct)
    net.addLink(s1, s4, bw=10, delay='100ms', loss=3, use_htb=True)
    
    # Lien WAN backup Londres -> Berlin (très lent)
    net.addLink(s4, s8, bw=10, delay='120ms', loss=4, use_htb=True)
    
    # Lien WAN backup Paris -> Berlin (extrêmement lent)
    net.addLink(s1, s8, bw=5, delay='150ms', loss=5, use_htb=True)
    
    info('*** Starting network\n')
    net.start()
    
    info('\n')
    info('=' * 80 + '\n')
    info('*** Topologie Entreprise Multi-Sites créée!\n')
    info('=' * 80 + '\n')
    info('\n')
    info('Sites:\n')
    info('  📍 Site A (Paris):   h1, h2, h3 via s1, s2, s3\n')
    info('  📍 Site B (Londres): h4, h5, h6 via s4, s5, s6\n')
    info('  📍 Site C (Berlin):  h7, h8, h9 via s8, s9, s10\n')
    info('  🌐 WAN Router: s7 (interconnexion)\n')
    info('\n')
    info('Caractéristiques des liens:\n')
    info('  ✓ LAN (intra-site):     1Gbps, 1ms, 0% perte (excellent)\n')
    info('  ⚠ WAN principal:        50-100Mbps, 20-30ms, 0.5-2% perte (moyen)\n')
    info('  ❌ WAN backup:          5-10Mbps, 100-150ms, 3-5% perte (mauvais)\n')
    info('\n')
    info('Décisions RAVEN attendues:\n')
    info('  • Trafic local (même site): Utiliser LAN rapide\n')
    info('  • Trafic inter-sites: Préférer WAN principal via s7\n')
    info('  • En cas de panne WAN principal: Basculer sur backup (lent)\n')
    info('\n')
    info('Tests recommandés:\n')
    info('  1. h1 ping h2          - Trafic local Paris (devrait être rapide)\n')
    info('  2. h1 ping h4          - Paris -> Londres via WAN\n')
    info('  3. h1 ping h7          - Paris -> Berlin via WAN\n')
    info('  4. iperf h1 h4         - Mesurer bande passante inter-sites\n')
    info('  5. link s1 s7 down     - Couper WAN principal Paris\n')
    info('  6. h1 ping h4          - Devrait utiliser backup (très lent)\n')
    info('\n')
    info('Scénarios intéressants:\n')
    info('  • RAVEN devrait éviter les liens backup sauf en cas de panne\n')
    info('  • Comparer latence avant/après panne du WAN principal\n')
    info('  • Observer le score des chemins dans les logs RAVEN\n')
    info('=' * 80 + '\n')
    info('\n')
    
    info('*** Running CLI\n')
    CLI(net)
    
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    enterprise_multisite_topology()
