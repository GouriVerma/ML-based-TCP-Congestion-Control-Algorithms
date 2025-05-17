
# NS3 GYM- TCP Congestion Control Algorithms 

## Setup NS3

We recommend using Linux (e.g. Ubuntu 22 or higher).

Install all dependencies required by ns-3.

    # minimal requirements for C++:
    apt-get install gcc g++ python3 python3-pip cmake

Check ns-3 requirements

Install ZMQ, Protocol Buffers and pkg-config libs:

    sudo apt-get update
    apt-get install libzmq5 libzmq3-dev
    apt-get install libprotobuf-dev
    apt-get install protobuf-compiler
    apt-get install pkg-config

Download and install ns3

    wget https://www.nsnam.org/releases/ns-allinone-3.40.tar.bz2
    tar xf ns-allinone-3.40.tar.bz2
    cd ns-allinone-3.40

Clone ns3-gym repository into contrib directory and change the branch:

    cd ./ns-3.40/contrib
    git clone https://github.com/tkn-tub/ns3-gym.git ./opengym
    cd opengym/
    git checkout app-ns-3.36+

Check working with cmake

It is important to use the opengym as the name of the ns3-gym app directory.

Configure and build ns-3 project:

    cd ../../
    ./ns3 configure --enable-examples
    ./ns3 build

Note: Opengym Protocol Buffer messages (C++ and Python) are build during configure.

Install ns3gym located in model/ns3gym (Python3 required)

    cd ./contrib/opengym/

    pip3 install --user ./model/ns3gym

    or
In CMakeLists.txt of opengym/examples folder:
Add this for TCP Reno, Cunic, Tahoe, Hybrid:

    build_lib_example(
        NAME new-tcp
        SOURCE_FILES new-tcp/sim.cc
                    new-tcp/tcp-rl-env.cc
                    new-tcp/tcp-rl.cc
        LIBRARIES_TO_LINK
        ${libapplications}
        ${libcore}
        ${libflow-monitor}
        ${libinternet}
        ${libopengym}
        ${libpoint-to-point-layout}
        ${libptp}
    )

Add this for TCP RL:

    build_lib_example(
            NAME new-tcp
            SOURCE_FILES new-rl-tcp/sim.cc
                        new-rl-tcp/tcp-rl-env.cc
                        new-rl-tcp/tcp-rl.cc
            LIBRARIES_TO_LINK
            ${libapplications}
            ${libcore}
            ${libflow-monitor}
            ${libinternet}
            ${libopengym}
            ${libpoint-to-point-layout}
            ${libptp}
        )

Set up python environment

    python3 -m venv ns3gym-venv
    source ./ns3gym-venv/bin/activate
    pip3 install ./model/ns3gym

Install all libraries required by your agent (like tensorflow, keras, matplotlib etc.).

<br />

# Steps for Running
## 1. Add new-tcp and new-rl-tcp Folders in opengym examples


## 2. Run Tahoe, Cubic, Reno, Hybrid Cubic-BBR:

1. Run directly in one terminal

        cd ./contrib/opengym/examples/new-tcp/ 
        ./test_tcp.py

2. Alternative Way to Run<br/>
Start ns-3 simulation script and Gym agent separately in two terminals (useful for debugging):

#### Terminal 1
In ns-3.40 folder

    ./ns3 run "new-tcp --transport_prot=TcpRl"

#### Terminal 2

    cd ./contrib/opengym/examples/new-tcp/ 
    ./test_tcp.py --start=0

### 3. To configure for different Models

Update in test_tcp.py. The following tcpAgent is used to select the algorithm

    def get_agent(obs):
        socketUuid = obs[0]
        tcpEnvType = obs[1]
        tcpAgent = get_agent.tcpAgents.get(socketUuid, None)
        if tcpAgent is None:
            if tcpEnvType == 0:
                # event-based = 0
                # tcpAgent = TcpNewReno()
                # tcpAgent = TcpHybridCubic()
                # tcpAgent = TcpCubic()
                # tcpAgent=TcpTahoe()
                tcpAgent=TcpCubicLP()
            else:
                # time-based = 1
                tcpAgent = TcpTimeBased()
            tcpAgent.set_spaces(get_agent.ob_space, get_agent.ac_space)
            get_agent.tcpAgents[socketUuid] = tcpAgent

        return tcpAgent


