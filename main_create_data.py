import pandas as pd
import pickle
import os
from classes import Line
from create_data import create_grid_network_data, create_parcels_arrivals, calculate_handle_parcels
from create_data import find_min_transfers_paths
from parameters import number_days, grid_dimension, daily_arrival_rate, total_travel_time, network,\
    parcels_arrivals_times


# Create a data folder
if not os.path.exists('data'):
    os.makedirs('data')

if network:
    network_data = pd.read_excel(network, index_col=0)
else:
    rows, columns = grid_dimension
    network_data = create_grid_network_data(rows, columns, total_travel_time / (rows - 1))

network_data.to_excel(f'data/network_data.xlsx')

lines_numbers = network_data['Line'].unique()
stations = network_data['from'].unique()

lines = {}
for line_num in lines_numbers:
    lines[line_num] = Line(line_num,
                           network_data['from'][network_data.Line == line_num].unique(),
                           network_data['time'][network_data.Line == line_num].sum())

parcels_max_transfers, lines = calculate_handle_parcels(network_data, stations, lines)
pickle.dump(parcels_max_transfers, open(f'data/parcels_max_transfers.p', "wb"))
pickle.dump(lines, open(f'data/lines.p', "wb"))

paths_data = find_min_transfers_paths(network_data, stations, parcels_max_transfers)
paths_data.to_excel(f'data/paths_data_min_transfers.xlsx')

if parcels_arrivals_times:
    parcels_arrivals = pickle.load(open(parcels_arrivals_times, 'rb'))
else:
    num_nodes = len(stations)
    arrival_rate_od = daily_arrival_rate / (num_nodes * (num_nodes - 1))
    parcels_arrivals = create_parcels_arrivals(stations, arrival_rate_od, number_days)

pickle.dump(parcels_arrivals, open(f'data/parcels_arrivals_times.p', "wb"))
