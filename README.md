# Dynamic Parcel Routing with Endogenous Service Times in a Hyper-Connected Network

This project implements a system to optimize parcel routing and delivery times within a hyper-connected grid network using advanced transportation algorithms including Fixed Dwell Time (FDT) and Anti-bunching Priority Routing (APR).

## Project Structure
- `parameters.py`: Sets up the problem parameters and other parameters used by the algorithms, detailed below.
- `create_data.py`: Functions for creating grid network data and generating parcel arrivals.
- `main_create_data.py`: Data generation.
- `FDT.py`: Implements the Fixed Dwell Time policy.
- `APR.py`: Implements the Adaptive Parcel Routing policy.
- `fdt_functions.py`: Contains helper functions for the FDT algorithm.
- `anti_bunching_functions.py`: Contains helper functions used by the APR algorithm for the anti-bunching mechanism.
- `classes.py`: Contains helper class used throughout the project.


## Setup:
1. **Install the required packages:**
   ```
   pip install -r requirements.txt
   ```
   
3. **Setting the parameters:**
  Start by setting the `parameters.py`:
   - `grid_dimension (tuple)`: Represent the dimensions of the grid configuration.
   - `total_travel_time (int)`: The travel time for the side of the grid configuration square.
   - `daily_arrival_rate (int)`: The total number of parcels that arrive in the system on a daily basis.
   - `alpha (float)`: The handling operation time for each parcel (identical for loading and unloading operations).
   - `number_days (int)`: The duration of the simulation in terms of the number of days.
   - `warm_up_duration (int)`: The warm-up period that will be omitted from the results.

   - `network (string)`: The path of the network data file (Excel file).
     If None, the program will generate a network data file by the grid configuration and travel time that is defined.

   - `parcels_arrivals_times (string)`: The path of the parcels arrivals time data file (pickle file).
     If None, the program will generate a network data file by the grid configuration and the daily arrival rate that is defined.

   - `vehicles_to_add (int)`: The number of vehicles added to the minimum number.
   - `weight (int)`: The anti-bunching weight parameter for the APR.
   - `update_method (int)`: The update method according to which the dwell times in FDT will be updated. Must be one of the two (1, 2).
   - `teg_mode (string)`: The method of finding the path for the parcel on the TEG:
       - "min_transfers" - a path that lexicographically minimizes the number of transfers and the delivery time.
       - "min_time" - a path that minimizes the delivery time of the parcel.
   - `max_iterations (int)`: The stopping criterion of the simulation-based search algorithm for update method 2

  4. **Data generation:**
  ```
  python main_create_data.py
  ```

## Run the FDT and APR algorithms:
  ```
  python FDT.py
  ```
 ```
  python APR.py
  ```


## Descriptions of Data Files
- **`network_data:`**
  This Excel file represents the network configuration including SPs and travel times. The file includes the following columns:
     - `Line`: The identifier for a vehicle route.
     - `From`: The starting SP of a leg within the vehicle route.
     - `To`: The ending SP of a leg within the vehicle route.
     - `Direction`: Indicates the direction of travel between SPs, typically noted as 'f' for forward or 'b' for backward.
     - `Time`: The travel time required to move from the `from` SP to the `to` SP.
- **`parcels_arrivals_times.p:`**
  This is a serialized Python pickle file containing the simulated arrival times of parcels within the network. It is based on a simulation scenario for a network configuration with a daily arrival rate. The file contains data structured as lists detailing each parcel's source, destination, and arrival time at the network.



## Results:
   - **FDT**:
     - `dwell_time_capacity.xlsx` - includes the dwell times at each stop along the vehicle route at each iteration of the algorithm, along with measures of surplus and shortage of the dwell time and the vehicle capacities.
     - `objective_FDT.xlsx` - includes the mean delivery time of the parcels across each iteration.
     - The algorithm also prints the value of the initial solution, the value of the final solution, and in which iteration the final solution was observed

  - **APR**:
      - `vehicles_times.xlsx` - includes detailed timings for each vehicle stop and work times at stops. This data is crucial for analyzing the effectiveness of anti-bunching.
      - The algorithm also prints the mean delivery times for parcels.

