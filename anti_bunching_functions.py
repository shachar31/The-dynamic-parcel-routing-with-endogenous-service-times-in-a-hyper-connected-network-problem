def calculate_time_behind(vehicle, vehicle_behind, L, paths_data):
    time = 0
    vehicle_station_index = vehicle.station_to_index[vehicle.curr_station]
    vehicle_behind_station_index = vehicle_behind.station_to_index[vehicle_behind.curr_station]
    if vehicle_station_index > vehicle_behind_station_index:
        for i in range(vehicle_behind_station_index, vehicle_station_index):
            station = vehicle_behind.index_to_station[i]
            # Adding the travel time between i to i+1 to the time calculation
            time += vehicle_behind.stations_dic[station][1]
            # Adding the working time at station i to the time calculation
            time += len(vehicle_behind.parcels_on_vehicle[station[0]])
            for parcel in L[station[0]]:
                if parcel.prev_line != vehicle_behind.line_number:
                    x = (paths_data[:, 0] == station[0]) & (paths_data[:, 1] == parcel.target)
                    lines_up = paths_data[x, 2]
                    if vehicle_behind.line_number in lines_up:
                        time += 1
        # Adding the working time at vehicle station to the time calculation
        time += len(vehicle_behind.parcels_on_vehicle[vehicle.curr_station[0]])
        for parcel in L[vehicle.curr_station[0]]:
            if parcel.prev_line != vehicle_behind.line_number:
                x = (paths_data[:, 0] == vehicle.curr_station[0]) & (paths_data[:, 1] == parcel.target)
                lines_up = paths_data[x, 2]
                if vehicle_behind.line_number in lines_up:
                    time += 1
    else:
        if vehicle.start_time < vehicle_behind.start_time:
            for i in range(vehicle_station_index, vehicle_behind_station_index):
                station = vehicle.index_to_station[i]
                # Adding the travel time between i to i+1 to the time calculation
                time += vehicle.stations_dic[station][1]
                # Adding the working time at station i to the time calculation
                time += len(vehicle.parcels_on_vehicle[station[0]])
                for parcel in L[station[0]]:
                    if parcel.prev_line != vehicle.line_number:
                        x = (paths_data[:, 0] == station[0]) & (paths_data[:, 1] == parcel.target)
                        lines_up = paths_data[x, 2]
                        if vehicle.line_number in lines_up:
                            time += 1
            # Adding the working time at vehicle station to the time calculation
            time += len(vehicle.parcels_on_vehicle[vehicle.curr_station[0]])
            for parcel in L[vehicle.curr_station[0]]:
                if parcel.prev_line != vehicle.line_number:
                    x = (paths_data[:, 0] == vehicle.curr_station[0]) & (paths_data[:, 1] == parcel.target)
                    lines_up = paths_data[x, 2]
                    if vehicle.line_number in lines_up:
                        time += 1
            time = -time

        else:
            end_station_index = vehicle.station_to_index[vehicle.end_station]
            for i in range(vehicle_behind_station_index, end_station_index):
                station = vehicle_behind.index_to_station[i]
                # Adding the travel time between i to i+1 to the time calculation
                time += vehicle_behind.stations_dic[station][1]
                # Adding the working time at station i to the time calculation
                time += len(vehicle_behind.parcels_on_vehicle[station[0]])
                for parcel in L[station[0]]:
                    if parcel.prev_line != vehicle_behind.line_number:
                        x = (paths_data[:, 0] == station[0]) & (paths_data[:, 1] == parcel.target)
                        lines_up = paths_data[x, 2]
                        if vehicle_behind.line_number in lines_up:
                            time += 1

            for i in range(1, vehicle_station_index):
                station = vehicle_behind.index_to_station[i]
                # Adding the travel time between i to i+1 to the time calculation
                time += vehicle_behind.stations_dic[station][1]
                # Adding the working time at station i to the time calculate
                for parcel in L[station[0]]:
                    if parcel.prev_line != vehicle_behind.line_number:
                        x = (paths_data[:, 0] == station[0]) & (paths_data[:, 1] == parcel.target)
                        lines_up = paths_data[x, 2]
                        if vehicle_behind.line_number in lines_up:
                            time += 1
                            # Adding the working time at vehicle station to the time calculation
            time += len(vehicle_behind.parcels_on_vehicle[vehicle.curr_station[0]])
            for parcel in L[vehicle.curr_station[0]]:
                if parcel.prev_line != vehicle.line_number:
                    x = (paths_data[:, 0] == vehicle.curr_station[0]) & (paths_data[:, 1] == parcel.target)
                    lines_up = paths_data[x, 2]
                    if vehicle_behind.line_number in lines_up:
                        time += 1
    return time
