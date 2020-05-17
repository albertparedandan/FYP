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

    # total wait time of lanes
    con_lane_wait = 0
    other_lane_wait = 0

    # list of lane_id of outgoing lanes
    out_lane_names = ["n1ton4_0", "n1ton4_1", "n0ton4_0", "n0ton4_1", "n3ton4_0", "n3ton4_1", "n2ton4_0", "n2ton4_1"]
    # list of lane_id of incoming lanes
    in_lane_names = ["n4ton1_1", "n4ton1_0", "n4ton0_1", "n4ton0_0", "n4ton3_1", "n4ton3_0", "n4ton2_1", "n4ton2_0"]
    # list of detector_ids in incoming lanes
    in_lane_det = ["myLoop11", "myLoop10", "myLoop9", "myLoop8", "myLoop15", "myLoop14", "myLoop13", "myLoop12"]
    # array to keep track of durations left in each traffic light
    time_limit = 42
    durations = [42, 42, 42, 42, 42, 42, 42, 42]
    # array to know if the traffic light is off or not
    traffic_mode = [0, 0, 0, 0, 0, 0, 0, 0]
    # array to keep track of number of vehicles in the outgoing lanes
    source_density = [0, 0, 0, 0, 0, 0, 0, 0]

    # array to keep track of average speed in the incoming lanes
    # -1 indicates that the lane is not supposed to have incoming vehicles
    # 0 indicates that the lane is supposed to have incoming vehicles, but congestion might be going on
    target_mSpeed = [-1, -1, -1, -1, -1, -1, -1, -1]

    # array to keep track if the lanes are lagging behind
    # only checks the left turn lanes since only they can be lagging behind
    # other lanes are included in order to keep the indices consistent
    lagging_lanes = [0, 0, 0, 0, 0, 0, 0, 0]

    # this is the new lagging time limit that will be set to a traffic light if they are lagging behind
    lag_time = (2 * time_limit) // 3

    major_phase = True
    traffic_mode[1] = 1
    traci.trafficlight.setLinkState("node4", 1, "G")
    traffic_mode[5] = 1
    traci.trafficlight.setLinkState("node4", 5, "G")

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        
        ## traffic
        vehs = traci.inductionloop.getLastStepVehicleIDs(in_lane_det[5])
        for veh in vehs:
            # print(traci.vehicle.getSpeed(veh))
            traci.vehicle.setSpeed(veh, 0.3)

        for i in range(8):
            if traci.lane.getLastStepVehicleNumber(out_lane_names[i]) == 0 and traffic_mode[i] == 1:
                source_density[i] -= 1
            else:
                source_density[i] = traci.lane.getLastStepVehicleNumber(out_lane_names[i])
            
            if i % 2 == 0:
                if traffic_mode[i] == 1:
                    if traci.lane.getLastStepVehicleNumber(in_lane_names[(i + 5) % 8]) > 0:
                        target_mSpeed[(i + 5) % 8] = traci.lane.getLastStepMeanSpeed(in_lane_names[(i + 5) % 8])
                    elif traci.lane.getLastStepVehicleNumber(in_lane_names[(i + 5) % 8]) < 1:
                        target_mSpeed[(i + 5) % 8] = -1
                else:
                    target_mSpeed[(i + 5) % 8] = -1

            else:
                if traffic_mode[i] == 1:
                    if traci.lane.getLastStepVehicleNumber(in_lane_names[(i + 1) % 8]) > 0:
                        target_mSpeed[(i + 1) % 8] = traci.lane.getLastStepMeanSpeed(in_lane_names[(i + 1) % 8])
                    elif traci.lane.getLastStepVehicleNumber(in_lane_names[(i + 1) % 8]) < 1:
                        target_mSpeed[(i + 1) % 8] = -1
                else:
                    target_mSpeed[(i + 1) % 8] = -1

        if major_phase:
            print("major: " , lagging_lanes)
            print("durations: " , durations)
            if (durations[1] == 0 and traffic_mode[1] == 1) or source_density[1] < -5 or (target_mSpeed[2] > 0 and target_mSpeed[2] < 3):
            # if (durations[1] == 0 and traffic_mode[1] == 1) or source_density[1] < -5:
            # if (durations[1] == 0 and traffic_mode[1] == 1):
                traffic_mode[1] = 0
                lagging_lanes[1] = 0
                traci.trafficlight.setLinkState("node4", 1, "r")
                durations[1] = 42
                #engage the next ring
                traffic_mode[4] = 1
                if traci.lane.getLastStepHaltingNumber(out_lane_names[4]) > 0:
                    other_lane_wait += traci.lane.getWaitingTime(out_lane_names[4]) / traci.lane.getLastStepHaltingNumber(out_lane_names[4])
                traci.trafficlight.setLinkState("node4", 4, "G")
                durations[4] = 42

            elif durations[1] > 0 and traffic_mode[1] == 1:
                durations[1] -= 1

            if lagging_lanes[1] == 0 and traffic_mode[1] == 1 and traffic_mode[0] == 1 and durations[1] > lag_time:
                lagging_lanes[1] = 1
                durations[1] = lag_time

            if (durations[5] == 0 and traffic_mode[5] == 1) or source_density[5] < -5 or (target_mSpeed[6] > 0 and target_mSpeed[6] < 0):
            # if (durations[5] == 0 and traffic_mode[5] == 1) or source_density[5] < -5:
            # if (durations[5] == 0 and traffic_mode[5] == 1):
                traffic_mode[5] = 0
                lagging_lanes[5] = 0
                traci.trafficlight.setLinkState("node4", 5, "r")
                durations[5] = 42
                # engage the next right
                traffic_mode[0] = 1
                if traci.lane.getLastStepHaltingNumber(out_lane_names[0]) > 0:
                    con_lane_wait += traci.lane.getWaitingTime(out_lane_names[0]) / traci.lane.getLastStepHaltingNumber(out_lane_names[0])
                traci.trafficlight.setLinkState("node4", 0, "G")
                durations[0] = 42

            elif durations[5] > 0 and traffic_mode[5] == 1:
                durations[5] -= 1

            if lagging_lanes[5] == 0 and traffic_mode[5] == 1 and traffic_mode[4] == 1 and durations[5] > lag_time:
                lagging_lanes[5] = 1
                durations[5] = lag_time

            if (durations[0] == 0 and traffic_mode[0] == 1) or source_density[0] < -5 or (target_mSpeed[5] > 0 and target_mSpeed[5] < 3):
            # if (durations[0] == 0 and traffic_mode[0] == 1) or source_density[0] < -5:
            # if (durations[0] == 0 and traffic_mode[0] == 1):
                traffic_mode[0] = -1
                traci.trafficlight.setLinkState("node4", 0, "r")
                durations[0] = 42

            elif durations[0] > 0 and traffic_mode[0] == 1:
                durations[0] -= 1

            if (durations[4] == 0 and traffic_mode[4] == 1) or source_density[4] < -5 or (target_mSpeed[1] > 0 and target_mSpeed[1] < 3):
            # if (durations[4] == 0 and traffic_mode[4] == 1) or source_density[4] < -5:
            # if (durations[4] == 0 and traffic_mode[4] == 1):
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
                if traci.lane.getLastStepHaltingNumber(out_lane_names[3]) > 0:
                    other_lane_wait += traci.lane.getWaitingTime(out_lane_names[3]) / traci.lane.getLastStepHaltingNumber(out_lane_names[3])
                traci.trafficlight.setLinkState("node4", 3, "G")
                durations[3] = 42
                traffic_mode[7] = 1
                if traci.lane.getLastStepHaltingNumber(out_lane_names[7]) > 0:
                    other_lane_wait += traci.lane.getWaitingTime(out_lane_names[7]) / traci.lane.getLastStepHaltingNumber(out_lane_names[7])
                traci.trafficlight.setLinkState("node4", 7, "G")
                durations[7] = 42

        else:
            print("minor: " , lagging_lanes)
            print("durations: " , durations)
            if (durations[3] == 0 and traffic_mode[3] == 1) or source_density[3] < -5 or (target_mSpeed[4] > 0 and target_mSpeed[4] < 3):
            # if (durations[3] == 0 and traffic_mode[3] == 1) or source_density[3] < -5:
            # if (durations[3] == 0 and traffic_mode[3] == 1):
                traffic_mode[3] = 0
                lagging_lanes[3] = 0
                traci.trafficlight.setLinkState("node4", 3, "r")
                durations[3] = 42
                # move to next ring
                traffic_mode[6] = 1
                if traci.lane.getLastStepHaltingNumber(out_lane_names[6]) > 0:
                    other_lane_wait += traci.lane.getWaitingTime(out_lane_names[6]) / traci.lane.getLastStepHaltingNumber(out_lane_names[6])
                traci.trafficlight.setLinkState("node4", 6, "G")
                durations[6] = 42

            elif durations[3] > 0 and traffic_mode[3] == 1:
                durations[3] -= 1

            if lagging_lanes[3] == 0 and traffic_mode[3] == 1 and traffic_mode[2] == 1 and durations[3] > lag_time:
                lagging_lanes[3] = 1
                durations[3] = lag_time

            if (durations[7] == 0 and traffic_mode[7] == 1) or source_density[7] < -5 or (target_mSpeed[0] > 0 and target_mSpeed[0] < 3):
            # if (durations[7] == 0 and traffic_mode[7] == 1) or source_density[7] < -5:
            # if (durations[7] == 0 and traffic_mode[7] == 1):
                traffic_mode[7] = 0
                traci.trafficlight.setLinkState("node4", 7, "r")
                durations[7] = 42
                # move to next ring
                traffic_mode[2] = 1
                if traci.lane.getLastStepHaltingNumber(out_lane_names[2]) > 0:
                    other_lane_wait += traci.lane.getWaitingTime(out_lane_names[2]) / traci.lane.getLastStepHaltingNumber(out_lane_names[2])
                traci.trafficlight.setLinkState("node4", 2, "G")
                durations[2] = 42

            elif durations[7] > 0 and traffic_mode[7] == 1:
                durations[7] -= 1

            if lagging_lanes[7] == 0 and traffic_mode[7] == 1 and traffic_mode[6] == 1 and durations[7] > lag_time:
                lagging_lanes[7] = 1
                durations[7] = lag_time

            if (durations[2] == 0 and traffic_mode[2] == 1) or source_density[2] < -5 or (target_mSpeed[7] > 0 and target_mSpeed[7] < 3):
            # if (durations[2] == 0 and traffic_mode[2] == 1) or source_density[2] < -5:
            # if (durations[2] == 0 and traffic_mode[2] == 1):
                traffic_mode[2] = -1 
                traci.trafficlight.setLinkState("node4", 2, "r")
                durations[2] = 42

            elif durations[2] > 0 and traffic_mode[2] == 1:
                durations[2] -= 1

            if (durations[6] == 0 and traffic_mode[6] == 1) or source_density[6] < -5 or (target_mSpeed[3] > 0 and target_mSpeed[3] < 3):
            # if (durations[6] == 0 and traffic_mode[6] == 1) or source_density[6] < -5:
            # if (durations[6] == 0 and traffic_mode[6] == 1):
                traffic_mode[6] = -1
                traci.trafficlight.setLinkState("node4", 6, "r")
                durations[6] = 42

            elif durations[6] > 0 and traffic_mode[6] == 1:
                durations[6] -= 1

            if traffic_mode[2] == -1 and traffic_mode[6] == -1:
                major_phase = True
                # set all minor phase stuff back to 0
                traffic_mode[2] = 0
                traffic_mode[6] = 0
                # enter next ring (major phase)
                traffic_mode[1] = 1
                if traci.lane.getLastStepHaltingNumber(out_lane_names[1]) > 0:
                    other_lane_wait += traci.lane.getWaitingTime(out_lane_names[1]) / traci.lane.getLastStepHaltingNumber(out_lane_names[1])
                traci.trafficlight.setLinkState("node4", 1, "G")
                durations[1] = 42
                traffic_mode[5] = 1
                if traci.lane.getLastStepHaltingNumber(out_lane_names[5]) > 0:
                    other_lane_wait += traci.lane.getWaitingTime(out_lane_names[5]) / traci.lane.getLastStepHaltingNumber(out_lane_names[5])
                traci.trafficlight.setLinkState("node4", 5, "G")
                durations[5] = 42

        step += 1
    
    print("Congestion lane wait: " + str(con_lane_wait))
    print("Other lane wait: " + str(other_lane_wait/7))
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
