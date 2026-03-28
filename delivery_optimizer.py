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

            
                
            
