# Routing Algorithm Comparison

## Overview of Path Selection Methods

This document compares different path selection algorithms you can implement in your ONOS + Mininet + RAVEN setup.

## Comparison Table

| Algorithm                    | Metric                  | Pros                   | Cons                    | Use Case                  |
| ---------------------------- | ----------------------- | ---------------------- | ----------------------- | ------------------------- |
| **RAVEN**                    | Reliability + Bandwidth | Multi-metric, adaptive | Complex, overhead       | Mission-critical networks |
| **Shortest Path (Dijkstra)** | Hop count               | Simple, fast           | Ignores quality         | Basic routing             |
| **Widest Path**              | Max bandwidth           | Good for bulk transfer | Ignores reliability     | Data centers              |
| **Minimum Latency**          | Delay                   | Low latency            | May use congested links | Real-time apps            |
| **Load Balancing**           | Link utilization        | Distributes traffic    | Complex state           | High-traffic networks     |
| **K-Shortest Paths**         | Multiple paths          | Redundancy             | More overhead           | Fault tolerance           |
| **Max Reliability**          | Link uptime             | Stable paths           | May be slow             | Critical services         |

## Detailed Comparison

### 1. RAVEN (Reliability-Aware Virtual Network Embedding)

**Formula:**

```
Score = α × Reliability + β × Bandwidth - γ × HopCount
```

**Implementation:**

```python
def compute_raven_score(self, path, alpha=0.6, beta=0.4):
    reliability = self.compute_path_reliability(path)
    bandwidth = self.compute_path_bandwidth(path)
    hop_count = len(path) - 1

    normalized_bandwidth = bandwidth / 100.0
    hop_penalty = hop_count * 0.1

    return (alpha * reliability) + (beta * normalized_bandwidth) - hop_penalty
```

**Pros:**

- ✅ Considers multiple metrics
- ✅ Adapts to network conditions
- ✅ Balances reliability and performance
- ✅ Configurable weights

**Cons:**

- ❌ More complex computation
- ❌ Requires metric tracking
- ❌ Higher overhead

**Best For:**

- Mission-critical applications
- Networks with varying link quality
- When both reliability and performance matter

---

### 2. Shortest Path (Dijkstra)

**Formula:**

```
Minimize: Σ hop_count
```

**Implementation:**

```python
def find_shortest_path(self, src, dst):
    return nx.shortest_path(self.topology, src, dst)
```

**Pros:**

- ✅ Very simple
- ✅ Fast computation
- ✅ Well-understood
- ✅ Low overhead

**Cons:**

- ❌ Ignores link quality
- ❌ Ignores bandwidth
- ❌ May choose congested paths
- ❌ Not adaptive

**Best For:**

- Simple networks
- When all links are similar quality
- Low-latency requirements
- Default routing

---

### 3. Widest Path (Maximum Bandwidth)

**Formula:**

```
Maximize: min(bandwidth) along path
```

**Implementation:**

```python
def find_widest_path(self, src, dst):
    # Invert bandwidth for shortest path algorithm
    for u, v, data in self.topology.edges(data=True):
        data['weight'] = 1.0 / data.get('bandwidth', 1.0)

    return nx.shortest_path(self.topology, src, dst, weight='weight')
```

**Pros:**

- ✅ Maximizes throughput
- ✅ Good for bulk transfers
- ✅ Avoids bottlenecks

**Cons:**

- ❌ May choose longer paths
- ❌ Ignores reliability
- ❌ Can cause congestion

**Best For:**

- Data center networks
- Large file transfers
- Video streaming
- Backup operations

---

### 4. Minimum Latency

**Formula:**

```
Minimize: Σ link_delay
```

**Implementation:**

```python
def find_min_latency_path(self, src, dst):
    return nx.shortest_path(self.topology, src, dst,
                           weight=lambda u,v,d: d.get('latency', 1))
```

**Pros:**

- ✅ Lowest delay
- ✅ Good for real-time apps
- ✅ Predictable performance

**Cons:**

- ❌ May use congested links
- ❌ Ignores bandwidth
- ❌ May be unreliable

**Best For:**

- VoIP applications
- Online gaming
- Video conferencing
- Trading systems

