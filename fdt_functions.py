import math
import numpy as np
from parameters import warm_up_duration, number_days, update_method


class Graph:
    def __init__(self):
        self.data_nodes = None
        self.node_id = 0
        self.node_time = 1
        self.node_name = 2
        self.node_direction = 3
        self.node_line = 4
        self.node_vehicle = 5
        self.node_cycle = 6
        self.next_visit = 7
        self.next_station = 8
        self.dwell_time = 9
        self.parcel_visit = 10
        self.parcel_visit_no_update = 11
        self.previous_node_station = 12
        self.previous_node_station_no_update = 13
        self.previous_node_vehicle = 14
        self.previous_node_vehicle_no_update = 15
        self.shortage = 16
        self.capacity_vehicle = 17
        self.cost_shortage = 18
        self.current_index = 0

    def shortest_path(self, source, target, parcel_index, max_change):
        flag, flag_no_update = False, False
        parcel_time, path, time_no_update, path_no_update = None, None, None, None
        dwell_time_update = []
        dwell_time_check = []
        start_index = self.data_nodes[self.current_index:, self.node_name].tolist().index(source) + self.current_index
        self.data_nodes[start_index, self.parcel_visit] = parcel_index
        self.data_nodes[start_index, self.previous_node_station] = ('source', 0)
        self.data_nodes[start_index, self.previous_node_vehicle] = (None, np.inf)
        self.data_nodes[start_index, self.parcel_visit_no_update] = parcel_index
        self.data_nodes[start_index, self.previous_node_station_no_update] = ('source', 0)
        self.data_nodes[start_index, self.previous_node_vehicle_no_update] = (None, np.inf)

        for ind in range(start_index, self.data_nodes.shape[0]):
            # The next visit of a vehicle at the station
            next_visit = self.data_nodes[ind, self.next_visit]
            # Reset relevant variables
            if self.data_nodes[next_visit, self.parcel_visit] != parcel_index:
                self.data_nodes[next_visit, self.previous_node_station] = (None, np.inf)
                self.data_nodes[next_visit, self.previous_node_vehicle] = (None, np.inf)
            if self.data_nodes[next_visit, self.parcel_visit_no_update] != parcel_index:
                self.data_nodes[next_visit, self.previous_node_station_no_update] = (None, np.inf)
                self.data_nodes[next_visit, self.previous_node_vehicle_no_update] = (None, np.inf)

            # The vehicle's next stop on its route
            next_station = self.data_nodes[ind, self.next_station]
            # Reset relevant variables
            if self.data_nodes[next_station, self.parcel_visit] != parcel_index:
                self.data_nodes[next_station, self.previous_node_station] = (None, np.inf)
                self.data_nodes[next_station, self.previous_node_vehicle] = (None, np.inf)
            if self.data_nodes[next_station, self.parcel_visit_no_update] != parcel_index:
                self.data_nodes[next_station, self.previous_node_station_no_update] = (None, np.inf)
                self.data_nodes[next_station, self.previous_node_vehicle_no_update] = (None, np.inf)

            # If this node was visited in the normal path
            if self.data_nodes[ind, self.parcel_visit] == parcel_index and not flag:
                prev_ind_station = self.data_nodes[ind, self.previous_node_station]
                prev_ind_vehicle = self.data_nodes[ind, self.previous_node_vehicle]
                if self.data_nodes[ind, self.dwell_time] > 0:
                    if self.data_nodes[ind, self.node_name] == target:
                        path = [ind]
                        dwell_time_update.append(ind)
                        previous_index = ind
                        # The destination can only be reached by a vehicle arc
                        curr_index = self.data_nodes[previous_index, self.previous_node_vehicle][0]
                        curr_edge = 'vehicle'
                        self.data_nodes[curr_index, self.capacity_vehicle] += 1
                        # while we haven't reached the start index
                        while curr_index != 'source':
                            path.append(curr_index)
                            previous_index = curr_index
                            prev_edge = curr_edge
                            curr_index_station = self.data_nodes[previous_index, self.previous_node_station]
                            curr_index_vehicle = self.data_nodes[previous_index, self.previous_node_vehicle]
                            previous_index_dwell_time = self.data_nodes[previous_index, self.dwell_time]
                            if prev_edge == 'vehicle':
                                if curr_index_vehicle[1] >= curr_index_station[1] + 1 and previous_index_dwell_time > 0:
                                    curr_index = curr_index_station[0]
                                    curr_edge = 'station'
                                else:
                                    curr_index = curr_index_vehicle[0]
                                    curr_edge = 'vehicle'
                                    self.data_nodes[curr_index, self.capacity_vehicle] += 1
                            elif prev_edge == 'station':
                                if curr_index_vehicle[1] + 1 < curr_index_station[1] and previous_index_dwell_time > 0:
                                    curr_index = curr_index_vehicle[0]
                                    curr_edge = 'vehicle'
                                    self.data_nodes[curr_index, self.capacity_vehicle] += 1
                                else:
                                    curr_index = curr_index_station[0]
                                    curr_edge = 'station'
                            if curr_edge != prev_edge:
                                dwell_time_update.append(previous_index)
                        flag = True
                        parcel_time = self.data_nodes[ind, self.node_time]
                    else:
                        if prev_ind_vehicle[1] >= prev_ind_station[1] + 1:
                            if prev_ind_station[1] + 1 <= max_change:
                                self.data_nodes[next_station, self.previous_node_vehicle] = (ind,
                                                                                             prev_ind_station[1] + 1)
                                self.data_nodes[next_station, self.parcel_visit] = parcel_index
                        else:
                            self.data_nodes[next_station, self.previous_node_vehicle] = (ind, prev_ind_vehicle[1])
                            self.data_nodes[next_station, self.parcel_visit] = parcel_index

                        if prev_ind_vehicle[1] + 1 >= prev_ind_station[1]:
                            self.data_nodes[next_visit, self.previous_node_station] = (ind, prev_ind_station[1])
                            self.data_nodes[next_visit, self.parcel_visit] = parcel_index
                        else:
                            if prev_ind_vehicle[1] + 1 <= max_change:
                                self.data_nodes[next_visit, self.previous_node_station] = (ind, prev_ind_vehicle[1] + 1)
                                self.data_nodes[next_visit, self.parcel_visit] = parcel_index

                else:
                    if prev_ind_vehicle[0]:
                        self.data_nodes[next_station, self.previous_node_vehicle] = (ind, prev_ind_vehicle[1])
                        self.data_nodes[next_station, self.parcel_visit] = parcel_index
                    if prev_ind_station[0]:
                        self.data_nodes[next_visit, self.previous_node_station] = (ind, prev_ind_station[1])
                        self.data_nodes[next_visit, self.parcel_visit] = parcel_index

            # If this node was visited in the non-updated path
            if self.data_nodes[ind, self.parcel_visit_no_update] == parcel_index and not flag_no_update:
                prev_ind_station = self.data_nodes[ind, self.previous_node_station_no_update]
                prev_ind_vehicle = self.data_nodes[ind, self.previous_node_vehicle_no_update]
                if self.data_nodes[ind, self.node_name] == target:
                    path_no_update = [ind]
                    dwell_time_check.append(ind)
                    previous_index = ind
                    # The destination can only be reached by a vehicle arc
                    curr_index = self.data_nodes[previous_index, self.previous_node_vehicle_no_update][0]
                    curr_edge = 'vehicle'
                    # while we haven't reached the start index
                    while curr_index != 'source':
                        path_no_update.append(curr_index)
                        previous_index = curr_index
                        prev_edge = curr_edge
                        curr_index_station = self.data_nodes[previous_index, self.previous_node_station_no_update]
                        curr_index_vehicle = self.data_nodes[previous_index, self.previous_node_vehicle_no_update]
                        if prev_edge == 'vehicle':
                            if curr_index_vehicle[1] >= curr_index_station[1] + 1:
                                curr_index = curr_index_station[0]
                                curr_edge = 'station'
                            else:
                                curr_index = curr_index_vehicle[0]
                                curr_edge = 'vehicle'
                        elif prev_edge == 'station':
                            if curr_index_vehicle[1] + 1 < curr_index_station[1]:
                                curr_index = curr_index_vehicle[0]
                                curr_edge = 'vehicle'
                            else:
                                curr_index = curr_index_station[0]
                                curr_edge = 'station'
                        if curr_edge != prev_edge:
                            dwell_time_check.append(previous_index)
                    flag_no_update = True
                    time_no_update = self.data_nodes[ind, self.node_time]
                else:
                    self.data_nodes[next_station, self.parcel_visit_no_update] = parcel_index
                    self.data_nodes[next_visit, self.parcel_visit_no_update] = parcel_index

                    if prev_ind_vehicle[1] >= prev_ind_station[1] + 1:
                        self.data_nodes[next_station, self.previous_node_vehicle_no_update] = (ind,
                                                                                               prev_ind_station[1] + 1)
                    else:
                        self.data_nodes[next_station, self.previous_node_vehicle_no_update] = (ind, prev_ind_vehicle[1])

                    if prev_ind_vehicle[1] + 1 >= prev_ind_station[1]:
                        self.data_nodes[next_visit, self.previous_node_station_no_update] = (ind, prev_ind_station[1])
                    else:
                        self.data_nodes[next_visit, self.previous_node_station_no_update] = (ind,
                                                                                             prev_ind_vehicle[1] + 1)

            # If both paths are found (the normal and the non-updated)
            if flag and flag_no_update:
                return parcel_time, time_no_update, dwell_time_update, dwell_time_check
        return parcel_time, time_no_update, dwell_time_update, dwell_time_check

    def update_graph(self, dwell_time_update):
        for i in dwell_time_update:
            # Updating the stay time at intermediate points
            self.data_nodes[i, self.dwell_time] -= 1

    def check_path_no_update(self, dwell_time_check, cost):
        nodes_shortage = []
        for i in dwell_time_check:
            if self.data_nodes[i, self.dwell_time] == 0:
                nodes_shortage.append(i)
        for i in nodes_shortage:
            self.data_nodes[i, self.shortage] += 1
            self.data_nodes[i, self.cost_shortage] += cost / len(nodes_shortage)