#######################################################################################################################


#######################################################################################################################
def calculate_time_in_front(vehicle, vehicle_in_front, L, paths_data):
    time = 0
    vehicle_station_index = vehicle.station_to_index[vehicle.curr_station]
    vehicle_in_front_station_index = vehicle_in_front.station_to_index[vehicle_in_front.curr_station]
    if vehicle_station_index < vehicle_in_front_station_index:
        # Adding the travel time between current station to next station to the time calculation
        time += vehicle.stations_dic[vehicle.curr_station][1]
        for i in range(vehicle_station_index + 1, vehicle_in_front_station_index):
            station = vehicle.index_to_station[i]
            # Adding the travel time between i to i+1 to the time calculation
            time += vehicle.stations_dic[station][1]
            # Adding the working time at station i to the time calculation
            time += len(vehicle.parcels_on_vehicle[station[0]])
            for parcel in L[station[0]]:
                if parcel.prev_line != vehicle.line_number:
                    x = (paths_data[:, 0] == station[0]) & (paths_data[:, 1] == parcel.target)
                    lines_up = paths_data[x, 2]
                    if vehicle.line_number in lines_up:
                        time += 1
        # Adding the working time at vehicle station to the time calculation
        time += len(vehicle.parcels_on_vehicle[vehicle_in_front.curr_station[0]])
        for parcel in L[vehicle_in_front.curr_station[0]]:
            if parcel.prev_line != vehicle.line_number:
                x = (paths_data[:, 0] == vehicle_in_front.curr_station[0]) & (paths_data[:, 1] == parcel.target)
                lines_up = paths_data[x, 2]
                if vehicle.line_number in lines_up:
                    time += 1
    else:
        if vehicle.start_time > vehicle_in_front.start_time:
            for i in range(vehicle_in_front_station_index, vehicle_station_index):
                station = vehicle.index_to_station[i]
                # Adding the travel time between i to i+1 to the time calculation
                time += vehicle.stations_dic[station][1]
                # Adding the working time at station i to the time calculation
                time += len(vehicle.parcels_on_vehicle[station[0]])
                for parcel in L[station[0]]:
                    if parcel.prev_line != vehicle.line_number:
                        x = (paths_data[:, 0] == station[0]) & (paths_data[:, 1] == parcel.target)
                        lines_up = paths_data[x, 2]
                        if vehicle.line_number in lines_up:
                            time += 1
            time = -time
        else:
            end_station_index = vehicle.station_to_index[vehicle.end_station]
            for i in range(vehicle_station_index, end_station_index):
                station = vehicle.index_to_station[i]
                # Adding the travel time between i to i+1 to the time calculation
                time += vehicle.stations_dic[station][1]
                # Adding the working time at station i to the time calculation
                time += len(vehicle.parcels_on_vehicle[station[0]])
                for parcel in L[station[0]]:
                    if parcel.prev_line != vehicle.line_number:
                        x = (paths_data[:, 0] == station[0]) & (paths_data[:, 1] == parcel.target)
                        lines_up = paths_data[x, 2]
                        if vehicle.line_number in lines_up:
                            time += 1
            for i in range(1, vehicle_in_front_station_index):
                station = vehicle.index_to_station[i]
                # Adding the travel time between i to i+1 to the time calculation
                time += vehicle.stations_dic[station][1]
                # Adding the working time at station i to the time calculate
                for parcel in L[station[0]]:
                    if parcel.prev_line != vehicle.line_number:
                        x = (paths_data[:, 0] == station[0]) & (paths_data[:, 1] == parcel.target)
                        lines_up = paths_data[x, 2]
                        if vehicle.line_number in lines_up:
                            time += 1
                            # Adding the working time at vehicle station to the time calculation
            time += len(vehicle.parcels_on_vehicle[vehicle_in_front.curr_station[0]])
            for parcel in L[vehicle_in_front.curr_station[0]]:
                if parcel.prev_line != vehicle.line_number:
                    x = (paths_data[:, 0] == vehicle_in_front.curr_station[0]) & (paths_data[:, 1] == parcel.target)
                    lines_up = paths_data[x, 2]
                    if vehicle.line_number in lines_up:
                        time += 1
    return time
