from tcp_base import TcpEventBased
import time
import pandas as pd
import math

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2018, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"
import sys
sys.stdout = open('hybrid_log.txt', 'w')

class TcpHybridCubic(TcpEventBased):
    """Hybrid TCP CUBIC Implementation with Delay and Bandwidth Awareness"""
    def __init__(self):
        super(TcpHybridCubic, self).__init__()
        
        # Core CUBIC parameters
        self.C = 0.4
        self.beta = 0.2
        self.epoch_start = 0
        self.w_max = 0
        self.k = 0
        self.curr_cwnd = 1
        self.origin_point = 0
        self.ack_cnt = 0
        self.cwnd_cnt = 0
        
        # Delay-based parameters
        self.delay_factor = 0.5
        self.rtt_threshold = 1.2
        self.min_rtt = float('inf')
        self.current_rtt = 0
        
        # BBR-like parameters
        self.max_bw = 0
        self.pacing_gain = 1.25
        self.cwnd_gain = 2.0
        self.cycle_index = 0
        
        # Hybrid control parameters
        self.fast_convergence = True
        self.tcp_friendliness = False
        self.W_tcp = 0
        
        # Logging
        self.df = pd.DataFrame(columns=[
            'ssThresh', 'cWnd', 'segmentsAcked', 'segmentSize',
            'bytesInFlight', 'caState', 'caEvent', 'loss',
            'current_rtt', 'min_rtt', 'max_bw', 'hybrid_target'
        ])

    def _cubic_window(self, t_us):
        """CUBIC window calculation"""
        t = (t_us - self.epoch_start) / 1e6
        return self.C * (t - self.k)**3 + self.w_max

    def _is_congestion_detected(self, caState):
        """Hybrid congestion detection"""
        return (caState == 3) or \
               (self.current_rtt > self.rtt_threshold * self.min_rtt)

    def _hybrid_congestion_response(self, simTime_us, cWnd):
        """Combined response to congestion"""
        # CUBIC response
        self.w_max = cWnd
        self.epoch_start = simTime_us
        self.k = ((self.w_max * (1 - self.beta)) / self.C) ** (1/3)
        
        # BBR-like response
        self.max_bw *= 0.85
        self.min_rtt = float('inf')
        
        # Fast convergence
        if self.fast_convergence and cWnd < self.w_max:
            self.w_max = cWnd * (2 - self.beta) / 2

    def _calculate_hybrid_target(self, simTime_us, cWnd, segmentSize):
        """Combined window target calculation"""
        # CUBIC target
        cubic_target = self._cubic_window(simTime_us)
        # cubic_target=1e9
        
        # BBR-like target
        if self.min_rtt > 0:
            bbr_target = (self.max_bw * self.min_rtt * self.cwnd_gain) / segmentSize
        else:
            bbr_target = float('inf')
        
        # Hybrid target selection
        hybrid_target = min(cubic_target, bbr_target)
        #hybrid_target=bbr_target
        
        # Delay-based backoff
        if self.current_rtt > self.rtt_threshold * self.min_rtt:
            hybrid_target *= (1 - self.delay_factor)
        
        return max(hybrid_target, 2)

    def get_action(self, obs, reward, done, info):
        socketUuid = obs[0]
        envType = obs[1]
        simTime_us = obs[2]
        nodeId = obs[3]
        ssThresh = obs[4]
        cWnd = obs[5]
        segmentSize = obs[6]
        segmentsAcked = obs[7]
        bytesInFlight = obs[8]
        current_rtt = obs[9]
        caState = obs[12]
        caEvent = obs[13]

        # Update RTT measurements
        self.current_rtt = current_rtt
        self.min_rtt = min(self.min_rtt, current_rtt)
        
        # Update bandwidth estimation
        if current_rtt > 0:
            current_bw = (cWnd * segmentSize) / current_rtt
            self.max_bw = max(self.max_bw, current_bw)

        # Detect and handle congestion
        if self._is_congestion_detected(caState):
            self._hybrid_congestion_response(simTime_us, cWnd)
            new_ssThresh = max(int(self.beta * cWnd), 2 * segmentSize)
            new_cWnd = new_ssThresh
            return [new_ssThresh, new_cWnd]

        # Slow start phase
        if cWnd < ssThresh:
            if segmentsAcked >= 1:
                new_cWnd = cWnd + segmentSize * int(self.pacing_gain)
            return [ssThresh, new_cWnd]

        # Congestion avoidance - hybrid window adjustment
        hybrid_target = self._calculate_hybrid_target(simTime_us, cWnd, segmentSize)
        
        # Window growth calculation
        if hybrid_target > cWnd:
            cnt = cWnd / (hybrid_target - cWnd)
        else:
            cnt = 100 * cWnd
        
        # Apply window update
        self.cwnd_cnt += segmentsAcked
        if self.cwnd_cnt > cnt:
            new_cWnd = cWnd + segmentSize
            self.cwnd_cnt = 0
        else:
            new_cWnd = cWnd

        # Logging
        self.df.loc[len(self.df)] = [
            ssThresh, cWnd, segmentsAcked, segmentSize,
            bytesInFlight, caState, caEvent, 0,
            self.current_rtt, self.min_rtt, self.max_bw, hybrid_target
        ]

        return [ssThresh, new_cWnd]