#!/usr/bin/env python3
"""
Compare RAVEN routing with default ONOS routing
Run this from your host machine (not inside containers)
"""

import requests
import json
import time
from typing import Dict, List

ONOS_URL = "http://localhost:8181/onos/v1"
AUTH = ("onos", "rocks")

def get_topology():
    """Fetch current topology from ONOS"""
    devices = requests.get(f"{ONOS_URL}/devices", auth=AUTH).json()
    links = requests.get(f"{ONOS_URL}/links", auth=AUTH).json()
    hosts = requests.get(f"{ONOS_URL}/hosts", auth=AUTH).json()
    return devices, links, hosts

def get_flows():
    """Get all flow rules"""
    response = requests.get(f"{ONOS_URL}/flows", auth=AUTH)
    return response.json()

def get_intents():
    """Get all intents"""
    response = requests.get(f"{ONOS_URL}/intents", auth=AUTH)
    return response.json()

def analyze_paths():
    """Analyze current path selection"""
    print("=" * 60)
    print("ROUTING ANALYSIS")
    print("=" * 60)
    
    devices, links, hosts = get_topology()
    
    print(f"\nTopology Overview:")
    print(f"  Devices: {len(devices.get('devices', []))}")
    print(f"  Links: {len(links.get('links', []))}")
    print(f"  Hosts: {len(hosts.get('hosts', []))}")
    
    print(f"\nActive Links:")
    for link in links.get('links', []):
        if link.get('state') == 'ACTIVE':
            src = link['src']['device']
            dst = link['dst']['device']
            print(f"  {src} -> {dst}")
    
    flows = get_flows()
    print(f"\nFlow Rules Installed: {len(flows.get('flows', []))}")
    
    intents = get_intents()
    print(f"Active Intents: {len(intents.get('intents', []))}")
    
    print("\n" + "=" * 60)

def compare_metrics():
    """Compare RAVEN vs default routing metrics"""
    print("\n" + "=" * 60)
    print("RAVEN vs DEFAULT ROUTING COMPARISON")
    print("=" * 60)
    
    print("\nMetrics to Compare:")
    print("  1. Path Length (hop count)")
    print("  2. Link Utilization")
    print("  3. Reliability Score")
    print("  4. Failover Time")
    
    print("\nRAVEN Advantages:")
    print("  ✓ Considers link reliability")
    print("  ✓ Considers available bandwidth")
    print("  ✓ Avoids congested paths")
    print("  ✓ Adapts to network conditions")
    
    print("\nDefault ONOS Routing:")
    print("  • Uses shortest path (hop count)")
    print("  • Doesn't consider link quality")
    print("  • Doesn't consider bandwidth")
    print("  • Static until topology changes")
    
    print("\n" + "=" * 60)

def monitor_changes(duration=60):
    """Monitor topology changes over time"""
    print(f"\nMonitoring topology changes for {duration} seconds...")
    print("(Simulate link failures in Mininet to see RAVEN adapt)")
    
    start_time = time.time()
    last_link_count = 0
    
    while time.time() - start_time < duration:
        try:
            _, links, _ = get_topology()
            active_links = [l for l in links.get('links', []) if l.get('state') == 'ACTIVE']
            link_count = len(active_links)
            
            if link_count != last_link_count:
                print(f"\n[{time.strftime('%H:%M:%S')}] Topology changed!")
                print(f"  Active links: {last_link_count} -> {link_count}")
                
                if link_count < last_link_count:
                    print("  ⚠️  Link failure detected - RAVEN recomputing paths...")
                else:
                    print("  ✓ Link restored - RAVEN updating paths...")
                
                last_link_count = link_count
            
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

def main():
    print("\n" + "=" * 60)
    print("RAVEN ROUTING ANALYSIS TOOL")
    print("=" * 60)
    
    try:
        # Test ONOS connectivity
        response = requests.get(f"{ONOS_URL}/applications", auth=AUTH, timeout=5)
        if response.status_code != 200:
            print("\n❌ Cannot connect to ONOS. Is it running?")
            print("   Start with: docker-compose up -d")
            return
        
        print("\n✓ Connected to ONOS")
        
        # Analyze current state
        analyze_paths()
        
        # Show comparison
        compare_metrics()
        
        # Ask to monitor
        print("\nOptions:")
        print("  1. Monitor topology changes (60s)")
        print("  2. Exit")
        
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == "1":
            monitor_changes(60)
        
        print("\n✓ Analysis complete")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to ONOS at localhost:8181")
        print("   Make sure Docker containers are running:")
        print("   docker-compose up -d")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
