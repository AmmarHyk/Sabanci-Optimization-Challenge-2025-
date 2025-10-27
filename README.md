# Sabanc-Optimization-Challenge-2025-
Our team's Top 7 Finalist solution for the Sabancı University Optimization Challenge 2025. This project features a Gurobi MIP model and a greedy heuristic to optimize the deployment of healthcare units and their supply routes.
# 🏆 Sabancı University Optimization Challenge 2025 - Finalist Solution

This repository contains the code and methodology our team developed for the **Sabancı University Optimization Challenge 2025**, where we were honored to qualify as one of the **top 7 finalist teams** out of 71 entries from across Türkiye. The competition was hosted by Sabancı University and [ICRON Technologies](https://www.icron.com/).

Our solution addresses a two-stage optimization problem focused on the efficient and equitable deployment of healthcare units to underserved communities.

---

## Problem Description

[cite_start]The challenge was a two-stage problem: first, the optimal deployment of healthcare units, and second, the optimal routing of ambulances to supply them[cite: 17].

### Stage 1: Healthcare Unit Deployment

[cite_start]The first stage objective was to determine the optimal placement of $M$ healthcare units among $N$ communities[cite: 6]. [cite_start]The goal was to minimize the **maximum population-weighted distance** traveled by any community member to access their assigned unit[cite: 10, 20].

* **Objective:** Minimize the maximum value of $Population_n \times \text{Distance}(n, j)$ for any community $n$ assigned to facility $j$.
* **Constraints:**
    * [cite_start]Exactly $M$ units must be deployed[cite: 6].
    * [cite_start]Units can only be placed at community locations[cite: 9].
    * Each community $n$ must be assigned to exactly one unit.
    * [cite_start]Each unit $j$ has a maximum capacity $C$, and the total population of communities assigned to it cannot exceed this capacity[cite: 9, 11].

### Stage 2: Equipment Distribution (Vehicle Routing)

[cite_start]Given the optimal locations from Stage 1, the second stage involved planning the logistics to supply these units from a central depot[cite: 12, 13].

* [cite_start]**Objective:** Minimize the **total travel distance** for a fleet of ambulances to deliver equipment to all deployed units[cite: 16, 21].
* **Constraints:**
    * [cite_start]Each ambulance has a capacity of $Q=10000$[cite: 15].
    * [cite_start]The equipment demand for each unit is equal to the total population it serves[cite: 14].
    * [cite_start]All routes must start and end at the depot[cite: 16].
    * [cite_start]Every deployed unit must be visited exactly once[cite: 16].

[cite_start]**Evaluation:** Solutions were ranked primarily by the Stage 1 objective, followed by the Stage 2 objective, and finally by the number of routes used[cite: 36, 38, 39, 41, 42, 43].

---

## 💡 Our Solution Approach

We developed a hybrid approach: a Mixed-Integer Program (MIP) for the Stage 1 deployment and a custom greedy heuristic for the Stage 2 routing.

### Stage 1: MIP Model with Gurobi

We formulated the deployment problem as a MIP using the `gurobipy` library.

**Key Optimization:** To ensure the model could be solved within the time limits for large instances ($N \ge 500$), we implemented a **neighbor-based heuristic**. Instead of allowing any community $n$ to be assigned to any facility $j$, we restricted the assignments. Each community $n$ could only be assigned to one of its **2,000 nearest neighbors**. This drastically reduced the number of binary variables ($T_{nj}$) in the model.

#### Model Formulation

* **Variables:**
    * $D_j \in \{0, 1\}$: $1$ if a healthcare unit is deployed at community $j$, $0$ otherwise.
    * $T_{nj} \in \{0, 1\}$: $1$ if community $n$ is assigned to the unit at community $j$ (only defined for $j \in \text{Neighbors}(n)$).
    * $Z \ge 0$: The maximum population-weighted distance (our objective).

* **Objective Function:**
    $$
    \min Z
    $$

* **Constraints:**
    1.  **Assign Each Community:** Each community $n$ must be assigned to exactly one facility $j$ from its neighbor list.
        $$
        \sum_{j \in \text{Neighbors}(n)} T_{nj} = 1 \quad \forall n \in N
        $$
       
    2.  **Assign to Open Facilities:** A community $n$ can only be assigned to $j$ if a facility is actually deployed at $j$.
        $$
        T_{nj} \le D_j \quad \forall n \in N, j \in \text{Neighbors}(n)
        $$
       
    3.  **Deploy Exactly M Facilities:**
        $$
        \sum_{j \in N} D_j = M
        $$
       
    4.  **Capacity Constraint:** The total population $P_n$ of all communities assigned to facility $j$ cannot exceed its capacity $C$.
        $$
        \sum_{n \text{ s.t. } j \in \text{Neighbors}(n)} P_n \cdot T_{nj} \le C \cdot D_j \quad \forall j \in N
        $$
       
    5.  **Objective Constraint:** $Z$ must be greater than or equal to the population-weighted distance for every single assignment.
        $$
        P_n \cdot d_{nj} \cdot T_{nj} \le Z \quad \forall n \in N, j \in \text{Neighbors}(n)
        $$
       

### Stage 2: Greedy Heuristic for Routing

For the Stage 2 vehicle routing problem, we implemented a fast and effective greedy heuristic. This approach is similar to a "First Fit Decreasing" strategy used in bin packing.

1.  **Calculate Demand:** First, we calculate the total equipment demand for each of the $M$ deployed centers (equal to the total population served).
2.  **Sort by Demand:** We sort the deployed centers in **descending order** of their demand.
3.  **Build Routes:** We iterate through the sorted list, adding centers to the `current_route` one by one, as long as the total `current_load` plus the new center's `demand` does not exceed the ambulance capacity $Q=10000$.
4.  **Create New Route:** When a center cannot be added to the current route, the route is "closed" (saved), and a new route is started with that center.
5.  **Calculate Distance:** Finally, we loop through all generated routes, calculating the total Euclidean distance for each trip (Depot $\rightarrow$ Center 1 $\rightarrow$ ... $\rightarrow$ Center k $\rightarrow$ Depot) and sum them up.

---

## 🛠️ How to Run the Code

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/YourUsername/Your-Repository-Name.git](https://github.com/YourUsername/Your-Repository-Name.git)
    cd Your-Repository-Name
    ```

2.  **Install Dependencies:**
    The code relies on `gurobipy`, `numpy`, and `matplotlib`.
    ```bash
    pip install gurobipy numpy matplotlib
    ```
    *Note: `gurobipy` requires a Gurobi license. A free academic license is available.*

3.  **Update File Path:**
    Open `Code File.py` and **change the file path on line 4** to point to the instance file (e.g., `Instance_1.txt`) on your local machine.
    ```python
    # Original:
    with open("C:/Users/ammar/OneDrive/Desktop/FINAL_ROUND_INSTANCES_OPTCHAL2025/Instance_1.txt", 'r') as file:
    
    # Change to:
    with open("path/to/your/Instance_1.txt", 'r') as file:
    ```

4.  **Run the Script:**
    ```bash
    python "Code File.py"
    ```
    The script will print the Stage 1 and Stage 2 assignments and objectives to the console and generate a `healthcare_deployment_plot.png` file visualizing the solution.

---

## The Team

This project was a collaborative effort, and I'm proud to have worked alongside such dedicated and talented individuals:
* **Ammar Hayek** - (https://www.linkedin.com/in/ammar-hayek-14714630b/)
* **Morhaf** - (https://www.linkedin.com/in/morhaf-rabe/)
* **Abdulmuhemen** - (https://www.linkedin.com/in/%D8%B9%D8%A8%D8%AF%D8%A7%D9%84%D9%85%D9%87%D9%8A%D9%85%D9%86-%D8%AD%D8%A7%D9%83%D9%85%D9%8A-7741891ba/)