#######################################################################################################################


#######################################################################################################################
def sim(iteration_number, graph, parcels_arrivals, lines, parcels_max_change):
    """
       Simulation to evaluate the mean delivery times of the parcels for the FDT policy

       Args:
           iteration_number (int): The iteration number of the search algorithm.
           graph (Graph): An object representing the time-expanded graph.
           parcels_arrivals (list): List of tuples representing parcel source, target, and arrival times.
           lines (dict): Dictionary containing the objects of the lines.
           parcels_max_change (dict): Dictionary containing the maximum number of transfers each parcel is needed.

       Returns:
           - the delivery times of the parcels
           - the shortages and surpluses at each SP
           - the capacity of the vehicles when leaving the SPs
       """

    # Initialize variables
    parcel_times = []
    num_parcel = 0

    # Iterate through parcel arrivals
    for parcel_source, parcel_target, T_now in parcels_arrivals:
        num_parcel += 1

        # Find relevant data nodes in the graph
        for i in range(graph.current_index, graph.data_nodes.shape[0]):
            if graph.data_nodes[i, graph.node_time] >= T_now:
                graph.current_index = i
                break

        # Determine maximum parcel change
        if parcels_max_change:
            parcel_max_change = parcels_max_change[(parcel_source, parcel_target)]
        else:
            parcel_max_change = np.inf

        # Calculate the shortest path for the parcel
        res_shortest_path = graph.shortest_path(parcel_source, parcel_target, num_parcel, parcel_max_change)
        time_arr, time_arr_no_update, dwell_time_update, dwell_time_check = res_shortest_path

        distance = time_arr - T_now
        distance_no_update = time_arr_no_update - T_now

        # Check and update path if necessary
        if distance != distance_no_update:
            graph.check_path_no_update(dwell_time_check, distance - distance_no_update)
        graph.update_graph(dwell_time_update)

        # Update parcel times and group times
        if T_now >= warm_up_duration*1440:
            parcel_times.append([iteration_number, T_now, distance])

    # Calculate shortage, surplus, and capacity information for lines
    for line in lines:
        for s in lines[line].dwell_time:
            for direction in lines[line].dwell_time[s]:
                x = (graph.data_nodes[:, graph.node_line] == line) & \
                    (graph.data_nodes[:, graph.node_name] == s) & \
                    (graph.data_nodes[:, graph.node_direction] == direction) & \
                    (graph.data_nodes[:, graph.node_time] >= warm_up_duration * 1440) & \
                    (graph.data_nodes[:, graph.node_time] <= number_days * 1440)

                number_of_visit = x.sum()

                # Calculate shortages
                number_of_visit_shortage = np.count_nonzero(graph.data_nodes[x, graph.shortage])
                if number_of_visit_shortage > 0:
                    amount_of_shortage = np.sum(graph.data_nodes[x, graph.shortage])
                    total_cost_shortage = np.sum(graph.data_nodes[x, graph.cost_shortage])
                    lines[line].shortage[s][direction] = [number_of_visit_shortage / number_of_visit,
                                                          amount_of_shortage / number_of_visit, total_cost_shortage]
                else:
                    lines[line].shortage[s][direction] = [0, 0, 0]

                # Calculate surpluses
                number_of_visit_surplus = np.count_nonzero(graph.data_nodes[x, graph.dwell_time])
                cost_surplus = graph.data_nodes[x, graph.dwell_time] * graph.data_nodes[x, graph.capacity_vehicle]
                if number_of_visit_surplus > 0:
                    amount_of_surplus = np.sum(graph.data_nodes[x, graph.dwell_time])
                    lines[line].surplus[s][direction] = [number_of_visit_surplus / number_of_visit,
                                                         amount_of_surplus / number_of_visit, np.sum(cost_surplus)]
                else:
                    lines[line].surplus[s][direction] = [0, 0, 0]

                # Calculate capacity information
                vehicle_capacity = np.sum(graph.data_nodes[x, graph.capacity_vehicle]) / number_of_visit
                lines[line].capacity[s][direction] = vehicle_capacity

    return parcel_times, lines
