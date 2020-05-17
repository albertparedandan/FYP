# SUMO FYP Traffic Simulation
SUMO simulation of FYP traffic algorithm. demo.py contains different modes of algorithm. Uncomment the "if" statements to enable the different algorithm modes.

There are 4 modes of algorithm:
- Algorithm 1 is the default algorithm
- Algorithm 2 is Algorithm 1 + Traffic Count at origin lane
- Algorithm 3 is Algorithm 2 + Congestion Boolean
- Algorithm 4 is Algorithm 3 + Lag Limit

## Explanation
1. Simulation files are located at demo.py
2. my_route.rou.xml contains the routes for the randomised trips
3. Additional config is put inside demo.add.xml, such as induction loops useful to gain statistical insights and for congestion simulation
4. All the results will be printed in the out.xml, tripinfo.xml
5. script.py is the script used to get statistical data from the out.xml file
6. randomTrips.py is used to generate random trips and route files
7. all the results are stored in the folder named proper
- con = with congestion boolean
- lag = with lag limit
- sou = traffic count of source
- def = default traffic phase sequence
- traf = with congestion simulated

## Getting Started
These instructions will get you to clone and run the project on your local machine for development and testing purposes.
```
# generate network files
netconvert --node-files NODE_FILE.nod.xml --edge-files EDGE_FILE.edg.xml -t TYPE_FILE.type.xml -o OUT_FILE.net.xml 

# generate random trips
python3 randomTrips.py -n NET_FILE.net.xml -r ROU_FILE.rou.xml -e END_DURA -l

# run simulation
python demo.py

```

### Prerequisites
* SUMO
* Python

# Authors
* Albert Paredandan
* Hans Krishandi
