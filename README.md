# JustInTime-Container-Pooling

## Movehack Submission for Problem Statement 2  
## Multi-modal Freight handling and Transportation

Design and build a common platform which helps in increasing the efficiency of ports and freight train terminals for
loading, unloading and transportation of goods in order to increase handling capacity, reduce dwell time, increase
throughput and provide multi-modal transport options in an efficient manner.

## Solution Overview  

Planning container movement from source till port is similar to travelling salesman problem with goals to reduce overall
transit time of vehicles involved and reduce bottlenecks at CFS,  Port or ICD. In order to generate optimal plan for 
truck/train movement so that required containers will reach port for export just in time, multiple factors like container sizes, 
load category, vehicle types, service times at CFS, loading and unloading time, clearance time, travelling time etc needs to be
considered. Optimal solution depends on right combination of above factors and identifying optimal solution is NP-Hard problem.
Idea is to generate number of feasible solutions and find optimal solution using Genetic Algorithm.

## Data Used  
 JNPT Port Shipping Data (Export)
 For Demo 5 days data from month of June is considered

## Demo solution
  Show loading Plan will give scheduled arrival time for vehicles at the dock such that it minimises the average dwell time for all    vehicles.
  Direct to Port vehicles as well as those from ICD/CFS can be accommodated.
  Routing plan can be further optimized using Genetic Algorithm (WIP). 
  Warehouse (CFS/ICD/DPD) Users can set their vehicle availability can be used to accommodate goods train time table (current page is for demo purpose only).
  If ship route info available can also provide optimal loading pattern (which can be used to further optimize vehicle arrival timings)

## Future scope 
 Solution can also be extended to provide plan for outbound vehicles for imports.
