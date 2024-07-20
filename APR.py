import numpy as np
import pandas as pd
import pickle
import heapq
from parameters import alpha, warm_up_duration, number_days, weight, vehicles_to_add
from classes import Event, Parcel, Vehicle
from anti_bunching_functions import calculate_time_behind, calculate_time_in_front


# Network data
network_data = pd.read_excel(f'data/network_data.xlsx', index_col=0)
stations = network_data['from'].unique()

# The parcels paths
paths_data = pd.read_excel(f'data/paths_data_min_transfers.xlsx', index_col=0)
paths_data = paths_data.drop_duplicates().to_numpy()

# Parcels arrivals time
parcels_arrivals = pickle.load(open(f'data/parcels_arrivals_times.p', 'rb'))

lines = pickle.load(open(f'data/lines.p', 'rb'))
num_nodes = len(stations)
for line in lines.values():
    line.calculate_number_of_vehicles(num_nodes)
    line.number_of_vehicles += vehicles_to_add
    line.time_between_vehicles = line.travel_time / line.number_of_vehicles
    if line.number_of_vehicles == 1 or weight == 0:
        line.bunching = False

p = []  # List of events
num_parcel = 0
num_parcel_finish = 0
L = {s: [] for s in stations}
parcel_times = []
vehicles_times = []
vehicles = {line: {c: None for c in range(lines[line].number_of_vehicles)} for line in lines}

for parcel_source, parcel_target, arr_time in parcels_arrivals:
    num_parcel += 1
    parcel = Parcel(parcel_source, parcel_target, arr_time, num_parcel)
    heapq.heappush(p, Event(arr_time, parcel, 'Parcel_Arrival'))

for line in lines.values():
    line_data = network_data[network_data.Line == line.line_number].iloc[:, 1:].to_numpy()
    stations_dic = {}
    station_to_index = {}
    index_to_station = {}
    station_index = 0
    prev_direction = 'f'
    station_switch = None
    target, direction = None, None
    for source, target, direction, travel_time in line_data:
        stations_dic[(source, direction)] = (target, travel_time)
        station_index += 1
        station_to_index[(source, direction)] = station_index
        index_to_station[station_index] = (source, direction)
        if prev_direction != direction:
            station_switch = source
        prev_direction = direction
    station_to_index[(target, direction)] = station_index + 1
    index_to_station[station_index + 1] = (target, direction)

    for vehicle_number in range(line.number_of_vehicles):
        t = vehicle_number * line.time_between_vehicles
        vehicle = Vehicle(line.line_number, stations_dic, line_data[0][0], station_switch, line.line_stations, t,
                          vehicle_number, station_to_index, index_to_station, line.bunching)
        vehicles[line.line_number][vehicle_number] = vehicle
        heapq.heappush(p, Event(t, vehicle, 'Vehicle_Stop'))

while num_parcel != num_parcel_finish:
    event = heapq.heappop(p)
    T_now = event.time

    if event.type == 'Parcel_Arrival':
        parcel = event.entity
        heapq.heappush(L[parcel.source], parcel)

    if event.type == 'Vehicle_Stop':
        vehicle = event.entity

        work_time = 0
        while vehicle.parcels_on_vehicle[vehicle.curr_station[0]]:
            parcel = heapq.heappop(vehicle.parcels_on_vehicle[vehicle.curr_station[0]])
            work_time += alpha*1440
            vehicle.total_work_time += alpha*1440
            if parcel.target == vehicle.curr_station[0]:
                num_parcel_finish += 1
                if T_now > warm_up_duration*1440:
                    parcel_times.append(T_now + work_time - parcel.arr_time)
            else:
                parcel.prev_line = vehicle.line_number
                heapq.heappush(L[vehicle.curr_station[0]], parcel)

        parcel_to_return = []
        vehicle_in_front = vehicles[vehicle.line_number][(vehicle.vehicle_number - 1) %
                                                         lines[vehicle.line_number].number_of_vehicles]
        vehicle_behind = vehicles[vehicle.line_number][(vehicle.vehicle_number + 1) %
                                                       lines[vehicle.line_number].number_of_vehicles]
        total_work_time_down = work_time
        while L[vehicle.curr_station[0]]:
            if vehicle.bunching:
                if work_time > total_work_time_down:
                    time_in_front = calculate_time_in_front(vehicle, vehicle_in_front, L, paths_data)
                    time_behind = calculate_time_behind(vehicle, vehicle_behind, L, paths_data)
                    if time_behind <= time_in_front * weight:
                        break
            parcel = heapq.heappop(L[vehicle.curr_station[0]])
            if parcel.prev_line != vehicle.line_number:
                x = (paths_data[:, 0] == vehicle.curr_station[0]) & (paths_data[:, 1] == parcel.target)
                lines_up = paths_data[x, 2]
                if vehicle.line_number in lines_up:
                    x = (paths_data[:, 0] == vehicle.curr_station[0]) & \
                        (paths_data[:, 1] == parcel.target) & \
                        (paths_data[:, 2] == vehicle.line_number)
                    station_down = paths_data[x, 3][0]
                    heapq.heappush(vehicle.parcels_on_vehicle[station_down], parcel)
                    work_time += alpha*1440
                    vehicle.total_work_time += alpha*1440
                else:
                    parcel_to_return.append(parcel)
            else:
                parcel_to_return.append(parcel)
        q = 0
        for parcel in L[vehicle.curr_station[0]]:
            if parcel.prev_line != vehicle.line_number:
                x = (paths_data[:, 0] == vehicle.curr_station[0]) & (paths_data[:, 1] == parcel.target)
                lines_up = paths_data[x, 2]
                if vehicle.line_number in lines_up:
                    q += 1

        for parcel in parcel_to_return:
            heapq.heappush(L[vehicle.curr_station[0]], parcel)

        if warm_up_duration * 1440 <= T_now <= number_days * 1440:
            vehicles_times.append([vehicle.line_number, vehicle.vehicle_number, vehicle.curr_station[0],
                                   vehicle.curr_station[1], T_now, work_time, q, len(L[vehicle.curr_station[0]])])

        if vehicle.curr_station == vehicle.end_station:
            vehicle_next_station, travel_time = vehicle.end_station[0], 0
            vehicle.direction = 'f'
            vehicle.start_time = T_now + work_time
        else:
            vehicle_next_station, travel_time = vehicle.stations_dic[vehicle.curr_station]
            if vehicle_next_station == vehicle.station_switch:
                vehicle.direction = 'b'
        vehicle.curr_station = (vehicle_next_station, vehicle.direction)
        heapq.heappush(p, Event(T_now + work_time + travel_time, vehicle, 'Vehicle_Stop'))

vehicles_times = pd.DataFrame(vehicles_times, columns=['Line', 'Vehicle', 'Station', 'Direction',
                                                       'Entry time', 'Work time', 'Shortages', 'Queue'])
vehicles_times.to_excel(f'results/vehicles_times.xlsx')

print(f'APR - Mean delivery time {np.mean(parcel_times)} [min]')
