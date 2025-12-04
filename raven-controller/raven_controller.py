#!/usr/bin/env python3
"""
RAVEN (Reliability-Aware Virtual Network Embedding) Controller
This controller monitors ONOS topology and implements RAVEN path selection
"""

import requests
import json
import time
import logging
from typing import List, Dict, Tuple
import networkx as nx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAVENController:
    def __init__(self, onos_url="http://onos:8181", username="onos", password="rocks"):
        self.onos_url = onos_url
        self.auth = (username, password)
        self.topology = nx.Graph()
        self.link_reliability = {}  # Track link reliability scores
        self.link_bandwidth = {}    # Track available bandwidth
        self.link_failures = {}     # Track failure history
        
    def get_topology(self):
        """Fetch current topology from ONOS"""
        try:
            # Get devices
            devices_url = f"{self.onos_url}/onos/v1/devices"
            devices_resp = requests.get(devices_url, auth=self.auth, timeout=5)
            devices = devices_resp.json().get('devices', [])
            
            # Get links
            links_url = f"{self.onos_url}/onos/v1/links"
            links_resp = requests.get(links_url, auth=self.auth, timeout=5)
            links = links_resp.json().get('links', [])
            
            # Get hosts
            hosts_url = f"{self.onos_url}/onos/v1/hosts"
            hosts_resp = requests.get(hosts_url, auth=self.auth, timeout=5)
            hosts = hosts_resp.json().get('hosts', [])
            
            return devices, links, hosts
        except Exception as e:
            logger.error(f"Error fetching topology: {e}")
            return [], [], []
    
    def build_graph(self, devices, links, hosts):
        """Build NetworkX graph from ONOS topology"""
        self.topology.clear()
        
        # Add switches
        for device in devices:
            if device.get('available'):
                self.topology.add_node(device['id'], type='switch')
        
        # Add hosts
        for host in hosts:
            host_id = host['id']
            self.topology.add_node(host_id, type='host')
            # Connect host to its switch
            for location in host.get('locations', []):
                device_id = location['elementId']
                if device_id in self.topology:
                    link_key = f"{host_id}-{device_id}"
                    self.topology.add_edge(host_id, device_id)
                    self.initialize_link_metrics(link_key)
        
        # Add links between switches
        for link in links:
            if link.get('state') == 'ACTIVE':
                src = link['src']['device']
                dst = link['dst']['device']
                link_key = f"{src}-{dst}"
                
                self.topology.add_edge(src, dst)
                self.initialize_link_metrics(link_key)
        
        logger.info(f"Graph built: {self.topology.number_of_nodes()} nodes, {self.topology.number_of_edges()} edges")
    
    def initialize_link_metrics(self, link_key):
        """Initialize metrics for a link"""
        if link_key not in self.link_reliability:
            self.link_reliability[link_key] = 1.0  # Start with perfect reliability
            self.link_bandwidth[link_key] = 100.0  # Assume 100 Mbps
            self.link_failures[link_key] = 0
    
    def compute_link_reliability(self, link_key):
        """
        Compute link reliability based on failure history
        RAVEN metric: R(l) = uptime / (uptime + downtime)
        """
        failures = self.link_failures.get(link_key, 0)
        # Simple model: reliability decreases with failures
        reliability = max(0.1, 1.0 - (failures * 0.1))
        return reliability
    
    def compute_path_reliability(self, path):
        """
        Compute path reliability as product of link reliabilities
        RAVEN: R(p) = ∏ R(l) for all links l in path
        """
        reliability = 1.0
        for i in range(len(path) - 1):
            link_key = f"{path[i]}-{path[i+1]}"
            link_reliability = self.compute_link_reliability(link_key)
            reliability *= link_reliability
        return reliability
    
    def compute_path_bandwidth(self, path):
        """
        Compute available bandwidth (bottleneck link)
        RAVEN: BW(p) = min(BW(l)) for all links l in path
        """
        min_bandwidth = float('inf')
        for i in range(len(path) - 1):
            link_key = f"{path[i]}-{path[i+1]}"
            bandwidth = self.link_bandwidth.get(link_key, 100.0)
            min_bandwidth = min(min_bandwidth, bandwidth)
        return min_bandwidth
    
    def compute_raven_score(self, path, alpha=0.6, beta=0.4):
        """
        Compute RAVEN score for path selection
        Score = α * Reliability + β * (Bandwidth / MaxBandwidth) - γ * HopCount
        
        Args:
            path: List of nodes in the path
            alpha: Weight for reliability (default 0.6)
            beta: Weight for bandwidth (default 0.4)
        """
        reliability = self.compute_path_reliability(path)
        bandwidth = self.compute_path_bandwidth(path)
        hop_count = len(path) - 1
        
        # Normalize bandwidth (assuming max 100 Mbps)
        normalized_bandwidth = bandwidth / 100.0
        
        # Penalize longer paths
        hop_penalty = hop_count * 0.1
        
        score = (alpha * reliability) + (beta * normalized_bandwidth) - hop_penalty
        
        logger.debug(f"Path {path}: Reliability={reliability:.3f}, BW={bandwidth:.1f}, Hops={hop_count}, Score={score:.3f}")
        
        return score
    
    def get_friendly_name(self, node_id):
        """
        Convert node ID to friendly name
        
        Args:
            node_id: Node identifier (MAC address or OpenFlow ID)
        
        Returns:
            Friendly name (e.g., 'h1', 's3', etc.)
        """
        # OpenFlow device IDs
        if node_id.startswith('of:'):
            # Extract the last part of the OpenFlow ID
            device_num = int(node_id.split(':')[-1], 16)
            return f's{device_num}'
        
        # MAC addresses for hosts
        if ':' in node_id:
            # Extract host number from MAC address
            # Format: 00:00:00:00:XX:YY where XX:YY identifies the host
            parts = node_id.split(':')
            if len(parts) >= 6:
                # Try to extract meaningful host number
                try:
                    host_num = int(parts[-1], 16)
                    return f'h{host_num}'
                except:
                    pass
        
        # Fallback to original ID
        return node_id
    
    def format_path(self, path):
        """
        Format path with friendly names
        
        Args:
            path: List of node IDs
        
        Returns:
            Formatted path string with friendly names
        """
        return ' -> '.join([self.get_friendly_name(node) for node in path])
    
    def find_best_path_raven(self, src, dst, k=3):
        """
        Find best path using RAVEN algorithm
        
        Args:
            src: Source node
            dst: Destination node
            k: Number of candidate paths to consider
        
        Returns:
            Best path according to RAVEN scoring
        """
        if src not in self.topology or dst not in self.topology:
            logger.warning(f"Source {self.get_friendly_name(src)} or destination {self.get_friendly_name(dst)} not in topology")
            return None
        
        try:
            # Find k shortest paths
            paths = list(nx.shortest_simple_paths(self.topology, src, dst))[:k]
            
            if not paths:
                logger.warning(f"No path found between {self.get_friendly_name(src)} and {self.get_friendly_name(dst)}")
                return None
            
            # Score each path using RAVEN
            best_path = None
            best_score = float('-inf')
            
            for path in paths:
                score = self.compute_raven_score(path)
                logger.info(f"Path {self.format_path(path)}: Score = {score:.3f}")
                
                if score > best_score:
                    best_score = score
                    best_path = path
            
            logger.info(f"✓ Selected: {self.format_path(best_path)} (Score: {best_score:.3f})")
            return best_path
            
        except nx.NetworkXNoPath:
            logger.warning(f"No path exists between {self.get_friendly_name(src)} and {self.get_friendly_name(dst)}")
            return None
    
    def install_path_flows(self, path, src_mac, dst_mac):
        """Install flow rules for the selected path in ONOS"""
        if not path or len(path) < 2:
            return False
        
        logger.info(f"Installing flows for path: {' -> '.join(path)}")
        
        # Install flows on each switch in the path
        for i in range(len(path) - 1):
            current_node = path[i]
            next_node = path[i + 1]
            
            # Skip if current node is a host
            if self.topology.nodes[current_node].get('type') == 'host':
                continue
            
            # Get output port (simplified - in real scenario, query ONOS for port numbers)
            success = self.install_flow_rule(current_node, dst_mac, next_node)
            if not success:
                logger.error(f"Failed to install flow on {current_node}")
                return False
        
        return True
    
    def install_flow_rule(self, device_id, dst_mac, next_hop):
        """Install a single flow rule via ONOS REST API"""
        url = f"{self.onos_url}/onos/v1/flows/{device_id}"
        
        flow = {
            "priority": 40000,
            "timeout": 0,
            "isPermanent": True,
            "deviceId": device_id,
            "treatment": {
                "instructions": [
                    {"type": "OUTPUT", "port": "1"}  # Simplified - should query actual port
                ]
            },
            "selector": {
                "criteria": [
                    {"type": "ETH_DST", "mac": dst_mac}
                ]
            }
        }
        
        try:
            response = requests.post(url, json=flow, auth=self.auth, timeout=5)
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error installing flow: {e}")
            return False
    
    def monitor_and_update(self):
        """Continuously monitor topology and update paths"""
        logger.info("Starting RAVEN controller monitoring...")
        
        while True:
            try:
                # Fetch topology
                devices, links, hosts = self.get_topology()
                
                if devices or links:
                    # Build graph
                    self.build_graph(devices, links, hosts)
                    
                    # Find all host pairs and compute best paths
                    host_nodes = [n for n, d in self.topology.nodes(data=True) if d.get('type') == 'host']
                    
                    logger.info(f"Found {len(host_nodes)} hosts")
                    
                    # Example: Compute paths between all host pairs
                    for i, src in enumerate(host_nodes):
                        for dst in host_nodes[i+1:]:
                            src_name = self.get_friendly_name(src)
                            dst_name = self.get_friendly_name(dst)
                            logger.info(f"\n{'='*60}")
                            logger.info(f"Computing paths: {src_name} → {dst_name}")
                            logger.info(f"{'='*60}")
                            best_path = self.find_best_path_raven(src, dst)
                            if best_path:
                                logger.info(f"★ BEST PATH: {self.format_path(best_path)}")
                                logger.info(f"{'='*60}\n")
                
                # Sleep before next update
                time.sleep(10)
                
            except KeyboardInterrupt:
                logger.info("Shutting down RAVEN controller")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)

def main():
    # Wait for ONOS to be ready
    logger.info("Waiting for ONOS to be ready...")
    time.sleep(30)
    
    # Create and start RAVEN controller
    controller = RAVENController()
    controller.monitor_and_update()

if __name__ == "__main__":
    main()
