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

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options


# contains TraCI control loop
def run():
    step = 0

    # list of lane_id of outgoing lanes
    out_lane_names = ["n1ton4_0", "n1ton4_1", "n0ton4_0", "n0ton4_1", "n3ton4_0", "n3ton4_1", "n2ton4_0", "n2ton4_1"]
    # list of lane_id of incoming lanes
    in_lane_names = ["n4ton1_1", "n4ton1_0", "n4ton0_1", "n4ton0_0", "n4ton3_1", "n4ton3_0", "n4ton2_1", "n4ton2_0"]
    # list of detector_ids in incoming lanes
    in_lane_det = ["myLoop11", "myLoop10", "myLoop9", "myLoop8", "myLoop15", "myLoop14", "myLoop13", "myLoop12"]
    # array to keep track of durations left in each traffic light
    durations = [42, 42, 42, 42, 42, 42, 42, 42]
    # array to know if the traffic light is off or not
    traffic_mode = [0, 0, 0, 0, 0, 0, 0, 0]
    # array to keep track of number of vehicles in the outgoing lanes
    source_density = [0, 0, 0, 0, 0, 0, 0, 0]

    # array to keep track of average speed in the incoming lanes
    # -1 indicates that the lane is not supposed to have incoming vehicles
    # 0 indicates that the lane is supposed to have incoming vehicles, but congestion might be going on
    target_mSpeed = [-1, -1, -1, -1, -1, -1, -1, -1]


    major_phase = True
    traffic_mode[1] = 1
    traci.trafficlight.setLinkState("node4", 1, "G")
    traffic_mode[5] = 1
    traci.trafficlight.setLinkState("node4", 5, "G")

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        
        vehs = traci.inductionloop.getLastStepVehicleIDs("myLoop12")
        for veh in vehs:
            print(traci.vehicle.getSpeed(veh))
            traci.vehicle.setSpeed(veh, 0.5)

        for i in range(8):
            if traci.lane.getLastStepVehicleNumber(out_lane_names[i]) == 0 and traffic_mode[i] == 1:
                source_density[i] -= 1
            else:
                source_density[i] = traci.lane.getLastStepVehicleNumber(out_lane_names[i])
            
            if traffic_mode[i] == 1:
                if i % 2 == 0:
                    print("i" , i)
                    print("i+5%8", (i+7)%8)
                    print("#vehi: " , traci.lane.getLastStepVehicleNumber(in_lane_names[(i+7)%8]))
                    if traci.lane.getLastStepVehicleNumber(in_lane_names[(i + 5) % 8]) > 0:
                        target_mSpeed[(i + 5) % 8] = traci.lane.getLastStepMeanSpeed(in_lane_names[(i + 5) % 8])
                    elif traci.lane.getLastStepVehicleNumber(in_lane_names[(i + 5) % 8]) < 1:
                        print("if2")
                        print((i+5)%8)
                        target_mSpeed[(i + 5) % 8] = -1
                    if traci.lane.getLastStepVehicleNumber(in_lane_names[(i + 7) % 8]) > 0:
                        print(traci.lane.getLastStepMeanSpeed(in_lane_names[(i + 7) % 8]))
                        target_mSpeed[(i + 7) % 8] = traci.lane.getLastStepMeanSpeed(in_lane_names[(i + 7) % 8])
                    elif traci.lane.getLastStepVehicleNumber(in_lane_names[(i + 7) % 8]) < 1:
                        print("SOMEHOW GOES HERE")
                        print((i+7)%8)
                        target_mSpeed[(i + 7) % 8] = -1
                else:
                    if traci.lane.getLastStepVehicleNumber(in_lane_names[(i + 1) % 8]) > 0:
                        target_mSpeed[(i + 1) % 8] = traci.lane.getLastStepMeanSpeed(in_lane_names[(i + 1) % 8])
                    elif traci.lane.getLastStepVehicleNumber(in_lane_names[(i + 1) % 8]) < 1:
                        print("if3")
                        print((i+1)%8)
                        target_mSpeed[(i + 1) % 8] = -1
            else:
                if i % 4 == 0:
                    print("if4")
                    if traffic_mode[2] == 0:
                        if i == 0:
                            target_mSpeed[7] = -1
                        if i == 4:
                            target_mSpeed[1] = -1
                    if traffic_mode[6] == 0:
                        if i == 0:
                            target_mSpeed[5] = -1
                        if i == 4:
                            target_mSpeed[3] = -1
                elif i % 4 == 2:
                    print("if5")
                    if traffic_mode[0] == 0:
                        if i == 2:
                            target_mSpeed[7] = -1
                        if i == 6:
                            target_mSpeed[5] = -1
                    if traffic_mode[4] == 0:
                        if i == 2:
                            target_mSpeed[1] = -1
                        if i == 6:
                            target_mSpeed[3] = -1
                else:
                    print("if6")
                    print((i+1)%8)
                    target_mSpeed[(i + 1) % 8] = -1

        if major_phase:
            print("major: " , target_mSpeed)
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

            if (durations[5] == 0 and traffic_mode[5] == 1) or source_density[5] < -5 or (target_mSpeed[6] > 0 and target_mSpeed[6] < 3):
                traffic_mode[5] = 0
                traci.trafficlight.setLinkState("node4", 5, "r")
                durations[5] = 42
                # engage the next right
                traffic_mode[0] = 1
                traci.trafficlight.setLinkState("node4", 0, "G")
                durations[0] = 42

            elif durations[5] > 0 and traffic_mode[5] == 1:
                durations[5] -= 1

            if (durations[0] == 0 and traffic_mode[0] == 1) or source_density[0] < -5 or (target_mSpeed[7] > 0 and target_mSpeed[7] < 3):
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
            print("minor: " , target_mSpeed)
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
                traffic_mode[2] = 1
                traci.trafficlight.setLinkState("node4", 2, "G")
                durations[2] = 42

            elif durations[7] > 0 and traffic_mode[7] == 1:
                durations[7] -= 1

            if (durations[2] == 0 and traffic_mode[2] == 1) or source_density[2] < -5 or (target_mSpeed[7] > 0 and target_mSpeed[7] < 3):
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
