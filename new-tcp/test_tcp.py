#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from ns3gym import ns3env
from tcp_base import TcpTimeBased
import matplotlib.pyplot as plt


from tcp_cubic import TcpCubic
from tcp_cubic_with_loss_predictor import TcpCubicLP
from tcp_hybrid_cubic_bbr import TcpHybridCubic
from tcp_newreno import TcpNewReno
from tcp_newtahoe import TcpTahoe



__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2018, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


parser = argparse.ArgumentParser(description='Start simulation script on/off')
parser.add_argument('--start',
                    type=int,
                    default=1,
                    help='Start ns-3 simulation script 0/1, Default: 1')
parser.add_argument('--iterations',
                    type=int,
                    default=1,
                    help='Number of iterations, Default: 1')

args = parser.parse_args()
startSim = bool(args.start)
iterationNum = int(args.iterations)

port = 5555
simTime = 50 # seconds
stepTime = 0.5  # seconds
seed = 12
simArgs = {"--duration": simTime,}
debug = False

env = ns3env.Ns3Env(port=port, stepTime=stepTime, startSim=startSim, simSeed=seed, simArgs=simArgs, debug=debug)
# simpler:
#env = ns3env.Ns3Env()
env.reset()

ob_space = env.observation_space
ac_space = env.action_space
print("Observation space: ", ob_space,  ob_space.dtype)
print("Action space: ", ac_space, ac_space.dtype)

stepIdx = 0
currIt = 0

def get_agent(obs):
    socketUuid = obs[0]
    tcpEnvType = obs[1]
    tcpAgent = get_agent.tcpAgents.get(socketUuid, None)
    if tcpAgent is None:
        if tcpEnvType == 0:
            # event-based = 0
            tcpAgent = TcpNewReno()
            # tcpAgent = TcpHybridCubic()
            # tcpAgent = TcpCubic()
            # tcpAgent=TcpTahoe()
            # tcpAgent=TcpCubicLP()
        else:
            # time-based = 1
            tcpAgent = TcpTimeBased()
        tcpAgent.set_spaces(get_agent.ob_space, get_agent.ac_space)
        get_agent.tcpAgents[socketUuid] = tcpAgent

    return tcpAgent

# initialize variable
# get_agent.tcpAgents, get_agent.ob_space, and get_agent.ac_space are attributes assigned directly to the function object.

# These behave like static variables inside the function scope.
get_agent.tcpAgents = {}
get_agent.ob_space = ob_space
get_agent.ac_space = ac_space



rewardsum = 0
rew_history = []
cWnd_history = []
pred_cWnd_history = []
rtt_history = []
tp_history = []


try:
    while True:
        print("Start iteration: ", currIt)
        obs = env.reset()
        reward = 0
        done = False
        info = None
        print("Step: ", stepIdx)
        print("---obs: ", obs)

        # get existing agent of create new TCP agent if needed, obs[1] is set to 0 in GetObservation() in tcp-rl-env.cc- for chosing TcpNewReno()
        tcpAgent = get_agent(obs)

        while True:
            stepIdx += 1
            action = tcpAgent.get_action(obs, reward, done, info)
            print("---action: ", action)

            print("Step: ", stepIdx)
            obs, reward, done, info = env.step(action)
            print("---obs, reward, done, info: ", obs, reward, done, info)

            
            next_state = obs[4:]
            cWnd = next_state[1]
            rtt=next_state[5]
            min_rtt=next_state[6]
            tp=next_state[11]
            rewardsum += reward
            cWnd_history.append(cWnd)
            rtt_history.append(rtt)
            tp_history.append(tp)
            rew_history.append(rewardsum)
            print("-----------------------tp---------------------",tp)
            


            # get existing agent of create new TCP agent if needed
            tcpAgent = get_agent(obs)

            if done:
                stepIdx = 0
                if currIt + 1 < iterationNum:
                    env.reset()
                break

        currIt += 1
        if currIt == iterationNum:
            break
    
    
    
    window_size = 5
    tp_moving_avg = [sum(tp_history[i:i+window_size])/window_size 
                 for i in range(len(tp_history)-window_size+1)]



    fig, ax = plt.subplots(2, 2, figsize=(14, 10))  # larger size
    fig.suptitle("TCP RL Agent Training Metrics", fontsize=16, y=1.02)  # optional main title

    tcpAgent.df.to_csv('samples.csv')

    # Fine-tune layout spacing
    plt.tight_layout(pad=4.0)
    plt.subplots_adjust(top=0.93, hspace=0.4, wspace=0.3)  # top to prevent title cut-off

    # Plotting
    ax[0, 0].plot(cWnd_history, linestyle="-")
    ax[0, 0].set_title('Congestion Window')
    ax[0, 0].set_xlabel('Steps')
    ax[0, 0].set_ylabel('CWND (segments)')

    ax[1, 0].plot(rtt_history, linestyle="-")
    ax[1, 0].set_title('RTT Over Time')
    ax[1, 0].set_xlabel('Steps')
    ax[1, 0].set_ylabel('RTT (μs)')

   

    ax[0, 1].plot(rew_history, linestyle="-")
    ax[0, 1].set_title('Cumulative Reward')
    ax[0, 1].set_xlabel('Steps')
    ax[0, 1].set_ylabel('Accumulated Reward')

    ax[1, 1].plot(tp_history, linestyle="-")
    ax[1, 1].set_title('Throughput Over Time')
    ax[1, 1].set_xlabel('Steps')
    ax[1, 1].set_ylabel('Throughput (bits)')
    # ax[0, 1].set_yscale('log')
    ax[1, 1].set_ylim(bottom=1e6,top=3e6)  # Start from 1 Mbps



    plt.savefig('plot.png', bbox_inches='tight')

    plt.show()


except KeyboardInterrupt:
    print("Ctrl-C -> Exit")
finally:
    env.close()
    print("Done")