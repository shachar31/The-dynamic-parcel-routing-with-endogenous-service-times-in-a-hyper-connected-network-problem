"""
   Set the parameters to generate the data and the FDT and APR policies experiments.

   - grid_dimension (tuple): Represent the dimensions of the grid configuration.
   - total_travel_time (int): The travel time for the side of the grid configuration square.
   - daily_arrival_rate (int): The total number of parcels that arrive in the system on a daily basis.
   - alpha (float): The handling operation time for each parcel (identical for loading and unloading operations).
   - number_days (int): The duration of the simulation in terms of the number of days.
   - warm_up_duration (int): The warm-up period that will be omitted from the results.

   - network (string): The path of the network data file (Excel file).
                       If None, the program will generate a network data file by the grid configuration and
                       travel time that is defined.

   - parcels_arrivals_times (string): The path of the parcels arrivals time data file (pickle file).
                                      If None, the program will generate a network data file by the grid
                                      configuration and the daily arrival rate that is defined.

   - vehicles_to_add (int): The number of vehicles added to the minimum number.
   - weight (int): The anti-bunching weight parameter for the APR.
   - update_method (int): The update method according to which the dwell times in FDT will be updated.
                          Must be one of the two (1, 2).
   - teg_mode (string): The method of finding the path for the parcel on the TEG:
                        - "min_transfers" - a path that lexicographically minimizes the number of transfers and
                           the delivery time.
                        - "min_time" - a path that minimizes the delivery time of the parcel.
   """

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
