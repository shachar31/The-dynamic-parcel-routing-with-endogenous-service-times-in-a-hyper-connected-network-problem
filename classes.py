import math
from parameters import alpha, daily_arrival_rate


class Line:
    def __init__(self, number, line_stations, travel_time):
        self.line_number = number
        self.line_stations = line_stations
        self.travel_time = travel_time
        self.handle_parcels = {s: {'f': 0, 'b': 0} for s in line_stations}
        self.handle_time = {s: {'f': 0, 'b': 0} for s in line_stations}
        self.dwell_time = {s: {'f': 0, 'b': 0} for s in line_stations}
        self.surplus = {}
        self.shortage = {}
        self.capacity = {}
        self.total_handle_time = 0
        self.number_of_vehicles = 0
        self.period = travel_time
        self.schedule = {s: {'f': 0, 'b': 0} for s in line_stations}
        self.time_between_vehicles = 0
        self.f = 0
        self.bunching = True

    def calculate_number_of_vehicles(self, num_nodes):
        arrival_rate_od = daily_arrival_rate / (num_nodes * (num_nodes - 1))
        self.total_handle_time = 0
        for s in self.line_stations:
            self.handle_parcels[s]['f'] *= arrival_rate_od
            self.handle_parcels[s]['b'] *= arrival_rate_od
            self.total_handle_time += self.handle_parcels[s]['f'] + self.handle_parcels[s]['b']
        self.number_of_vehicles = math.ceil(self.total_handle_time * alpha)

    def calculate_f(self):
        F_c = (self.number_of_vehicles - self.total_handle_time * alpha) / (self.travel_time / 1440)
        F_p = 0
        x = {s: {'f': 0, 'b': 0} for s in self.line_stations}
        while F_c != F_p:
            F_p = F_c
            total_x = 0
            for s in x:
                for d in x[s]:
                    x[s][d] = alpha * math.ceil(self.handle_parcels[s][d] / F_p)
                    total_x += x[s][d]
            F_c = self.number_of_vehicles / (total_x + (self.travel_time / 1440))
        self.f = F_c
        self.calculate_dwell_time(x)

    def calculate_dwell_time(self, x):
        self.period = self.travel_time
        for s in x:
            for d in x[s]:
                self.dwell_time[s][d] = x[s][d] * 1440
                self.period += self.dwell_time[s][d]
        self.time_between_vehicles = self.period / self.number_of_vehicles

    def export_line_data(self, iteration_number):
        data = []
        for s in self.shortage:
            for direction in self.shortage[s]:
                data.append([iteration_number,  # iteration number
                             self.line_number,  # line number
                             s,  # station number
                             direction,  # station direction
                             self.dwell_time[s][direction],  # dwell time according to direction
                             self.shortage[s][direction][0],  # percent of shortage
                             self.shortage[s][direction][1],  # quantity of shortage
                             self.shortage[s][direction][2],  # cost of shortage
                             self.surplus[s][direction][0],  # percent of surplus
                             self.surplus[s][direction][1],  # quantity of surplus
                             self.surplus[s][direction][2],  # cost of surplus
                             self.capacity[s][direction],  # vehicle capacity
                             ])
        return data
#######################################################################################################################


#######################################################################################################################
class Event:
    def __init__(self, event_time, entity, event_type=None):
        self.time = event_time
        self.entity = entity
        self.type = event_type

    def __lt__(self, event2):
        return self.time < event2.time
#######################################################################################################################


#######################################################################################################################
class Parcel:
    def __init__(self, parcel_source, parcel_target, arr_time, num):
        self.source = parcel_source
        self.target = parcel_target
        self.arr_time = arr_time
        self.num = num
        self.prev_line = None
        self.wait_time = 0

    def __lt__(self, parcel2):
        return self.arr_time < parcel2.arr_time

    def __repr__(self):
        return f'( {self.source}, {self.target})'
#######################################################################################################################


#######################################################################################################################
class Vehicle:
    def __init__(self, number, stations_dic, first_station, station_switch, line_station, start_time, vehicle_number,
                 station_to_index, index_to_station, bunching):
        self.line_number = number
        self.stations_dic = stations_dic
        self.curr_station = (first_station, 'f')
        self.end_station = (first_station, 'b')
        self.direction = 'f'
        self.station_switch = station_switch
        self.parcels_on_vehicle = {s: [] for s in line_station}
        self.start_time = start_time
        self.vehicle_number = vehicle_number
        self.station_to_index = station_to_index
        self.index_to_station = index_to_station
        self.total_work_time = 0
        self.bunching = bunching
#######################################################################################################################


#######################################################################################################################
class Path:
    def __init__(self, cost, path):
        self.cost = cost
        self.path = path
        self.change = 0

    def __lt__(self, path2):
        return self.cost < path2.cost
    
    def __repr__(self):
        return f'path: {self.path} ; cost: {self.cost}'
#######################################################################################################################


#######################################################################################################################
class Solution:
    def __init__(self, objective, iteration, parcel_times, lines):
        self.objective = objective
        self.iteration = iteration
        self.parcel_times = parcel_times
        self.lines = lines

