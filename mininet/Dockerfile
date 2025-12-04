FROM iwaseyusuke/mininet:latest

# Install pip and additional Python packages
RUN apt-get update && apt-get install -y \
    python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --no-cache-dir \
    requests \
    flask

# Create topologies directory
RUN mkdir -p /topologies

WORKDIR /topologies

# Start OVS on container start
CMD service openvswitch-switch start && /bin/bash
