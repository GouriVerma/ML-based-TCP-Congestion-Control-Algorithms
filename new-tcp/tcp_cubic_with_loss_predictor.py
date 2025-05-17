


from tcp_base import TcpEventBased
import time
import pandas as pd
import joblib
import numpy as np

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2018, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"
import sys
sys.stdout = open('my_log_file.txt', 'w')



class TcpCubicLP(TcpEventBased):
    """TCP CUBIC Implementation"""
    def __init__(self):
        super(TcpCubicLP, self).__init__()
        # CUBIC parameters
        self.C = 0.4          # Cubic scaling factor
        self.beta = 0.2      # Multiplicative decrease factor
        self.epoch_start = 0  # Time of last congestion event (microseconds)
        self.w_max = 0        # Window size before last congestion
        self.K = 0            # Time offset for cubic function
        self.curr_cwnd = 1    # Track current cWnd between calls
        self.origin_point = 0
        self.ack_cnt=0
        # self.cnt=0
        self.dMin=0
        self.cwnd_cnt=0
        self.fast_convergence=True
        self.tcp_friendliness=False # True to activate
        self.W_tcp=0
        self.df=pd.DataFrame(columns=['ssThresh','cWnd','segmentsAcked','segmentSize','bytesInFlight','caState','caEvent','loss'])
        self.lp = joblib.load("trained_random_forest.joblib")
        self.loss_threshold=0.95

    

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
        caState=obs[12]
        caEvent=obs[13]

        # Track current cWnd between calls
        self.curr_cwnd = cWnd
        new_cWnd = 1
        new_ssThresh = 1


        ############################### Prediction ######################################
        features = [ssThresh,cWnd,segmentsAcked,segmentSize,bytesInFlight,caState,caEvent] # Adjust indices as per your model's input features
        feature_names = ['ssThresh', 'cWnd', 'segmentsAcked', 'segmentSize', 'bytesInFlight', 'caState', 'caEvent']
        features_df = pd.DataFrame([features], columns=feature_names)
        loss_prob = self.lp.predict_proba(features_df)[0][1]
        # loss_prob = self.lp.predict_proba(features)[0][1]
        if loss_prob > self.loss_threshold:
            new_cWnd = max(1, cWnd - 1)
            new_ssThresh = ssThresh
            print(f"NN predicts loss: {loss_prob:.2f} > {self.loss_threshold}, cwnd reduced to {new_cWnd}")
            return [new_cWnd, new_ssThresh]




        ###################################################################################

        

        print('----------------------------------caEvent@',caEvent,'-----------------------------------------------')
        print('----------------------------------caState@',caState,'-----------------------------------------------')

        if caState == 3:  # TCP_CA_LOSS
            self.df.loc[len(self.df)]=[ssThresh,cWnd,segmentsAcked,segmentSize,bytesInFlight,caState,caEvent,1]

        # Multiplicative decrease
            new_ssThresh = max(int(self.beta * cWnd), 2 * segmentSize)
            new_cWnd = new_ssThresh
            
            # Fast convergence
            if self.fast_convergence and cWnd < self.w_max:
                self.w_max = cWnd * (2 - self.beta) / 2
            else:
                self.w_max = cWnd
            
            # Reset epoch
            self.epoch_start = simTime_us
            self.K = ((self.w_max * (1 - self.beta)) / self.C) ** (1/3)
            self.origin_point = self.w_max
            self.ack_cnt = 0
            
            return [new_cWnd, new_ssThresh]
        
        self.df.loc[len(self.df)]=[ssThresh,cWnd,segmentsAcked,segmentSize,bytesInFlight,caState,caEvent,0]


        # Update minimum RTT
        if self.dMin == 0:
            self.dMin = obs[9]  # RTT
        else:
            self.dMin = min(self.dMin, obs[9])
        



 
        
       # IncreaseWindow
        if (cWnd < ssThresh):
            # slow start
            if (segmentsAcked >= 1):
                new_cWnd = cWnd + segmentSize
            new_ssThresh = ssThresh
            return [new_ssThresh, new_cWnd]
        



        # Congestion avoidance phase
        t = (simTime_us - self.epoch_start) / 1e6  # Convert to seconds
        
        # Calculate target window 
        # if cWnd < self.w_max:
        #     target = self.origin_point + self.C * (t - self.K)**3
        # else:
        #     target = cWnd + self.C * (t**3) # by passed w_max, again concave increase
        target = self.origin_point + self.C * (t - self.K)**3

        # Calculate window growth rate
        if target > cWnd:
            cnt = cWnd / (target - cWnd)
        else:
            cnt = 100 * cWnd # to make growth very slow
        

        # TCP Friendliness 
        if self.tcp_friendliness:
            self.W_tcp += (3 * self.beta) / (2 - self.beta) * self.ack_cnt / cWnd
            self.ack_cnt = 0
            tcp_cnt = cWnd / (self.W_tcp - cWnd) if self.W_tcp > cWnd else 0
            cnt = min(cnt, tcp_cnt)
        

        # Update window
        self.cwnd_cnt += segmentsAcked
        if self.cwnd_cnt > cnt:
            new_cWnd = cWnd + segmentSize
            self.cwnd_cnt = 0
        else:
            new_cWnd = cWnd
        

        self.ack_cnt += segmentsAcked


        

        # Ensure minimum window size
        new_cWnd = max(new_cWnd, segmentSize)
        new_ssThresh = max(new_ssThresh, 2 * segmentSize)

        return [new_ssThresh, new_cWnd]