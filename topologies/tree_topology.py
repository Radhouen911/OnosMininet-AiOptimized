#!/usr/bin/env python3
"""
Tree topology with ONOS controller
"""

from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.topo import Topo

class TreeTopo(Topo):
    """Tree topology with configurable depth and fanout"""
    
    def build(self, depth=2, fanout=2):
        # Create tree topology
        self.create_tree(depth, fanout)
    
    def create_tree(self, depth, fanout, parent=None, level=0):
        """Recursively create tree topology"""
        if level == depth:
            return
        
        for i in range(fanout):
            if level == 0:
                # Root switches
                switch = self.addSwitch(f's{level}_{i}', protocols='OpenFlow13')
                self.create_tree(depth, fanout, switch, level + 1)
            elif level == depth - 1:
                # Leaf level - add hosts
                host = self.addHost(f'h{level}_{i}', 
                                   ip=f'10.0.{level}.{i+1}/24',
                                   mac=f'00:00:00:00:{level:02x}:{i+1:02x}')
                self.addLink(parent, host)
            else:
                # Intermediate switches
                switch = self.addSwitch(f's{level}_{i}', protocols='OpenFlow13')
                self.addLink(parent, switch)
                self.create_tree(depth, fanout, switch, level + 1)

def tree_topology():
    """Create and run tree topology"""
    
    topo = TreeTopo(depth=3, fanout=2)
    net = Mininet(topo=topo, controller=RemoteController)
    
    info('*** Adding ONOS controller\n')
    net.addController('c0', controller=RemoteController, ip='onos', port=6653)
    
    info('*** Starting network\n')
    net.start()
    
    info('*** Running CLI\n')
    CLI(net)
    
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    tree_topology()
