import gurobipy

with open("C:/Users/ammar/OneDrive/Desktop/FINAL_ROUND_INSTANCES_OPTCHAL2025/Instance_1.txt", 'r') as file:

    lines = file.readlines()




N, M = map(int, lines[0].split())  # N: number of communities, M: number of healthcare centers
depot_line = lines[1]              # skip for stage 1
community_lines = lines[2:]

# Extract coordinates, capacity, and population
Xn, Yn, Pn = [], [], []
for line in community_lines:
    parts = line.strip().split()
    Xn.append(float(parts[1]))
    Yn.append(float(parts[2]))
    Pn.append(int(parts[4]))

C = int(community_lines[0].split()[3])  # capacity of a healthcenter


import numpy as np

Xn = np.array(Xn, dtype=np.float32)
Yn = np.array(Yn, dtype=np.float32)

# Reshape to column vectors
Xn_mat = Xn.reshape(-1, 1)
Yn_mat = Yn.reshape(-1, 1)

dx2 = (Xn_mat - Xn_mat.T) ** 2
dy2 = (Yn_mat - Yn_mat.T) ** 2
d = np.sqrt(dx2 + dy2).astype(np.float32)  # final NxN distance matrix


neighbors = {n: np.argsort(d[n])[:2000].tolist() for n in range(N)}


from gurobipy import Model, GRB, quicksum

model = Model("Healthcenter_Deployment")
if N>=500:             
    model.setParam("Presolve", 1)              
    model.setParam("Heuristics", 0.1)          
    model.setParam("MIPFocus", 1)              
    model.setParam("Cuts", 0)                  
    model.setParam("MIPGap", 0.2)             
    model.setParam("TimeLimit", 3600)
       
model.setParam("OptimalityTol", 1e-9)     
model.setParam("FeasibilityTol", 1e-9)
model.setParam("IntFeasTol", 1e-6)
model.setParam("NumericFocus", 1)         


# Decision variables
Dj = model.addVars(N, vtype=GRB.BINARY, name="Dj")
Tnj = model.addVars([(n, j) for n in range(N) for j in neighbors[n]], vtype=GRB.BINARY, name="Tnj")
Z = model.addVar(lb=0, name="Z")

# Objective: Minimize 1,000,000 * Z 

model.setObjective( 1000000 * Z, GRB.MINIMIZE )

# Each node n must be assigned to exactly one facility
for n in range(N):
    model.addConstr(quicksum(Tnj[n, j] for j in neighbors[n]) == 1, name=f"assign_{n}")


# Assign only to open facilities
for n in range(N):
    for j in neighbors[n]:
        model.addConstr(Tnj[n, j] <= Dj[j], name=f"assignOpen_{n}_{j}")

# Exactly M facilities must be opened
model.addConstr(quicksum(Dj[j] for j in range(N)) == M, name="facility_count")

# Capacity constraint
for j in range(N):
    # Include only communities that consider j a neighbor
    assigned_communities = [n for n in range(N) if j in neighbors[n]]
    if assigned_communities:  # avoid empty lists
        model.addConstr(
            quicksum(Pn[n] * Tnj[n, j] for n in assigned_communities) <= C * Dj[j],
            name=f"capacity_{j}"
        )


# Max-pop-weighted distance constraint
for n in range(N):
    for j in neighbors[n]:
        model.addConstr(Pn[n] * d[n][j] * Tnj[n, j] <= Z, name=f"maxDist_{n}_{j}")


# Solve model
model.optimize()


assignments = {n: j for n in range(N) for j in neighbors[n] if Tnj[n, j].X > 0.5}
facilities = [j for j in range(N) if Dj[j].X > 0.5]







import matplotlib.pyplot as plt

# Get assignments and facilities
assignments = {n: j for n in range(N) for j in neighbors[n] if Tnj[n, j].X > 0.5}
facilities = [j for j in range(N) if Dj[j].X > 0.5]


# Plot
plt.figure(figsize=(10, 8))
colors = plt.cm.get_cmap('tab10', len(facilities))

for idx, center in enumerate(facilities):
    assigned = [n for n, j in assignments.items() if j == center]
    color = colors(idx)
    plt.scatter([Xn[n] for n in assigned], [Yn[n] for n in assigned], color=color, label=f"Center {center + 1}", s=40)
    plt.scatter(Xn[center], Yn[center], marker='^', color=color, edgecolor='black', s=200)
    for n in assigned:
        plt.text(Xn[n] + 3, Yn[n], f"{n+1}", fontsize=8)

print("done")
from decimal import Decimal, getcontext

getcontext().prec = 50  # Arbitrary high precision

high_precision_Z = Decimal(str(Z.X))
print(f" Max Population-Weighted Distance (Z): {high_precision_Z}")

print("\nStage-1:")
for center in facilities:
    assigned = [n for n, j in assignments.items() if j == center]
    assigned_human = [n + 1 for n in assigned]
    print(f"Healthcenter deployed at {center + 1}: Communities Assigned = {assigned_human}")
print(f"Objective Value: {high_precision_Z}")





#  STAGE 2


print("\nStage-2:")

Q = 10000  # Ambulance capacity
depot_x, depot_y = map(float, depot_line.strip().split()[1:])

# Get equipment demand per center
equipment_demand = {
    j: sum(Pn[n] for n, assigned_j in assignments.items() if assigned_j == j)
    for j in facilities
}

# Sort centers by demand
sorted_centers = sorted(equipment_demand.items(), key=lambda x: -x[1])

routes = []  # List of lists of center indices
current_route = []
current_load = 0
total_distance = 0

for j, demand in sorted_centers:
    if current_load + demand <= Q:
        current_route.append(j)
        current_load += demand
    else:
        if current_route:
            routes.append(current_route)
        current_route = [j]
        current_load = demand

if current_route:
    routes.append(current_route)
from math import hypot


# Print and calculate distance
for i, route in enumerate(routes):
    trip_distance = 0
    print(f"Route {i+1}: Depot", end='')
    last_x, last_y = depot_x, depot_y

    for j in route:
        center_x, center_y = Xn[j], Yn[j]
        trip_distance += hypot(center_x - last_x, center_y - last_y)
        print(f" -> Healthcenter at {j+1}", end='')
        last_x, last_y = center_x, center_y

    trip_distance += hypot(depot_x - last_x, depot_y - last_y)
    print(" -> Depot")

    total_distance += trip_distance

print(f"Objective Value: {total_distance:.2f}")





plt.title("Healthcare Center Deployment and Assignments")
plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("healthcare_deployment_plot.png")
plt.show(block=True)


