import os
import sys
import csv
from collections import defaultdict
import heapq

#initialize the constants 

priority_map= {'high' : 1, 'medium' : 2, 'low' : 3}


NUM_AGENTS=3  #initialize no of agents(may change later)
MAX_NO_OF_DELIVERIES= None # for now 

#STEP 1: Read and validate the CSV file, then create a list of deliveries with their details.

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

    with open(filepath,'r', newline='' , encoding='utf-8') as f:
        reader=csv.DictReader(f)

        if not reader.fieldnames: # if missing columns 
            raise ValueError("[ERROR] CSV has no header row.")
        
        fields_normalization= [col.strip().lower() for col in reader.fieldnames]

        needed_fields = {'location_id', 'distance_from_warehouse', 'delivery_priority'}

        missing= needed_fields - set(fields_normalization)

        if missing:
            raise ValueError(f"[ERROR] CSV required missing columns : {missing}")
        
        for num, raw_row in enumerate(reader, start=2): # start=2 to account for header row
            #normalizing all values by stripping and lowercasing

            row={k.strip().lower(): v.strip() for k,v in raw_row.items()}

            #location _ id 
            location_id= row.get('location_id','').strip()
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
            raw_priority = row.get('delivery_priority', '').strip().lower()

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
                'priority': raw_priority,
                'priority_value': priority_map[raw_priority]
            # this is why we use map : for priority value to be used in sorting numbers in faster and cleaner than sorting string"
            })

        if not delivery_list:
            raise ValueError("[ERROR] No valid delivery entries found after validation")
    return delivery_list

# STEP 2: Sort the deliveries based on priority and distance.

def sorting_deliveries(delivery_list):
    """
    Sort deliveries based on priority first, then distance.

    - High priority deliveries go first, Low go last.
    - If two deliveries have the same priority, the nearer one is chosen.

    Using Python's built-in sorted() with a tuple key makes this simple and efficient.

    Other approaches like Bubble Sort are too slow (O(n²)),
    and Counting Sort doesn't work here since distance values are floats.

    Handled cases:
    - If all deliveries have same priority → sorted by distance
    - If both priority and distance are same → use location_id to keep order consistent
    - If all distances are same → sorted only by priority
    """
    
    return sorted(delivery_list, key=lambda x: (x['priority_value'], x['distance_from_warehouse'], x['location_id']))

#STEP 3 and 4: Assign deliveries to agents and balance (greedy + min-heap)

def assign_deliveries_to_agents(delivery_list,num_agents=NUM_AGENTS, max_per_agent=MAX_NO_OF_DELIVERIES):
    """
    Assign deliveries to agents while keeping their total travel distance balanced.

    Approach:
    - Always assign the next delivery to the agent with the least current distance.
    - A min-heap helps quickly find that agent.

    Why this approach?
    - It keeps the workload fairly balanced without overcomplicating things.
    - Using a heap avoids checking all agents every time, so it's efficient.

    Why not simpler methods?
    - Round Robin doesn’t consider distance, so one agent might get longer routes.
    - Advanced optimization (like ILP) is unnecessary for just a few agents.

    Handled scenarios:
    - If deliveries are fewer than agents → some agents may stay idle
    - If priorities or distances are similar → still distributes fairly
    - If one delivery is very far → slight imbalance is expected and noted
    """

    # Entries in the heap : (total_distance, agent_id, delivery_count)
    # Total distance is the sort key -> agent with least load is always at top

    heap = [(0.0, agent_id, 0) for agent_id in range(1, num_agents + 1)]
    heapq.heapify(heap)

    agents= defaultdict(list)
    agent_distances= defaultdict(float)
    unassigned=[]

    for delivery in delivery_list:

        if max_per_agent:

            # find the agent under limit 

            # skip agents who are full

            skipped=[]
            assigned=False

            while heap:
                total_dist, agent_id, count = heapq.heappop(heap)

                if count < max_per_agent:
                    # this agent has capacity, assign delivery

                    agents[agent_id].append(delivery)
                    new_dist= total_dist + delivery['distance_from_warehouse']
                    agent_distances[agent_id]= new_dist
                    heapq.heappush(heap, (new_dist, agent_id, count + 1))

                    #restore skipped agents back to heap
                    for item in skipped:
                        heapq.heappush(heap, item)

                    assigned=True
                    break
                else:
                    skipped.append((total_dist, agent_id, count))

            if not assigned:

                # all agents are full
                print(f"[WARNING] All agents have reached the maximum delivery limit.( {max_per_agent})."
                       f"Delivery '{delivery['location_id']}' is UNASSIGNED.")
                unassigned.append(delivery)

                #restore heap

                for item in skipped:
                    heapq.heappush(heap, item)

        else:

            #no limit - assign to least - loaded agent 

            total_dist, agent_id, count = heapq.heappop(heap)
            agents[agent_id].append(delivery)
            new_dist= total_dist + delivery['distance_from_warehouse']
            agent_distances[agent_id]= new_dist
            heapq.heappush(heap, (new_dist, agent_id, count + 1))

    for agent_id in range(1, num_agents + 1):
        if agent_id not in agent_distances:
            agent_distances[agent_id]=0.0

    return agents, agent_distances, unassigned

