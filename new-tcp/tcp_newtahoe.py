from tcp_base import TcpEventBased

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2018, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


import sys
import os
from datetime import datetime

# Create logs/ directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Create a timestamped log file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_path = os.path.join("logs", f"sim_log_{timestamp}.txt")

# Redirect print output to both console and file
class Logger:
    def __init__(self, file_path):
        self.terminal = sys.stdout
        self.log = open(file_path, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = Logger(log_file_path)



class TcpTahoe(TcpEventBased):
    """docstring for TcpNewReno"""
    def __init__(self):
        super(TcpTahoe, self).__init__()
   
    def get_action(self, obs, reward, done, info):
        # unique socket ID
        socketUuid = obs[0]
        # TCP env type: event-based = 0 / time-based = 1
        envType = obs[1]
        # sim time in us
        simTime_us = obs[2]
        # unique node ID
        nodeId = obs[3]
        # current ssThreshold
        ssThresh = obs[4]
        # current contention window size
        cWnd = obs[5]
        # segment size
        segmentSize = obs[6]
        # number of acked segments
        segmentsAcked = obs[7]
        # estimated bytes in flight
        bytesInFlight  = obs[8]
        caState = obs[12]
        caEvent = obs[13]

        new_cWnd = 1
        new_ssThresh = 1

        if caEvent == 2:  # CA_EVENT_LOSS
            print("-------------------------------------------------loss--------------------------------------------------------")
            new_ssThresh = segmentSize
            new_cWnd = segmentSize  # Reset to 1 segment (slow start)


        # IncreaseWindow
        elif (cWnd < ssThresh):
            # slow start
            if (segmentsAcked >= 1):
                new_cWnd = cWnd + segmentSize


        elif (cWnd >= ssThresh):
            # congestion avoidance
            if (segmentsAcked > 0):
                adder = 1.0 * (segmentSize * segmentSize) / cWnd;
                adder = int(max (1.0, adder))
                new_cWnd = cWnd + adder


        # GetSsThresh
        new_ssThresh = int(max (2 * segmentSize, bytesInFlight / 2))
        # new_ssThresh = segmentSize

        # return actions
        actions = [new_ssThresh, new_cWnd]

        return actions


        
