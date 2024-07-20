import pandas as pd
import numpy as np
import heapq
import networkx as nx
import copy
from classes import Event, Path
from parameters import alpha


def create_grid_network_data(rows, columns, basic_travel_time):
    nodes_position = {}
    for m in range(rows):
        for n in range(1, columns+1):
            nodes_position[m * columns + n] = (n * basic_travel_time, m * basic_travel_time)

    graph_data = []
    line_number = 0
    flag = True
    for m in range(rows):
        line_number += 1
        lines_data = []
        lst = []
        for n in range(1, columns):
            if flag:
                from_node = m*columns + n
                to_node = m*columns + n + 1
            else:
                to_node = m*columns + n
                from_node = m*columns + n + 1
            x1, y1 = nodes_position[from_node]
            x2, y2 = nodes_position[to_node]
            travel_time = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            lines_data.append([line_number, from_node, to_node, 'f', travel_time])
            lst.append([line_number, to_node, from_node, 'b', travel_time])
        if flag:
            lines_data += lst[::-1]
            graph_data += lines_data
            flag = False
        else:
            lines_data = lines_data[::-1]
            lines_data += lst
            graph_data += lines_data
            flag = True

    for n in range(1, columns + 1):
        line_number += 1
        lines_data = []
        lst = []
        for m in range(rows - 1):
            if flag:
                from_node = n + m*columns
                to_node = n + (m + 1)*columns
            else:
                to_node = n + m*columns
                from_node = n + (m + 1)*columns
            x1, y1 = nodes_position[from_node]
            x2, y2 = nodes_position[to_node]
            travel_time = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            lines_data.append([line_number, from_node, to_node, 'f', travel_time])
            lst.append([line_number, to_node, from_node, 'b', travel_time])
        if flag:
            lines_data += lst[::-1]
            graph_data += lines_data
            flag = False
        else:
            lines_data = lines_data[::-1]
            lines_data += lst
            graph_data += lines_data
            flag = True

    network = pd.DataFrame(graph_data, columns=['Line', 'from', 'to', 'direction', 'time'])
    return network


def create_parcels_arrivals(stations, lamda, number_days):
    p = []  # List of events
    data = []
    for i in stations:
        for j in stations:
            if i != j:
                arrival_time = np.random.exponential((1/lamda)*24*60)
                heapq.heappush(p, Event(arrival_time, (i, j)))
    t_now = 0
    t_max = number_days*24*60
    while t_now <= t_max:
        event = heapq.heappop(p)
        t_now, parcel = event.time, event.entity
        data.append([parcel[0], parcel[1], t_now])
        y = np.random.exponential((1 / lamda) * 24 * 60)
        heapq.heappush(p, Event(t_now + y, parcel))
    return data


def all_shortest_paths(graph, source, target, dic_of_nodes):
    # Find all the shortest paths between the source to the target
    for line_number in dic_of_nodes[source]:
        graph.add_edge(source, (line_number, source), length=0, direction=None)
    for line_number in dic_of_nodes[target]:
        graph.add_edge((line_number, target), target, length=0, direction=None)

    shortest_paths = []
    paths_generator = nx.all_shortest_paths(graph, source=source, target=target, weight='length')
    for path in paths_generator:
        new_path = path[1:-1]
        shortest_paths.append(new_path)
    return shortest_paths


def calculate_handle_parcels(network_data, stations, lines):
    parcels_max_change = {}
    G = nx.from_pandas_edgelist(network_data, 'from', 'to',
                                edge_attr=['Line', 'direction', 'time'],
                                create_using=nx.DiGraph())
    graph_for_handle_time = nx.DiGraph()
    nodes_dic = {s: set() for s in stations}
    for line_number, source, target, direction, time in network_data.to_numpy():
        graph_for_handle_time.add_edge((line_number, source), (line_number, target), length=time, direction=direction)
        nodes_dic[source].add(line_number)
        nodes_dic[target].add(line_number)
    data_nodes = network_data[['Line', 'from']].drop_duplicates()
    for node in stations:
        node_data = data_nodes[data_nodes['from'] == node].to_numpy()
        for i in range(node_data.shape[0] - 1):
            line_1, _ = node_data[i]
            for line_2, _ in node_data[i + 1:]:
                graph_for_handle_time.add_edge((line_1, node), (line_2, node), length=1000, direction=None)
                graph_for_handle_time.add_edge((line_2, node), (line_1, node), length=1000, direction=None)

    for i in stations:
        for j in stations:
            if i != j:
                # Find all the shortest paths between i to j
                shortest_paths = all_shortest_paths(copy.deepcopy(graph_for_handle_time), i, j, nodes_dic)
                handling_time_to_add = (alpha*1440) / len(shortest_paths)
                for p in shortest_paths:
                    path = [p[0][1]]
                    prev_n = p[0][1]
                    for edge in p[1:]:
                        if edge[1] != prev_n:
                            path.append(edge[1])
                            prev_n = edge[1]

                    parcels_max_change[(i, j)] = 0
                    path_edges = list(zip(path, path[1:]))

                    prev_line = G.edges[path_edges[0]]['Line']
                    prev_line_object = lines[prev_line]
                    prev_direction = G.edges[path_edges[0]]['direction']
                    prev_line_object.handle_parcels[i][prev_direction] += handling_time_to_add
                    parcels_max_change[(i, j)] += 1
                    for e in path_edges[1:]:
                        curr_line = G.edges[e]['Line']
                        direction = G.edges[e]['direction']
                        if prev_line != curr_line:
                            prev_line_object = lines[prev_line]
                            prev_line_object.handle_parcels[e[0]][prev_direction] += handling_time_to_add
                            parcels_max_change[(i, j)] += 1

                            line_object = lines[curr_line]
                            line_object.handle_parcels[e[0]][direction] += handling_time_to_add
                            parcels_max_change[(i, j)] += 1
                        prev_line = curr_line
                        prev_direction = direction

                    prev_line_object = lines[prev_line]
                    prev_line_object.handle_parcels[j][prev_direction] += handling_time_to_add
                    parcels_max_change[(i, j)] += 1
    return parcels_max_change, lines


