#!/usr/bin/env python3
"""
Custom topology template - modify as needed
"""

from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

def custom_topology():
    """Create your custom topology here"""
    
    net = Mininet(controller=RemoteController, link=TCLink)
    
    info('*** Adding ONOS controller\n')
    net.addController('c0', controller=RemoteController, ip='onos', port=6653)
    
    info('*** Adding switches\n')
    # Add your switches here
    # Example: s1 = net.addSwitch('s1', protocols='OpenFlow13')
    
    info('*** Adding hosts\n')
    # Add your hosts here
    # Example: h1 = net.addHost('h1', ip='10.0.0.1/24')
    
    info('*** Creating links\n')
    # Add your links here with optional bandwidth/delay/loss parameters
    # Example: net.addLink(h1, s1, bw=10, delay='5ms', loss=1)
    
    info('*** Starting network\n')
    net.start()
    
    info('*** Running CLI\n')
    CLI(net)
    
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    custom_topology()