#######################################################################################################################


#######################################################################################################################
def create_graph(network_data, stations, lines):
    graph = Graph()
    data_nodes = []
    for line in lines.values():
        line_data = network_data[network_data.Line == line.line_number].iloc[:, 1:].to_numpy()
        for vehicle in range(line.number_of_vehicles):
            t = vehicle * line.time_between_vehicles
            for cycle in range(math.ceil(line.f / line.number_of_vehicles) * 2 * number_days):
                prev_direction = 'b'
                for source, target, direction, travel_time in line_data:
                    if prev_direction != direction:
                        node_direction = None
                    else:
                        node_direction = direction
                    t += line.dwell_time[source][node_direction]
                    node = [None,  # node id
                            t,  # node time
                            source,  # node name
                            node_direction,  # node direction
                            line.line_number,  # node line
                            vehicle + 1,  # node vehicle
                            cycle + 1,  # node cycle
                            None,  # next visit
                            None,  # next station
                            line.dwell_time[source][node_direction],  # stay time
                            None,  # parcel visit
                            None,  # parcel visit no update
                            (None, np.inf),  # previous node station
                            (None, np.inf),  # previous node station no update
                            (None, np.inf),  # previous node vehicle
                            (None, np.inf),  # previous node vehicle no update
                            0,  # shortage
                            0,  # capacity vehicle
                            0  # cost shortage
                            ]
                    data_nodes.append(node)
                    t += travel_time
                    prev_direction = direction

    graph.data_nodes = np.array(data_nodes, dtype=object)
    graph.data_nodes = graph.data_nodes[graph.data_nodes[:, graph.node_time].argsort()]
    graph.data_nodes[:, graph.node_id] = range(graph.data_nodes.shape[0])

    # Next visit index
    for s in stations:
        x = graph.data_nodes[:, graph.node_name] == s
        list_index = graph.data_nodes[x, graph.node_id].tolist() + [None]
        graph.data_nodes[x, graph.next_visit] = list_index[1:]

    # Next station index
    for line in lines:
        for vehicle in range(1, lines[line].number_of_vehicles + 1):
            x = (graph.data_nodes[:, graph.node_line] == line) & (graph.data_nodes[:, graph.node_vehicle] == vehicle)
            a = graph.data_nodes[x, :].copy()
            a = a[np.lexsort((a[:, graph.node_cycle], a[:, graph.node_time]))]
            list_index = a[:, graph.node_id].tolist() + [None]
            graph.data_nodes[x, graph.next_station] = list_index[1:]
    return graph
#######################################################################################################################


#######################################################################################################################
def update_dwell_time(dic_lines, update_size):
    stopping_criterion = False
    update = 0
    biggest_update = 0
    for line in dic_lines.values():
        line.period = line.travel_time
        for s in line.shortage:
            for direction in line.shortage[s]:
                if update_method == 1:
                    if line.shortage[s][direction][2] >= line.surplus[s][direction][2]:
                        update = round(update_size * line.shortage[s][direction][1], 0)
                    else:
                        update = -round(update_size * line.surplus[s][direction][1], 0)

                elif update_method == 2:
                    if line.shortage[s][direction][2] >= line.surplus[s][direction][2]:
                        update = 1
                    else:
                        update = -1

                if update > biggest_update:
                    biggest_update = update

                line.dwell_time[s][direction] += update
                line.dwell_time[s][direction] = max([line.dwell_time[s][direction], 1])
                line.period += line.dwell_time[s][direction]
        line.time_between_vehicles = line.period / line.number_of_vehicles
        line.f = (1440 / line.period) * line.number_of_vehicles
    if biggest_update < 1:
        stopping_criterion = True
    return stopping_criterion, dic_lines