### 4. Run TCP RL

1. Run directly in one terminal

        cd ./contrib/opengym/examples/new-rl-tcp/ 
        ./TCP-RL-Agent.py

2. Alternative Way to Run<br/>
Start ns-3 simulation script and Gym agent separately in two terminals (useful for debugging):

#### Terminal 1

    ./ns3 run "new-rl-tcp --transport_prot=TcpRlTimeBased"

#### Terminal 2

    cd ./contrib/opengym/examples/new-rl-tcp/ 
    ./TCP-RL-Agent.py --start=0

### 5. Run TCP RL Tahoe Hybrid

    python3 main.py



<br />
<br />
<br />
<br />

# 2. MahiMahi Emulator</br>
Step 1: Install dependencies

    sudo apt update
    sudo apt install -y \
        build-essential \
        cmake \
        pkg-config \
        libprotobuf-dev \
        protobuf-compiler \
        libssl-dev \
        libcurl4-openssl-dev \
        libmicrohttpd-dev \
        libboost-all-dev \
        liblua5.2-dev \
        apache2 \
        libapache2-mod-php \
        php-cli \
        unzip \
        git
Step 2: Clone Mahimahi from GitHub

        git clone https://github.com/ravinet/mahimahi.git
        cd mahimahi
Step 3: Build and install Mahimahi

        make
        sudo make install

Step 4: Test installation

        which mm-webrecord
        mm-delay --help
To run:
IN tcp_analysis_project:

    run ./capture_reno.sh
    run ./capture_tahoe.sh
    run ./capture_cubic.sh
    python analyse.py


.

    ├── tcp_analysis_project/               # Project directory for TCP performance analysis
    │   ├── analyze.py                      # Python script for analyzing trace data
    │   ├── capture.sh                      # Shell script to capture TCP traffic
    │   ├── captureCubic.sh                 # Capture script specific to Cubic TCP
    │   ├── captureTahoe.sh                 # Capture script specific to Tahoe TCP
    │   ├── record.sh                       # Records TCP sessions
    │   ├── replay.sh                       # Replays captured TCP traffic
    │   ├── plots/                          # Stores generated analysis plots
    │   └── traces/                         # Contains trace files from different TCP variants
    ├── new-rl-tcp/                         # RL-based TCP implementation
    │   ├── TCP-RL-Agent.py                 # Core agent implementation for RL-based TCP
    │   ├── hybrid_tahoe_rl.py             # Hybrid RL Tahoe variant
    │   ├── main.py                         # Entry point for training/testing
    │   ├── tcp_base.py                     # Base TCP class used by RL variants
    │   ├── sim.cc                          # NS3 simulation C++ file
    │   ├── tcp-rl.cc / .h                  # RL-based TCP source files
    │   ├── tcp-rl-env.cc / .h             # NS3 environment interface
    │   ├── LICENSE, README.md              # Documentation and license
    │   ├── reference_doc_used_for...pdf    # Reference document used in implementation
    │   ├── rl_plot.png                     # RL training performance plot
    │   └── run.log                         # Log output from a simulation run
    ├── new-tcp/                            # Classic and hybrid TCP implementations
    │   ├── tcp_base.py                     # Base class for classic TCP variants
    │   ├── tcp_cubic.py                    # Cubic TCP implementation
    │   ├── tcp_cubic_with_loss_predictor.py # Enhanced Cubic with loss prediction
    │   ├── tcp_hybrid_cubic_bbr.py         # Hybrid Cubic-BBR implementation
    │   ├── tcp_newreno.py                  # NewReno TCP variant
    │   ├── tcp_newtahoe.py                 # NewTahoe TCP variant
    │   ├── tcp-rl-env.cc                   # Common environment file for TCP variants
    │   ├── sim.cc                          # NS3 simulation file
    │   ├── random_forest_train.py          # ML model training for loss prediction
    │   ├── samples.csv                     # Data used for ML model training
    │   ├── hybrid_log.txt                  # Logs for hybrid TCP tests
    │   ├── my_log_file.txt                 # Custom log file
    │   ├── README.md                       # Description of the TCP experiments
    │   ├── logs/                           # Log outputs
    │   └── plots/                          # Graphs and visual outputs
        └── test_tcp.py                         # Python test script for TCP modules
        └── trained_random_forest.joblib        # Pretrained ML model for TCP decision making

