# #!/bin/bash

# # Create folder for traces if not exists
# mkdir -p traces
# sudo sysctl -w net.ipv4.tcp_congestion_control="tahoe"
# # Replace 'lo' with your correct interface if needed (like eth0, wlan0)
# DURATION=15

# # Start tcpdump with timeout to avoid hanging
# curl -s http://localhost > /dev/null &
# echo "Starting tcpdump for $DURATION seconds..."
# sudo timeout $DURATION tcpdump -i lo -w traces/tahoe.pcap tcp

# echo "Capture saved to traces/TAHOE.pcap"


#!/bin/bash

# Set the congestion control algorithm (change to 'reno', 'tahoe', etc. as needed)
ALGO="tahoe"

# Create folder for traces if it doesn't exist
mkdir -p traces

# Set congestion control
echo "Setting TCP congestion control to $ALGO"
sudo sysctl -w net.ipv4.tcp_congestion_control="$ALGO"

# Capture duration
DURATION=15

# Start some traffic (replace with your real traffic pattern if needed)
curl -s http://localhost > /dev/null &

echo "Starting tcpdump for $DURATION seconds..."
# sudo timeout $DURATION tcpdump -i lo -w "traces/${ALGO}.pcap" tcp
sudo timeout $DURATION tcpdump -s 96 -i lo -w "traces/${ALGO}.pcap" tcp

echo "Capture saved to traces/${ALGO}.pcap"
