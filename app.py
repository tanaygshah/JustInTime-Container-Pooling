# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 15:27:53 2018

@author: Tanay_Shah
"""
import itertools
import datetime
import time
import random
import sys
import pandas as pd
import numpy as np
from flask import request , jsonify , render_template, make_response, Flask
import json

app = Flask(__name__, template_folder='webapp', static_folder = 'webapp/static', static_url_path='/webapp/static')

todays_arrivals= [] 
all_available_vehicles = []
all_containers_to_ship = [] 
all_warehouses = []

class Container():
    
    container_id = itertools.count().next
    """
    States of container
    -
    """
    def to_dict(self):
        return {
            "source" : self.source,
            "destination" : self.destination,
            "mode_of_travel" : self.mode_of_travel,
            "ship" : self.ship,
            "current_status" : self.current_status,
            "current_location" : self.current_location,
            "next_hop" : self.next_hop,
            "land_vehicle" : self.land_vehicle,
            "id" : self.id
        }
        
    def __init__(self, source, destination, mode_of_travel, ship, current_status, current_location, next_hop, land_vehicle, container_no="NA"):
        self.source = source
        self.destination = destination
        self.mode_of_travel = mode_of_travel
        self.ship = ship
        self.current_status = current_status
        self.current_location = current_location
        self.next_hop = next_hop
        self.land_vehicle = land_vehicle
        if container_no != "NA":
            self.id = container_no
        else:
            self.id = Container.container_id()
        

class Land_Vehicle():
    
    def __init__(self, vehicle_id, vehice_type, for_warehouse, max_containers = 1):
        self.id = vehicle_id
        self.for_warehouse = for_warehouse
        self.containers_list = []
        self.max_containers = max_containers
        
    def load_vehicle(self, containers):
        if len(containers) <= self.max_containers:
            for container in containers:
                self.containers_list.append(container.id)
                container.land_vehicle = self.id
        else:
            raise Exception('number of containers to load should not exceed max containers')
            
class Ship():
    def __init__(self, ship_name, next_stop, route, next_stop_docking_time, next_stop_departure_time):
        self.name = ship_name
        self.route = route
        self.next_stop = next_stop
        self.next_stop_docking_time = next_stop_docking_time
        self.next_stop_departure_time = next_stop_departure_time
        self.containers = []
        
    def load_containers(self, containers):
        for container in containers:
                self.containers.append(container)
               
    def get_basic_loading_plan(self):
        containers_df = pd.DataFrame.from_records([container.to_dict() for container in self.containers])
        container_df_grp = containers_df.groupby(['current_location', 'mode_of_travel'], as_index=False).agg({'id':lambda x: tuple(x) })
        routing_schedule = {"scheduled_vehicles" : []}
        last_vehicle_time = self.next_stop_departure_time
        warehouse_train_count = {}
        warehouse_truck_count = {}
        for i in range(0, len(container_df_grp)):
            if container_df_grp['mode_of_travel'].iloc[i] == "RAIL":
                if container_df_grp['current_location'].iloc[i] in warehouse_train_count.keys():
                    pass
                else:
                    warehouse_train_count[container_df_grp['current_location'].iloc[i]] = 0
                warehouse_train_count[container_df_grp['current_location'].iloc[i]] = warehouse_train_count[container_df_grp['current_location'].iloc[i]] +1
                routing_schedule['scheduled_vehicles'].append({
                            "time": last_vehicle_time - 1000,
                            "vehicle_type": "Train",
                            "containers": list(container_df_grp['id'].iloc[i]),
                            "vehicle_detail": "Train " + str(warehouse_train_count[container_df_grp['current_location'].iloc[i]]) + " from " + str(container_df_grp['current_location'].iloc[i])
                        })
                last_vehicle_time = last_vehicle_time - 1000
            else:
                if container_df_grp['current_location'].iloc[i] in warehouse_truck_count.keys():
                    pass
                else:
                    warehouse_truck_count[container_df_grp['current_location'].iloc[i]] = 0
                for j in range(0, len(container_df_grp['id'].iloc[i])):
                    
                    warehouse_truck_count[container_df_grp['current_location'].iloc[i]] = warehouse_truck_count[container_df_grp['current_location'].iloc[i]] +1
                    routing_schedule['scheduled_vehicles'].append({
                                "time": last_vehicle_time - 300,
                                "vehicle_type": "Truck",
                                "containers": [container_df_grp['id'].iloc[i][j]],
                                "vehicle_detail": "Truck " + str(warehouse_truck_count[container_df_grp['current_location'].iloc[i]]) + " from " + str(container_df_grp['current_location'].iloc[i])
                            })
                    last_vehicle_time = last_vehicle_time - 300
        return routing_schedule
                            
class Warehouse():
    def __init__(self, name, warehouse_type, address, latitude, longitude):
        self.name = name
        self.type= warehouse_type
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.vehicles_available = []
        self.containers = []
        
    def set_available_vehicles(self, vehicle_details):
        for vehicle_detail in vehicle_details:
            self.vehicles_available.append({"vehicle": vehicle_detail['vehicle'], "slot_start": vehicle_detail['slot_start'], "slot_end": vehicle_detail['slot_end']})
     
        
def create_virtual_data():
    #create ships
    todays_arrivals = []
    todays_arrivals.append(Ship('Maipo', ['Port Qasim', 'Nhava Sheva', 'Mundra', 'DamiettaNewark', 'Norfolk', \
                                  'Savannah', 'Charleston'], 'Nhava Sheva', \
                                  time.mktime(datetime.datetime(2018,datetime.datetime.now().month, datetime.datetime.now().day,5,0,0).timetuple()),\
                                  time.mktime(datetime.datetime(2018,datetime.datetime.now().month, datetime.datetime.now().day,8,45,0).timetuple())))
    todays_arrivals.append(Ship('Northern Guild', ['Jebel Ali','Mundra','Nhava Sheva','Abu Dhabi'], 'Nhava Sheva', \
                                  time.mktime(datetime.datetime(2018,datetime.datetime.now().month, datetime.datetime.now().day,9,0,0).timetuple()),\
                                  time.mktime(datetime.datetime(2018,datetime.datetime.now().month, datetime.datetime.now().day,11,0,0).timetuple())))
    todays_arrivals.append(Ship('Wan Hai 507', ['Nhava Sheva', 'Port Klang'], 'Nhava Sheva', \
                                  time.mktime(datetime.datetime(2018,datetime.datetime.now().month, datetime.datetime.now().day,11,5,0).timetuple()),\
                                  time.mktime(datetime.datetime(2018,datetime.datetime.now().month, datetime.datetime.now().day,12,20,0).timetuple())))
    todays_arrivals.append(Ship('Cardonia', ['Nhava Sheva', 'Port of Fremantle'], 'Nhava Sheva', \
                                  time.mktime(datetime.datetime(2018,datetime.datetime.now().month, datetime.datetime.now().day,12,25,0).timetuple()),\
                                  time.mktime(datetime.datetime(2018,datetime.datetime.now().month, datetime.datetime.now().day,13,40,0).timetuple())))
    todays_arrivals.append(Ship('OEL Emirates', ['Nhava Sheva', 'Port of Duoro'], 'Nhava Sheva', \
                                  time.mktime(datetime.datetime(2018,datetime.datetime.now().month, datetime.datetime.now().day,14,0,0).timetuple()),\
                                  time.mktime(datetime.datetime(2018,datetime.datetime.now().month, datetime.datetime.now().day,17,45,0).timetuple())))
    todays_arrivals.append(Ship('KMTC Dubai', ['Mundra','Nhava Shevan', 'Port of Good Hope', 'Salvador'], 'Nhava Sheva', \
                                  time.mktime(datetime.datetime(2018,datetime.datetime.now().month, datetime.datetime.now().day,18,0,0).timetuple()),\
                                  time.mktime(datetime.datetime(2018,datetime.datetime.now().month, datetime.datetime.now().day,21,0,0).timetuple())))
    todays_arrivals.append(Ship('ER Denmark', ['Port Qasim', 'Nhava Sheva', 'Mundra', 'DamiettaNewark', 'Norfolk', \
                                  'Savannah', 'Charleston'], 'Nhava Sheva', \
                                  time.mktime(datetime.datetime(2018,datetime.datetime.now().month, datetime.datetime.now().day,21,20,0).timetuple()),\
                                  time.mktime(datetime.datetime(2018,datetime.datetime.now().month, datetime.datetime.now().day,23,50
                                                                ,0).timetuple())))
    
    #create warehouses
    Adani_CFS_Eximyard_Mundra =  Warehouse("Adani CFS Eximyard Mundra", "CFS", "Mundra",22.807149, 69.703706)
    Punjab_Conware_CFS = Warehouse('Punjab Conware CFS', "CFS", "Punjab",29.933069, 75.355966)
    
    #create available vehicles 
    all_available_vehicles = []
    all_available_vehicles.append(Land_Vehicle("MH 120B 476", "Truck", "Punjab Conware CFS", max_containers = 1))
    all_available_vehicles.append(Land_Vehicle("Goods Carrier express", "Train", "Punjab Conware CFS", max_containers = 50))
    all_available_vehicles.append(Land_Vehicle("PB 65RF 996", "Truck", "Punjab Conware CFS", max_containers = 1))
    all_available_vehicles.append(Land_Vehicle("GJ 21FF 349", "Truck", "Adani CFS Eximyard Mundra", max_containers = 1))
    all_available_vehicles.append(Land_Vehicle("Goods Train 007", "Train", "Adani CFS Eximyard Mundra", max_containers = 50))
    all_available_vehicles.append(Land_Vehicle("RJ 78RF 468", "Truck", "Adani CFS Eximyard Mundra", max_containers = 1))
    
    #create containers
    all_containers_to_ship = []
    
    list_of_all_destinations = ['Mundra', 'DamiettaNewark', 'Norfolk', 'Savannah', 'Charleston']
    for i in range(0, 40):
        all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Train", todays_arrivals[0].name, "In Transit", "Punjab Conware CFS", "JNPT", "Goods Carrier express"))
    all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Truck", todays_arrivals[0].name, "In Transit", "Adani CFS Eximyard Mundra", "JNPT", "GJ 21FF 349"))
    all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Truck", todays_arrivals[0].name, "In Transit", "Adani CFS Eximyard Mundra", "JNPT", "RJ 78RF 468"))
    
    list_of_all_destinations = ['Abu Dhabi']
    for i in range(0, 45):
        all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Train", todays_arrivals[1].name, "In Transit", "Punjab Conware CFS", "JNPT", "Goods Carrier express"))
    all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Truck", todays_arrivals[1].name, "In Transit", "Adani CFS Eximyard Mundra", "JNPT", "GJ 21FF 349"))
    all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Truck", todays_arrivals[1].name, "In Transit", "Adani CFS Eximyard Mundra", "JNPT", "RJ 78RF 468"))
    
    list_of_all_destinations = ['Port Klang']
    for i in range(0, 40):
        all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Train", todays_arrivals[2].name, "In Transit", "Adani CFS Eximyard Mundra", "JNPT", "Goods Train 007"))
    all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Truck", todays_arrivals[2].name, "In Transit", "Adani CFS Eximyard Mundra", "JNPT", "GJ 21FF 349"))
    
    list_of_all_destinations = ['Port of Fremantle']
    all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Truck", todays_arrivals[3].name, "In Transit", "Punjab Conware CFS", "JNPT", "MH 120B 476"))
    all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Truck", todays_arrivals[3].name, "In Transit", "Punjab Conware CFS", "JNPT", "PB 65RF 996"))
    
    list_of_all_destinations = ['Port of Duoro']
    for i in range(0, 50):
        all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Train", todays_arrivals[4].name, "In Transit", "Adani CFS Eximyard Mundra", "JNPT", "Goods Train 007"))
    for i in range(0, 50):
        all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Train", todays_arrivals[4].name, "In Transit", "Punjab Conware CFS", "JNPT", "Goods Carrier express"))
    
    all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Truck", todays_arrivals[4].name, "In Transit", "Adani CFS Eximyard Mundra", "JNPT", "GJ 21FF 349"))
    all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Truck", todays_arrivals[4].name, "In Transit", "Adani CFS Eximyard Mundra", "JNPT", "RJ 78RF 468"))
    all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Truck", todays_arrivals[4].name, "In Transit", "Punjab Conware CFS", "JNPT", "MH 120B 476"))
    all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Truck", todays_arrivals[4].name, "In Transit", "Punjab Conware CFS", "JNPT", "PB 65RF 996"))
    
    list_of_all_destinations = ['Port of Good Hope', 'Salvador']
    for i in range(0, 48):
        all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Train", todays_arrivals[5].name, "In Transit", "Punjab Conware CFS", "JNPT", "Goods Carrier express"))
    all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Truck", todays_arrivals[5].name, "In Transit", "Adani CFS Eximyard Mundra", "JNPT", "GJ 21FF 349"))
    all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Truck", todays_arrivals[5].name, "In Transit", "Adani CFS Eximyard Mundra", "JNPT", "RJ 78RF 468"))
    
    list_of_all_destinations = ['Mundra', 'DamiettaNewark', 'Norfolk', 'Savannah', 'Charleston']
    for i in range(0, 45):
        all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Train", todays_arrivals[6].name, "In Transit", "Punjab Conware CFS", "JNPT", "Goods Carrier express"))
    all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Truck", todays_arrivals[6].name, "In Transit", "Adani CFS Eximyard Mundra", "JNPT", "GJ 21FF 349"))
    all_containers_to_ship.append(Container("JNPT", random.choice(list_of_all_destinations),"Truck", todays_arrivals[6].name, "In Transit", "Adani CFS Eximyard Mundra", "JNPT", "RJ 78RF 468"))
    
    
    #virtual load containers to ship
    for ship in todays_arrivals:
        for container in all_containers_to_ship:
            if container.ship == ship.name:
                ship.load_containers([container])
    
    return todays_arrivals, all_available_vehicles, all_containers_to_ship
    

def get_data_from_dataset(date):
    shipping_export_data = pd.read_excel('data/JNPT Data.xlsx')
    required = []
    for i in range(0, len(shipping_export_data)):
        if str(shipping_export_data['VESSEL_SAILING_TIME'].iloc[i])[0:10] == date:
            required.append("Y")
        else:
            required.append("N")
    shipping_export_data['required'] = required
    shipping_export_data = shipping_export_data[shipping_export_data['required'] == "Y"].reset_index(drop = True)
    shipping_export_data = shipping_export_data.fillna(method='bfill')
    
    all_ships_today = shipping_export_data.drop_duplicates(subset = "SHIP_ID").reset_index(drop = True)
    todays_arrivals = []
    
    for i in range(0, len(all_ships_today)):
        todays_arrivals.append(Ship(all_ships_today['SHIP_ID'][i], [], 'Nhava Sheva', time.mktime(all_ships_today['VESSEL_SAILING_TIME'].iloc[i].timetuple()) - 18000, time.mktime(all_ships_today['VESSEL_SAILING_TIME'].iloc[i].timetuple())))
    
    
    all_warehouses = []
    all_warehouses_df = shipping_export_data.drop_duplicates(subset = "CFS/ICD Code").reset_index(drop = True)        
    for i in range(0, len(all_warehouses_df)):
        all_warehouses.append(Warehouse(all_warehouses_df["CFS/ICD Code"].iloc[i], "CFS/ICD", "NA", "NA" , "NA"))
    
    #assume each warehouse has 2 tracins of capacity 50 containers and 100 trucks of capacity 1 container
    all_available_vehicles = []
    for warehouse in all_warehouses:
        try:
            all_available_vehicles.append(Land_Vehicle("Train-" + warehouse.name + "-1" , "Train", warehouse.name, max_containers = 50))
            all_available_vehicles.append(Land_Vehicle("Train-" + warehouse.name + "-2" , "Train", warehouse.name, max_containers = 50))
        except Exception:
            pass
        for k in range(0, 100):
            try:
                all_available_vehicles.append(Land_Vehicle("Truck-" + warehouse.name + "-" + str(k) , "Truck", warehouse.name, max_containers = 1))
            except Exception:
                pass
    all_containers_to_ship = []
    all_containers_to_ship = []
    for i in range(0, len(shipping_export_data)):
        all_containers_to_ship.append(Container("JNPT", "NA", shipping_export_data["Carrier"].iloc[i], shipping_export_data["SHIP_ID"].iloc[i], "In Transit", shipping_export_data["CFS/ICD Code"].iloc[i], "JNPT", "NA", shipping_export_data["CONTAINER_NO"].iloc[i]))
    
    #virtual load containers to ship
    for ship in todays_arrivals:
        for container in all_containers_to_ship:
            if container.ship == ship.name:
                ship.load_containers([container])
                
    return todays_arrivals, all_available_vehicles, all_containers_to_ship, all_warehouses

@app.route("/webapp/<path:path>", methods=['GET', 'POST'])
def serve_webapp(path):
    headers = {'Content-Type': 'text/html'}
    #return render_template('%s' % path)
    return make_response(render_template('%s' % path),200,headers)

@app.route("/api/todays_arrivals", methods=["GET"])
def get_todays_arrivals():
    global todays_arrivals  
    global all_available_vehicles
    global all_containers_to_ship
    global all_warehouses
    date =  request.args.get('date')
    todays_arrivals, all_available_vehicles, all_containers_to_ship, all_warehouses = get_data_from_dataset(date)
    return_data = {"ships": []}
    for ship in todays_arrivals:
        current_ship_containers = []
        for container in ship.containers:
            current_ship_containers.append({
                        "name": container.id,
                        "source": container.source,
                        "destination": container.destination,
                        "mode_of_travel" : container.mode_of_travel,
                        "current_location": container.current_location
                    })
        return_data["ships"].append({
                    "name": ship.name,
                    "sailing_time": ship.next_stop_departure_time,
                    "containers": current_ship_containers
                })
    return jsonify(return_data)


@app.route("/api/ship_loading_plan", methods=["GET"])
def get_ship_loading_plan():
    global todays_arrivals  
    global all_available_vehicles
    global all_containers_to_ship
    global all_warehouses
    ship_number =  request.args.get('ship_number')
    loading_plan = todays_arrivals[int(ship_number)].get_basic_loading_plan()
    return jsonify(loading_plan)
    
if __name__ == "__main__":
    app.run(debug=True)
    pass