---

### 5. Load Balancing (ECMP-like)

**Formula:**

```
Distribute traffic across multiple equal-cost paths
```

**Implementation:**

```python
def find_load_balanced_paths(self, src, dst, k=3):
    # Find k shortest paths
    paths = list(nx.shortest_simple_paths(self.topology, src, dst))[:k]

    # Distribute flows round-robin
    return paths

def select_path_for_flow(self, flow_id, paths):
    return paths[flow_id % len(paths)]
```

**Pros:**

- ✅ Distributes load
- ✅ Prevents congestion
- ✅ Better utilization
- ✅ Fault tolerance

**Cons:**

- ❌ Complex state management
- ❌ Packet reordering possible
- ❌ More flow rules needed

**Best For:**

- High-traffic networks
- Data centers
- When multiple equal paths exist
- Load distribution

---

### 6. K-Shortest Paths

**Formula:**

```
Find k paths with minimum cost
```

**Implementation:**

```python
def find_k_shortest_paths(self, src, dst, k=3):
    return list(nx.shortest_simple_paths(self.topology, src, dst))[:k]
```

**Pros:**

- ✅ Multiple path options
- ✅ Fast failover
- ✅ Redundancy
- ✅ Can choose based on conditions

**Cons:**

- ❌ More computation
- ❌ More memory
- ❌ Need selection criteria

**Best For:**

- Fault-tolerant networks
- When backup paths needed
- Dynamic path selection
- Resilient routing

---

### 7. Maximum Reliability

**Formula:**

```
Maximize: Π link_reliability
```

**Implementation:**

```python
def find_max_reliability_path(self, src, dst):
    # Use negative log of reliability as weight
    for u, v, data in self.topology.edges(data=True):
        reliability = data.get('reliability', 1.0)
        data['weight'] = -math.log(reliability) if reliability > 0 else float('inf')

    return nx.shortest_path(self.topology, src, dst, weight='weight')
```

**Pros:**

- ✅ Most stable paths
- ✅ Fewer failures
- ✅ Predictable
- ✅ Good for critical services

**Cons:**

- ❌ May be slower
- ❌ May have lower bandwidth
- ❌ Requires reliability tracking

**Best For:**

- Critical infrastructure
- Financial transactions
- Healthcare systems
- Safety-critical applications

---

## Performance Comparison

### Scenario: 10-node network, 2 paths available

**Path A:** 3 hops, 100 Mbps, 95% reliable, 10ms latency
**Path B:** 2 hops, 50 Mbps, 70% reliable, 5ms latency

| Algorithm            | Selected Path | Reason                         |
| -------------------- | ------------- | ------------------------------ |
| RAVEN (α=0.6, β=0.4) | Path A        | Better reliability + bandwidth |
| Shortest Path        | Path B        | Fewer hops                     |
| Widest Path          | Path A        | Higher bandwidth               |
| Min Latency          | Path B        | Lower delay                    |
| Max Reliability      | Path A        | Higher reliability             |

---

## Computational Complexity

| Algorithm       | Time Complexity | Space Complexity | Notes                 |
| --------------- | --------------- | ---------------- | --------------------- |
| RAVEN           | O(k × E log V)  | O(V + E)         | k paths evaluated     |
| Shortest Path   | O(E log V)      | O(V + E)         | Dijkstra's algorithm  |
| Widest Path     | O(E log V)      | O(V + E)         | Modified Dijkstra     |
| Min Latency     | O(E log V)      | O(V + E)         | Dijkstra with weights |
| Load Balancing  | O(k × E log V)  | O(k × V)         | k paths stored        |
| K-Shortest      | O(k × E log V)  | O(k × V)         | Yen's algorithm       |
| Max Reliability | O(E log V)      | O(V + E)         | Modified Dijkstra     |

Where:

- V = number of vertices (switches/hosts)
- E = number of edges (links)
- k = number of paths considered

---

## Implementation Guide

### Switching Between Algorithms

Edit `raven-controller/raven_controller.py`:

