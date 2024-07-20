grid_dimension = (5, 5)
total_travel_time = 60
daily_arrival_rate = 5000
alpha = 1 / 1440
number_days = 50
warm_up_duration = 10

network = f'data/network_data_{grid_dimension}.xlsx'
parcels_arrivals_times = f'data/parcels_arrivals_times_{grid_dimension}_{daily_arrival_rate}.p'

vehicles_to_add = 1
weight = 0.5
update_method = 1
teg_mode = 'min_transfers'
max_iterations = 10
