#!/usr/bin/env python

import os
import sys
import optparse

# we need to import some python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


from sumolib import checkBinary  # Checks for the binary in environ vars
import traci

log = open("log.txt", "w")

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options


# contains TraCI control loop
def run():
    step = 0
    lane_names = ["n1ton4_0", "n1ton4_1", "n0ton4_0", "n0ton4_1", "n3ton4_0", "n3ton4_1", "n2ton4_0", "n2ton4_1"]
    durations = [42, 42, 42, 42, 42, 42, 42, 42]
    traffic_mode = [0, 0, 0, 0, 0, 0, 0, 0]
    source_density = [0, 0, 0, 0, 0, 0, 0, 0]
    target_mSpeed = [0, 0, 0, 0, 0, 0, 0, 0]


    major_phase = True
    traffic_mode[1] = 1
    traci.trafficlight.setLinkState("node4", 1, "G")
    traffic_mode[5] = 1
    traci.trafficlight.setLinkState("node4", 5, "G")

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        
        for i in range(8):
            if traci.lane.getLastStepVehicleNumber(lane_names[i]) == 0 and traffic_mode[i] == 1:
                source_density[i] -= 1
            else:
                source_density[i] = traci.lane.getLastStepVehicleNumber(lane_names[i])

            target_mSpeed[i] = traci.lane.getLastStepMeanSpeed(lane_names[i])

        if major_phase:
            if (durations[1] == 0 and traffic_mode[1] == 1) or source_density[1] < -5:
                traffic_mode[1] = 0
                traci.trafficlight.setLinkState("node4", 1, "r")
                durations[1] = 42
                #engage the next ring
                traffic_mode[4] = 1
                traci.trafficlight.setLinkState("node4", 4, "G")
                durations[4] = 42

            elif durations[1] > 0 and traffic_mode[1] == 1:
                durations[1] -= 1

            if (durations[5] == 0 and traffic_mode[5] == 1) or source_density[5] < -5:
                traffic_mode[5] = 0
                traci.trafficlight.setLinkState("node4", 5, "r")
                durations[5] = 42
                # engage the next right
                traffic_mode[0] = 1
                traci.trafficlight.setLinkState("node4", 0, "G")
                durations[0] = 42

            elif durations[5] > 0 and traffic_mode[5] == 1:
                durations[5] -= 1

            if (durations[0] == 0 and traffic_mode[0] == 1) or source_density[0] < -5:
                traffic_mode[0] = -1
                traci.trafficlight.setLinkState("node4", 0, "r")
                durations[0] = 42

            elif durations[0] > 0 and traffic_mode[0] == 1:
                durations[0] -= 1

            if (durations[4] == 0 and traffic_mode[4] == 1) or source_density[4] < -5:
                traffic_mode[4] = -1
                traci.trafficlight.setLinkState("node4", 4, "r")
                durations[4] = 42

            elif durations[4] > 0 and traffic_mode[4] == 1:
                durations[4] -= 1

            if traffic_mode[0] == -1 and traffic_mode[4] == -1:
                major_phase = False
                # set all major phase stuff back to 0
                traffic_mode[0] = 0
                traffic_mode[4] = 0
                # enter next ring (minor phase)
                traffic_mode[3] = 1
                traci.trafficlight.setLinkState("node4", 3, "G")
                durations[3] = 42
                traffic_mode[7] = 1
                traci.trafficlight.setLinkState("node4", 7, "G")
                durations[7] = 42

        else:
            print("minor: " , source_density)
            if (durations[3] == 0 and traffic_mode[3] == 1) or source_density[3] < -5:
                traffic_mode[3] = 0
                traci.trafficlight.setLinkState("node4", 3, "r")
                durations[3] = 42
                # move to next ring
                traffic_mode[6] = 1
                traci.trafficlight.setLinkState("node4", 6, "G")
                durations[6] = 42

            elif durations[3] > 0 and traffic_mode[3] == 1:
                durations[3] -= 1

            if (durations[7] == 0 and traffic_mode[7] == 1) or source_density[7] < -5:
                traffic_mode[7] = 0
                traci.trafficlight.setLinkState("node4", 7, "r")
                durations[7] = 42
                # move to next ring
                print("here")
                traffic_mode[2] = 1
                traci.trafficlight.setLinkState("node4", 2, "G")
                durations[2] = 42

            elif durations[7] > 0 and traffic_mode[7] == 1:
                durations[7] -= 1

            if (durations[2] == 0 and traffic_mode[2] == 1) or source_density[2] < -5:
                print("cus")
                traffic_mode[2] = -1 
                traci.trafficlight.setLinkState("node4", 2, "r")
                durations[2] = 42

            elif durations[2] > 0 and traffic_mode[2] == 1:
                durations[2] -= 1

            if (durations[6] == 0 and traffic_mode[6] == 1) or source_density[6] < -5:
                traffic_mode[6] = -1
                traci.trafficlight.setLinkState("node4", 6, "r")
                durations[6] = 42

            elif durations[6] > 0 and traffic_mode[6] == 1:
                durations[6] -= 1

            if (traffic_mode[2] == -1 and traffic_mode[6] == -1) or source_density[2] < -5:
                major_phase = True
                # set all minor phase stuff back to 0
                traffic_mode[2] = 0
                traffic_mode[6] = 0
                # enter next ring (major phase)
                traffic_mode[1] = 1
                traci.trafficlight.setLinkState("node4", 1, "G")
                durations[1] = 42
                traffic_mode[5] = 1
                traci.trafficlight.setLinkState("node4", 5, "G")
                durations[5] = 42

        # if traffic mode is on, decrease the duration by 1
        # if off, make it the default value
        # for i in range(8):
        #     source_density[i] = traci.lane.getLastStepVehicleNumber(lane_names[i])

        #     if  traffic_mode[i] == 0:
        #         durations[i] = 42
        #         traci.trafficlight.setLinkState("node4", i, "r")

        #     elif traffic_mode[i] == 1 and durations[i] == 0:
        #         traffic_mode[i] = 0
        #         traci.trafficlight.setLinkState("node4", i, "r")

        #     elif traffic_mode[i] == 1 and durations[i] > 0 and source_density[i] == 0:
        #         traffic_mode[i] = 0
        #         traci.trafficlight.setLinkState("node4", i, "r")

        #     elif traffic_mode[i] == 1 and durations[i] > 0 and source_density[i] > 0:
        #         durations[i] -= 1

        # print("i: " , i , " | traffic_mode: " , traffic_mode , " | durations: " , durations , " | source_density: " , source_density)
        
        # print("durations: " , durations)
        # print("traffic_mode: " , traffic_mode)
        # print("step", step)
        # first phase 

        step += 1

    traci.close()
    sys.stdout.flush()


# main entry point
if __name__ == "__main__":
    options = get_options()

    # check binary
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "my_config_file.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()
