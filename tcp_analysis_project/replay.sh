#!/bin/bash

ALG=$1  # reno, cubic, tahoe
RECORD_DIR=~/recordings/test
PCAP_FILE=traces/${ALG}.pcap

# Set TCP algorithm
sudo sysctl -w net.ipv4.tcp_congestion_control=$ALG

# Clean any old captures
rm -f $PCAP_FILE

# Run test and capture packets
sudo tcpdump -i lo -w $PCAP_FILE tcp &

# Capture PID of tcpdump to kill later
TCPDUMP_PID=$!

# Replay in simulated network
mm-delay 100 mm-link 5mbps 1mbps mm-webreplay $RECORD_DIR firefox http://127.0.0.1

# Wait for user to close Firefox
sleep 5
sudo kill $TCPDUMP_PID
