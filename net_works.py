import random
#if the quality of the link is good, it has higher P to return to HiQ
L_quality_good = [True, False, True, False, True, True, False, True]
#probability of changing quality after the interval
P_of_Qswitch = [0.002, 0.05, 0.002, 0.05, 0.002, 0.002, 0.05, 0.002]
#P boost when link is good and we are in bad Q
P_GOOD_BOOST = 0.2
#initial network trace
network_trace = [[0, 0, 0, 0, 0, 0, 0, 0]]
HIGH_REP = 0
LOW_REP = 2


#inputs the previous states of network (reps) and returns the next
def network_state(previous_state):
    current_state = []
    for i in range(0, len(P_of_Qswitch)):
        current_state.append(next_value(previous_state[i], P_of_Qswitch[i], L_quality_good[i]))
    return current_state


#fill network_trace with available reps of
def emulate_network(NETWORK_INTERVAL_MS):
    for t in range(0, 200000, NETWORK_INTERVAL_MS):
        i = t / NETWORK_INTERVAL_MS
        network_trace.append(network_state(network_trace[i]))
    return network_trace


def next_value(cur_value, P_in, isGood):
    if (isGood and cur_value > HIGH_REP):
        p_switch = P_in + P_GOOD_BOOST
    else:
        p_switch = P_in
    if (random.random() < p_switch):
        if (cur_value == HIGH_REP):
            return 2
        if (cur_value == LOW_REP):
            return 0
    return cur_value


def emulate_single_link_network(NETWORK_INTERVAL_MS, P_in, isGood, initial_state):
    net_trace = [initial_state]
    for t in range(0, 200000, NETWORK_INTERVAL_MS):
        i = t / NETWORK_INTERVAL_MS
        net_trace.append(next_value(net_trace[i], P_in, isGood))
    return net_trace