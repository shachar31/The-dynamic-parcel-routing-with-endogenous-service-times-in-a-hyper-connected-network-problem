import numpy as np
import pandas as pd
import pickle
import copy
from fdt_functions import sim, create_graph, update_dwell_time
from classes import Solution
from parameters import alpha, daily_arrival_rate, update_method, teg_mode, vehicles_to_add, max_iterations


# Network data
network_data = pd.read_excel(f'data/network_data.xlsx', index_col=0)
stations = network_data['from'].unique()

parcels_arrivals = pickle.load(open(f'data/parcels_arrivals_times.p', 'rb'))
lines = pickle.load(open(f'data/lines.p', 'rb'))
num_nodes = len(stations)
arrival_rate_od = daily_arrival_rate / (num_nodes * (num_nodes - 1))
for line in lines.values():
    line.calculate_number_of_vehicles(arrival_rate_od, alpha)
    line.number_of_vehicles += vehicles_to_add
    line.calculate_f(alpha)

    line_data = network_data[network_data.Line == line.line_number].iloc[:, 1:].to_numpy()
    prev_direction = 'b'
    for source, target, direction, travel_time in line_data:
        if prev_direction != direction:
            dwell_time = line.dwell_time[source][prev_direction] + line.dwell_time[source][direction]
            line.dwell_time[source] = {None: dwell_time}
            line.surplus[source] = {None: 0}
            line.shortage[source] = {None: 0}
            line.capacity[source] = {None: 0}
        else:
            line.surplus[source] = {'f': 0, 'b': 0}
            line.shortage[source] = {'f': 0, 'b': 0}
            line.capacity[source] = {'f': 0, 'b': 0}
        prev_direction = direction

if teg_mode == 'min_transfers':
    parcels_max_change = pickle.load(open(f'data/parcels_max_transfers.p', 'rb'))
else:
    parcels_max_change = None

results_data = []
objective = []
iterations_no_improvement = 0
iteration_number = 1
update_size = 1
stopping_criterion = False

graph = create_graph(network_data, stations, lines)
parcel_times, lines = sim(iteration_number, graph, parcels_arrivals, lines, parcels_max_change)
avg_arr_time = np.array(parcel_times)[:, 2].mean()
objective.append([iteration_number, avg_arr_time])

first_sol = avg_arr_time

for line in lines.values():
    export_data = line.export_line_data(iteration_number)
    results_data += export_data

initial_solution = Solution(avg_arr_time, iteration_number, parcel_times, lines)
best_solution = copy.deepcopy(initial_solution)

while not stopping_criterion:
    prev_lines = copy.deepcopy(lines)
    stopping_criterion, lines = update_dwell_time(lines, update_size)
    iteration_number += 1
    graph = create_graph(network_data, stations, lines)
    parcel_times, lines = sim(iteration_number, graph, parcels_arrivals, lines, parcels_max_change)
    avg_arr_time = np.array(parcel_times)[:, 2].mean()
    objective.append([iteration_number, avg_arr_time])

    for line in lines.values():
        export_data = line.export_line_data(iteration_number)
        results_data += export_data

    if avg_arr_time < best_solution.objective:
        best_solution = Solution(avg_arr_time, iteration_number, parcel_times, lines)
        iterations_no_improvement = 0
    else:
        update_size *= 0.9
        if update_method == 2:
            iterations_no_improvement += 1
            if iterations_no_improvement >= max_iterations:
                stopping_criterion = True
        else:
            # Return to the previous solution
            update_size *= 0.9
            lines = copy.deepcopy(prev_lines)
print(f'FDT :')
print(f'The initial solution: {first_sol}')
print(f'The final solution was {best_solution.objective} and obtained at iteration {best_solution.iteration}')
print(' ')

indicators_dwell_time_capacity = pd.DataFrame(results_data, columns=['Iteration', 'Line', 'Station',
                                                                     'Direction', 'Stay time (units of parcels)',
                                                                     'Percent of shortage', 'Quantity of shortage',
                                                                     'Cost of shortage', 'Percent of surplus',
                                                                     'Quantity of surplus', 'Cost of surplus',
                                                                     'vehicle capacity'])
indicators_dwell_time_capacity.to_excel(f'dwell_time_capacity.xlsx')

objective_FDT = pd.DataFrame(objective, columns=['Iteration', 'Objective (FDT)'])
objective_FDT.to_excel('objective_FDT.xlsx')