def add_path(path):
    data = []
    target = path[-1][1]
    line_number_up, curr_node = path[0]
    
    path_edges = list(zip(path, path[1:]))
    for e in path_edges:
        line_1, node = e[0]
        line_2, node = e[1]
        if line_1 != line_2:
            station_down = node
            data.append([curr_node, target, line_number_up, station_down])
            curr_node = node
            line_number_up = line_2
    station_down = target
    data.append([curr_node, target, line_number_up, station_down])
    return data


def min_transfers_path(network_data, max_change, graph, source, target):
    P = []
    B = []

    data_nodes = network_data[['Line', 'from']].drop_duplicates()
    source_nodes = data_nodes[data_nodes['from'] == source].to_numpy()

    graph[source] = {}
    for i in range(source_nodes.shape[0] - 1):
        line_1, _ = source_nodes[i]
        for line_2, _ in source_nodes[i + 1:]:
            del graph[(line_1, source)][(line_2, source)]
            del graph[(line_2, source)][(line_1, source)]
            heapq.heappush(B, Path(0, [(line_2, source)]))
            heapq.heappush(B, Path(0, [(line_1, source)]))

    target_nodes = data_nodes[data_nodes['from'] == target].to_numpy()
    for i in range(target_nodes.shape[0] - 1):
        line_1, _ = target_nodes[i]
        for line_2, _ in target_nodes[i + 1:]:
            del graph[(line_1, target)][(line_2, target)]
            del graph[(line_2, target)][(line_1, target)]

    while B:
        curr_path = heapq.heappop(B)
        u = curr_path.path[-1]
        if u[1] == target:
            P.append(curr_path)
        else:
            for v in graph[u]:
                if v not in curr_path.path:
                    if v[0] != u[0]:
                        if curr_path.change + 1 <= (max_change - 2) / 2:
                            new_path = copy.deepcopy(curr_path)
                            new_path.path += [v]
                            new_path.cost += graph[u][v][0]
                            new_path.change += 1
                            heapq.heappush(B, new_path)
                    else:
                        new_path = copy.deepcopy(curr_path)
                        new_path.path += [v]
                        new_path.cost += graph[u][v][0]
                        heapq.heappush(B, new_path)
    return P


def find_min_transfers_paths(network_data, stations, parcels_max_change):
    paths_data = []
    graph = {}
    for line_number, source, target, direction, time in network_data.to_numpy():
        if (line_number, source) not in graph:
            graph[(line_number, source)] = {}
        graph[(line_number, source)][(line_number, target)] = [time, direction]
    data_nodes = network_data[['Line', 'from']].drop_duplicates()
    for node in stations:
        node_data = data_nodes[data_nodes['from'] == node].to_numpy()
        for i in range(node_data.shape[0] - 1):
            line_1, _ = node_data[i]
            for line_2, _ in node_data[i + 1:]:
                graph[(line_1, node)][(line_2, node)] = [1000, None]
                graph[(line_2, node)][(line_1, node)] = [1000, None]

    for i in stations:
        for j in stations:
            if i != j:
                P = min_transfers_path(network_data, parcels_max_change[(i, j)], copy.deepcopy(graph), i, j)
                for path in P:
                    paths_data += add_path(path.path)

    paths_data = pd.DataFrame(paths_data, columns=['curr_node', 'target', 'line_number_up', 'station_down'])
    return paths_data
