import os
import sys
import csv
from collections import defaultdict
import heapq

#initialize the constants 

priority_map= {'high' : 1, 'medium' : 2, 'low' : 3}


num_agents=3  #initialize no of agents(may change later)
max_no_of_deliveries= None # for now 

def read_csv(filepath):
    """

    edge cases to take into account are:
    1.file not found
    2.file is empty
    3.required colmnns are missing
    4.unknown priority values- treated as low
    5.dupicate location - gives warning 
    6.null/empty values - rows skipped 
    7.negative distance rows skipped
    8.distance=0- allowed but gives warning
    9.distance is not a number- row skipped

"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"[ERROR] CSV file not found at path: '{filepath}'")
    
    if os.path.getsize(filepath) == 0:
        raise ValueError(f"[ERROR] CSV file is completely .")
    
    delivery_list=[] # to store the list of deliveries read from the csv file
    ids_done=set() #to track duplicate location ids

    with open(filepath,'r', newline='' , enoding='utf-8') as f:
        reader=csv.DictReader(f)

        if not reader.fieldnames: # if missing columns 
            raise ValueError("[ERROR] CSV has no header row.")
        
        fields_normalization= [col.strip().lower() for col in reader.fieldnames]

        needed_fields={'location_id ','distance_from_warehouse','priority'}

        missing= needed_fields - set(fields_normalization)

        if missing:
            raise ValueError(f"[ERROR] CSV required missing columns : {missing}")
        
        for num, raw_row in enumerate(reader, start=2): # start=2 to account for header row
            #normalizing all values by stripping and lowercasing

            row={k.strip().lower(): v.strip() for k,v in raw_row.items()}

            #location _ id 
            location_id= row.get('location_id,'').strip()')
            if not location_id:
                print(f"[SKIP] Row {num} : Empty location_id.")
                continue

            if location_id in ids_done:
                print(f"[WARNING] Row {num} : Duplicate location_id '{location_id}'.Skipping duplicate.")
                continue
            ids_done.add(location_id)

            #distance from warehouse
            raw_dist=row.get('distance_from_warehouse','').strip()
            if not raw_dist:
                print(f"[SKIP] Row {num} : Missing distance.")
                continue
            try:
                distance= float(raw_dist)
            except ValueError:
                print(f"[SKIP] Row {num} : Invalid distance value '{raw_dist}'.")
                continue

            #if distance is negative
            if distance < 0:
                print(f"[SKIP] Row {num} : Negative distance '{distance}'.Not Valid.")
                continue

            # if distance is same as warehouse or equal to 0
            if distance == 0:
                print(f"[WARNING] Row {num} : Distance is 0. Location is same as warehouse.Keeping")
                
            #about priority
            raw_priority=row.get('priority','').strip().lower()

            #if prioty is missing or unknown, default to low and give warning
            if not raw_priority:
                print(f"[WARN] Row {num} ({location_id}): Missing priority. Defaulting to 'low'.")
                raw_priority='low'
            if raw_priority not in priority_map:
                print(f"[WARN] Row {num} ({location_id}): Unknown priority '{raw_priority}'. Defaulting to 'low'.")
                raw_priority='low'

            delivery_list.append({
                'location_id': location_id,
                'distance_from_warehouse': distance,
                'priority': raw_priority
                'priority_value': priority_map[raw_priority]
            # this is why we use map : for priority value to be used in sorting numbers in faster and cleaner than sorting string"
            })

        if not delivery_list:
            raise ValueError("[ERROR] No valid delivery entries found after validation")
    return delivery_list