#STEP 5: output delivery plan

def write_output(agents, agent_distances, unassigned, output_path='output.txt'):
    """
    Write the final delivery assignment result to a text file.

    This keeps the output simple and easy to read.
    It shows each agent's deliveries, total distance,
    any unassigned deliveries, and a small summary at the end.
    """

    with open(output_path, 'w', encoding='utf-8') as f:
        
        f.write("=" * 65 + "\n")
        f.write("        DELIVERY OPTIMIZATION - AGENT ASSIGNMENT PLAN\n")
        f.write("=" * 65 + "\n\n")

        #write details for each agent
        for agent_id in sorted(agents.keys()):
            delivery_list= agents[agent_id]
            total_dist= agent_distances[agent_id]

            f.write(f"  AGENT {agent_id} ({len(delivery_list)} deliveries | {total_dist:.2f} km total)\n")
            f.write("  " + "-" * 60 + "\n")
            f.write(f"  {'#':<5} {'Location ID':<15} {'Priority':<10} {'Distance (km)':<15}\n")
            f.write("  " + "-" * 60 + "\n")

            if not delivery_list:
                f.write("  No deliveries assigned.\n")
            else:
                for idx,d in enumerate(delivery_list,1):
                    priority_dispaly=d['priority'].capitalize()
                    f.write(f"  {idx:<5} {d['location_id']:<15} {priority_dispaly:<10} {d['distance_from_warehouse']:<15.2f}\n")

            f.write(" " + "-" * 60 + "\n")
            f.write(f"  Total Distance : {total_dist:.2f} km\n")
            f.write(f"  Total Stops    : {len(delivery_list)}\n")

        #write unassigned deliveries seperately if any are left out 
        if unassigned:
            f.write("="*65 + "\n")
            f.write("  UNASSIGNED DELIVERIES \n")
            f.write("="*65 + "\n")
            for d in unassigned:
                f.write(f"  Location ID: {d['location_id']} | Priority: {d['priority'].capitalize()} | Distance: {d['distance_from_warehouse']:.2f} km\n")
            f.write("\n" )

        #summary section
        all_distances= list(agent_distances.values())
        max_dist=max(all_distances) 
        min_dist=min(all_distances)
        imbalance= max_dist - min_dist
        total=sum(all_distances)

        f.write("=" * 65 + "\n")
        f.write("  SUMMARY\n")
        f.write("=" * 65 + "\n")
        f.write(f"  Total Deliveries Assigned : {sum(len(v) for v in agents.values())}\n")
        f.write(f"  Unassigned Deliveries     : {len(unassigned)}\n")
        f.write(f"  Combined Distance         : {total:.2f} km\n")
        f.write(f"  Max Agent Distance        : {max_dist:.2f} km\n")
        f.write(f"  Min Agent Distance        : {min_dist:.2f} km\n")
        f.write(f"  Load Imbalance            : {imbalance:.2f} km\n")

        #simple warning if distance split is too uneven
        if total>0 and (imbalance/total)>0.3:
            f.write("\n  Warning: load distribution is a bit uneven.\n")
            f.write("  This may be because of very long-distance deliveries\n")
            f.write("  or too many important deliveries in the same area.\n")

        f.write("\n" + "=" * 65 + "\n")


def main():
    print("\n" + "="*50)
    print("     DELIVERY OPTIMMIZATION SYSTEM ")
    print("=" * 50 +"\n")

    #allow cli agruments : python delivery_oprtimizer.py input.csv 

    csv_path = sys.argv[1] if len(sys.argv) > 1 else 'input.csv'
    output_path= sys.argv[2] if len(sys.argv) > 2 else 'output.txt'

    try:
        # Step 1: Read CSV
        print(f"[Step 1/4] Reading CSV: '{csv_path}'")
        delivery_list = read_csv(csv_path)
        print(f"           Done. {len(delivery_list)} valid deliveries loaded.\n")

        #step 2: sort deliveries
        print("[Step 2/4] Sorting deliveries by priority and distance...")
        sorted_list=sorting_deliveries(delivery_list)
        print(f"           Done.First 5 deliveries after soritng:")
        for d in sorted_list[:5]:
            print(f"           {d['location_id']} | {d['priority'].capitalize()} | {d['distance_from_warehouse']} km")
        print()

        #step 3 & 4: Assign+balance
        print("[Step 3/4] Assigning deliveries to agents...")
        agents, agent_distances, unassigned = assign_deliveries_to_agents(sorted_list)
        for agent_id in sorted(agents.keys()):
            print(f"           Agent {agent_id}: {len(agents[agent_id])} deliveries | {agent_distances[agent_id]:.2f} km")
        if unassigned:
            print(f"           WARNING: {len(unassigned)} deliveries could not be assigned.")
        print()

        #step 5 : write out 
        print(f"[Step 4/4] Writing output to '{output_path}'...")
        write_output(agents, agent_distances, unassigned, output_path)
        print(f"           Done.\n")

        print("=" * 50)
        print(f"  Output saved to: {output_path}")
        print("=" * 50 + "\n")
    
    except (FileNotFoundError, ValueError) as e:
        print(f"\n{e}")
        print("Please fix the issue and try again.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()