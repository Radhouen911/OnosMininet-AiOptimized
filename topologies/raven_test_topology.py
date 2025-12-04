#!/usr/bin/env python3
"""
Test topology for RAVEN algorithm
Creates a network with multiple paths between hosts
"""

from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

def raven_test_topology():
    """
    Create topology with multiple paths for RAVEN testing
    
    Topology:
              s2 --- s3
             /  \   /  \
        h1--s1    X    s4--h2
             \  /   \  /
              s5 --- s6
    
    Multiple paths between h1 and h2:
    - Path 1: h1-s1-s2-s3-s4-h2 (5 hops, high reliability)
    - Path 2: h1-s1-s5-s6-s4-h2 (5 hops, lower reliability)
    - Path 3: h1-s1-s2-s6-s4-h2 (5 hops, medium reliability)
    - Path 4: h1-s1-s5-s3-s4-h2 (5 hops, medium reliability)
    """
    
    net = Mininet(controller=RemoteController, link=TCLink)
    
    info('*** Adding ONOS controller\n')
    net.addController('c0', controller=RemoteController, ip='onos', port=6653)
    
    info('*** Adding switches\n')
    s1 = net.addSwitch('s1', protocols='OpenFlow13')
    s2 = net.addSwitch('s2', protocols='OpenFlow13')
    s3 = net.addSwitch('s3', protocols='OpenFlow13')
    s4 = net.addSwitch('s4', protocols='OpenFlow13')
    s5 = net.addSwitch('s5', protocols='OpenFlow13')
    s6 = net.addSwitch('s6', protocols='OpenFlow13')
    
    info('*** Adding hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
    h2 = net.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
    h3 = net.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03')
    h4 = net.addHost('h4', ip='10.0.0.4/24', mac='00:00:00:00:00:04')
    
    info('*** Creating links with different characteristics\n')
    
    # Host to switch links
    net.addLink(h1, s1, bw=100)
    net.addLink(h2, s4, bw=100)
    net.addLink(h3, s2, bw=100)
    net.addLink(h4, s6, bw=100)
    
    # Upper path (high bandwidth, high reliability)
    net.addLink(s1, s2, bw=100, delay='5ms', loss=0)
    net.addLink(s2, s3, bw=100, delay='5ms', loss=0)
    net.addLink(s3, s4, bw=100, delay='5ms', loss=0)
    
    # Lower path (lower bandwidth, lower reliability)
    net.addLink(s1, s5, bw=50, delay='10ms', loss=1)
    net.addLink(s5, s6, bw=50, delay='10ms', loss=1)
    net.addLink(s6, s4, bw=50, delay='10ms', loss=1)
    
    # Cross links (medium characteristics)
    net.addLink(s2, s6, bw=75, delay='7ms', loss=0.5)
    net.addLink(s5, s3, bw=75, delay='7ms', loss=0.5)
    
    info('*** Starting network\n')
    net.start()
    
    info('*** Network topology created\n')
    info('*** RAVEN controller will analyze paths and select best routes\n')
    info('*** \n')
    info('*** Test commands:\n')
    info('***   pingall              - Test connectivity\n')
    info('***   iperf h1 h2          - Test bandwidth\n')
    info('***   link s1 s2 down      - Simulate link failure\n')
    info('***   link s1 s2 up        - Restore link\n')
    info('*** \n')
    info('*** Monitor RAVEN: docker logs -f raven-controller\n')
    info('*** \n')
    
    info('*** Running CLI\n')
    CLI(net)
    
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    raven_test_topology()
