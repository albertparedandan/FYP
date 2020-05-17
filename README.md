# SUMO FYP Traffic Simulation
SUMO simulation of FYP traffic algorithm. demo.py contains different modes of algorithm. Uncomment the "if" statements to enable the different algorithm modes.

## Explanation
1. Simulation files are located at demo.py
2. my_route_*.rou.xml contains different simulations and 5 different randomised trips
3. Additional config is put inside demo.add.xml, such as induction loops useful to gain statistical insights and for congestion simulation
4. All the results will be printed in the out.xml, tripinfo.xml
5. script.py is the script used to get statistical data from the out.xml file
6. randomTrips.py is used to generate random trips and route files

## Getting Started
These instructions will get you to clone and run the project on your local machine for development and testing purposes.
```
python demo.py # to run simulation
```

### Prerequisites
* SUMO
* Python

# Authors
* Albert Paredandan