```python
def monitor_and_update(self):
    # ... topology fetching code ...

    for src in host_nodes:
        for dst in host_nodes[i+1:]:
            # Choose your algorithm:

            # Option 1: RAVEN (default)
            best_path = self.find_best_path_raven(src, dst)

            # Option 2: Shortest Path
            # best_path = nx.shortest_path(self.topology, src, dst)

            # Option 3: Widest Path
            # best_path = self.find_widest_path(src, dst)

            # Option 4: Min Latency
            # best_path = self.find_min_latency_path(src, dst)

            # Option 5: Max Reliability
            # best_path = self.find_max_reliability_path(src, dst)

            # Option 6: Load Balancing
            # paths = self.find_k_shortest_paths(src, dst, k=3)
            # best_path = self.select_path_round_robin(paths)
```

### Adding Custom Metrics

```python
class RAVENController:
    def __init__(self):
        # ... existing code ...
        self.link_latency = {}      # Track latency
        self.link_jitter = {}       # Track jitter
        self.link_loss = {}         # Track packet loss
        self.link_utilization = {}  # Track usage

    def compute_custom_score(self, path):
        """Custom scoring function"""
        reliability = self.compute_path_reliability(path)
        bandwidth = self.compute_path_bandwidth(path)
        latency = self.compute_path_latency(path)
        loss = self.compute_path_loss(path)

        # Weighted combination
        score = (0.3 * reliability +
                0.3 * bandwidth -
                0.2 * latency -
                0.2 * loss)

        return score
```

---

## Hybrid Approaches

### RAVEN + Load Balancing

```python
def find_best_paths_raven_lb(self, src, dst, k=3):
    """Find k best paths using RAVEN, then load balance"""
    paths = list(nx.shortest_simple_paths(self.topology, src, dst))[:k*2]

    # Score all paths
    scored_paths = [(p, self.compute_raven_score(p)) for p in paths]
    scored_paths.sort(key=lambda x: x[1], reverse=True)

    # Return top k paths for load balancing
    return [p for p, score in scored_paths[:k]]
```

### Adaptive Algorithm Selection

```python
def select_algorithm_adaptive(self, src, dst, traffic_type):
    """Choose algorithm based on traffic type"""
    if traffic_type == 'video':
        return self.find_widest_path(src, dst)
    elif traffic_type == 'voip':
        return self.find_min_latency_path(src, dst)
    elif traffic_type == 'critical':
        return self.find_max_reliability_path(src, dst)
    else:
        return self.find_best_path_raven(src, dst)
```

---

## Testing Different Algorithms

### Benchmark Script

```python
import time

def benchmark_algorithms(controller, src, dst):
    """Compare algorithm performance"""

    algorithms = {
        'RAVEN': lambda: controller.find_best_path_raven(src, dst),
        'Shortest': lambda: nx.shortest_path(controller.topology, src, dst),
        'Widest': lambda: controller.find_widest_path(src, dst),
        'Min Latency': lambda: controller.find_min_latency_path(src, dst),
    }

    results = {}
    for name, algo in algorithms.items():
        start = time.time()
        path = algo()
        duration = time.time() - start

        results[name] = {
            'path': path,
            'time': duration,
            'hops': len(path) - 1,
            'score': controller.compute_raven_score(path)
        }

    return results
```

---

## Recommendations

### For Different Network Types

**Enterprise Network:**

- Use: RAVEN or Shortest Path
- Why: Balance reliability and simplicity

**Data Center:**

- Use: Load Balancing or Widest Path
- Why: Maximize throughput and utilization

**ISP Network:**

- Use: K-Shortest Paths with RAVEN scoring
- Why: Redundancy and quality

**IoT Network:**

- Use: Max Reliability
- Why: Devices may have unreliable links

**Real-Time Applications:**

- Use: Min Latency
- Why: Delay-sensitive traffic

**Mission-Critical:**

- Use: RAVEN with high reliability weight
- Why: Stability is paramount

---

## Conclusion

Each algorithm has trade-offs. Choose based on:

1. **Network characteristics** - Link quality, topology
2. **Traffic requirements** - Latency, bandwidth, reliability
3. **Computational resources** - Available processing power
4. **Operational complexity** - Management overhead

**RAVEN provides a good balance** for most scenarios, but you can easily switch or combine algorithms based on your needs.
