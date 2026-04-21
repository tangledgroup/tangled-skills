# Worked Examples

## Beer Distribution Problem (Official Transportation Case Study)

The canonical PuLP transportation problem: minimize shipping cost from breweries to bars.

From the official [PuLP case study](https://coin-or.github.io/pulp/CaseStudies/a_transportation_problem.html):

```python
from pulp import *

# Supply nodes (warehouses)
Warehouses = ["A", "B"]
supply = {"A": 1000, "B": 4000}

# Demand nodes (bars)
Bars = ["1", "2", "3", "4", "5"]
demand = {
    "1": 500, "2": 900, "3": 1800,
    "4": 200, "5": 700
}

# Cost matrix: costs[warehouse_index][bar_index]
costs = [
    [2, 4, 5, 2, 1],  # A
    [3, 1, 3, 2, 3],  # B
]

# Convert to dictionary using makeDict from amply:
# costs_dict["A"]["1"] = 2, costs_dict["B"]["3"] = 3
from amply import makeDict
costs_dict = makeDict([Warehouses, Bars], costs, default=0)

# Problem
prob = LpProblem("Beer Distribution Problem", LpMinimize)

# Decision variables: crates shipped from each warehouse to each bar
vars = prob.add_variable_dict(
    "Route", (Warehouses, Bars), lowBound=0, cat=LpInteger
)

# Objective: minimize total transportation cost
prob += (
    lpSum([vars[w, b] * costs_dict[w][b] for w in Warehouses for b in Bars]),
    "TotalTransportCost"
)

# Supply constraints: each warehouse ships at most its supply
for w in Warehouses:
    prob += (
        lpSum([vars[w, b] for b in Bars]) <= supply[w],
        f"Supply_{w}"
    )

# Demand constraints: each bar receives at least its demand
for b in Bars:
    prob += (
        lpSum([vars[w, b] for w in Warehouses]) >= demand[b],
        f"Demand_{b}"
    )

prob.solve()
print(f"Status: {LpStatus[prob.status]}")
for w in Warehouses:
    for b in Bars:
        if value(vars[w, b]) > 0:
            print(f"  Ship {vars[w, b].varValue:.0f} from {w} to {b}")
print(f"Total Cost: ${value(prob.objective):,.0f}")
```

### Unbalanced Transportation (Supply > Demand)

When total supply exceeds total demand, add a dummy demand node:

```python
# Add dummy bar D with demand = excess supply
demand["D"] = 900  # 6000 supply - 5100 demand

# Zero cost to dummy (unsatisfied supply has no shipping cost)
costs.append([0, 0, 0, 0, 0, 0])  # costs from C to all bars + dummy

# Add third warehouse
Warehouses.append("C")
supply["C"] = 100
```

## Transportation Problem (General)

Minimize shipping cost from plants to markets:

```python
from pulp import *

# Parameters
plants = ["Seattle", "San_Diego"]
markets = ["New_York", "Chicago", "Topeka"]
capacity = {"Seattle": 355, "San_Diego": 600}
demand = {"New_York": 325, "Chicago": 300, "Topeka": 275}
distance = {
    ("Seattle", "New_York"): 2.5, ("Seattle", "Chicago"): 1.7,
    ("Seattle", "Topeka"): 1.8,   ("San_Diego", "New_York"): 2.5,
    ("San_Diego", "Chicago"): 1.8, ("San_Diego", "Topeka"): 1.4
}
freight = 90  # $ per unit per 1000 miles

# Decision variables
shipments = LpVariable.dicts("Ship", (plants, markets), lowBound=0)

# Problem
prob = LpProblem("Transportation", LpMinimize)

# Objective: min total shipping cost
prob += lpSum(
    shipments[i][j] * distance[i][j] * freight / 1000
    for i in plants for j in markets
), "TotalCost"

# Supply constraints
for i in plants:
    prob += lpSum(shipments[i][j] for j in markets) <= capacity[i], f"Supply_{i}"

# Demand constraints
for j in markets:
    prob += lpSum(shipments[i][j] for i in plants) == demand[j], f"Demand_{j}"

prob.solve()
print(f"Status: {LpStatus[prob.status]}")
for i in plants:
    for j in markets:
        print(f"  Ship {i} -> {j}: {value(shipments[i][j])}")
```

## Blending Problem

Determine optimal mix of ingredients to minimize cost while meeting quality specs:

```python
from pulp import *

# Ingredients and their properties
ingredients = ["Sugar", "Cream", "Water"]
cost = {"Sugar": 1.0, "Cream": 1.5, "Water": 0.0}
flavor = {"Sugar": 100, "Cream": 50, "Water": 0}
color = {"Sugar": 80, "Cream": 60, "Water": 0}
preservative = {"Sugar": 20, "Cream": 10, "Water": 30}
volume = 100  # total batch volume

# Decision variables: amount of each ingredient
amount = LpVariable.dicts("Amt", ingredients, lowBound=0)

prob = LpProblem("Blending", LpMinimize)

# Objective: minimize cost
prob += lpSum(cost[i] * amount[i] for i in ingredients), "TotalCost"

# Volume constraint
prob += lpSum(amount[i] for i in ingredients) == volume, "TotalVolume"

# Quality constraints (as percentages of total batch)
prob += lpSum(flavor[i] * amount[i] for i in ingredients) >= 50 * volume, "MinFlavor"
prob += lpSum(color[i] * amount[i] for i in ingredients) >= 75 * volume, "MinColor"
prob += lpSum(preservative[i] * amount[i] for i in ingredients) <= 25 * volume, "MaxPreservative"

prob.solve()
for i in ingredients:
    print(f"  {i}: {value(amount[i]):.1f}")
print(f"Total Cost: ${value(prob.objective):.2f}")
```

## Assignment Problem

Assign workers to tasks minimizing total cost:

```python
from pulp import *

workers = ["Alice", "Bob", "Carol"]
tasks = ["Design", "Code", "Test"]
cost_matrix = {
    ("Alice", "Design"): 10, ("Alice", "Code"): 8, ("Alice", "Test"): 9,
    ("Bob", "Design"): 12,   ("Bob", "Code"): 6,   ("Bob", "Test"): 7,
    ("Carol", "Design"): 9,  ("Carol", "Code"): 11, ("Carol", "Test"): 8,
}

# Binary: worker w assigned to task t
assign = LpVariable.dicts("Assign", (workers, tasks), cat='Binary')

prob = LpProblem("Assignment", LpMinimize)

# Objective: min total cost
prob += lpSum(
    cost_matrix[w][t] * assign[w][t]
    for w in workers for t in tasks
), "TotalCost"

# Each worker does exactly one task
for w in workers:
    prob += lpSum(assign[w][t] for t in tasks) == 1, f"OneTask_{w}"

# Each task done by exactly one worker
for t in tasks:
    prob += lpSum(assign[w][t] for w in workers) == 1, f"OneWorker_{t}"

prob.solve()
for w in workers:
    for t in tasks:
        if value(assign[w][t]) == 1:
            print(f"  {w} -> {t} (cost={cost_matrix[w][t]})")
```

## Production Planning with Fixed Costs (MIP)

Decide which products to produce, considering setup costs:

```python
from pulp import *

products = ["A", "B"]
setup_cost = {"A": 100, "B": 150}
profit_per_unit = {"A": 10, "B": 15}
max_demand = {"A": 50, "B": 40}
resource_usage = {"A": 3, "B": 5}
total_resource = 200

# Decision variables
produce = LpVariable.dicts("Qty", products, lowBound=0)
build = LpVariable.dicts("Build", products, cat='Binary')

prob = LpProblem("Production", LpMaximize)

# Objective: max profit minus setup costs
prob += lpSum(
    profit_per_unit[p] * produce[p] - setup_cost[p] * build[p]
    for p in products
), "NetProfit"

# Link production to setup (big-M constraint)
for p in products:
    prob += produce[p] <= max_demand[p] * build[p], f"Link_{p}"

# Resource constraint
prob += lpSum(resource_usage[p] * produce[p] for p in products) <= total_resource, "Resource"

prob.solve()
for p in products:
    print(f"  {p}: produce={value(produce[p])}, build={'Yes' if value(build[p]) == 1 else 'No'}")
print(f"Net Profit: ${value(prob.objective):.2f}")
```

## Knapsack Problem

Select items to maximize value within weight capacity:

```python
from pulp import *

items = [
    ("laptop", 5, 200),   # (name, weight, value)
    ("phone", 1, 100),
    ("water", 2, 60),
    ("food", 3, 90),
    ("first_aid", 1, 80),
    ("clothes", 4, 120),
]

capacity = 10

# Binary: select item i
selected = LpVariable.dicts("Pick", range(len(items)), cat='Binary')

prob = LpProblem("Knapsack", LpMaximize)

# Objective: max total value
prob += lpSum(
    items[i][2] * selected[i] for i in range(len(items))
), "TotalValue"

# Weight constraint
prob += lpSum(
    items[i][1] * selected[i] for i in range(len(items))
) <= capacity, "WeightLimit"

prob.solve()
for i in range(len(items)):
    if value(selected[i]) == 1:
        name, weight, value = items[i]
        print(f"  Take: {name} (w={weight}, v={value})")
print(f"Total Value: {value(prob.objective)}, Total Weight: {sum(items[i][1] for i in range(len(items)) if value(selected[i])==1)}")
```

## Diet / Nutrition Problem

Minimize food cost while meeting nutritional requirements:

```python
from pulp import *

foods = ["milk", "chicken", "egg"]
min_nutrition = {"calories": 2000, "protein_g": 50, "calcium_mg": 700}
max_nutrition = {"fat_g": 100}
nutrition_per_serving = {
    "milk":     {"calories": 120, "protein_g": 8,   "calcium_mg": 300, "fat_g": 3},
    "chicken":  {"calories": 300, "protein_g": 30,  "calcium_mg": 15,  "fat_g": 10},
    "egg":      {"calories": 200, "protein_g": 13,  "calcium_mg": 60,  "fat_g": 12},
}
cost_per_serving = {"milk": 0.50, "chicken": 2.00, "egg": 0.30}

# Decision variables: servings of each food
servings = LpVariable.dicts("Serv", foods, lowBound=0)

prob = LpProblem("Diet", LpMinimize)

# Objective: minimize cost
prob += lpSum(cost_per_serving[f] * servings[f] for f in foods), "TotalCost"

# Minimum nutrition
for nutrient, minimum in min_nutrition.items():
    prob += lpSum(
        nutrition_per_serving[f][nutrient] * servings[f] for f in foods
    ) >= minimum, f"Min_{nutrient}"

# Maximum nutrition
for nutrient, maximum in max_nutrition.items():
    prob += lpSum(
        nutrition_per_serving[f][nutrient] * servings[f] for f in foods
    ) <= maximum, f"Max_{nutrient}"

prob.solve()
for f in foods:
    print(f"  {f}: {value(servings[f]):.2f} servings")
print(f"Total Cost: ${value(prob.objective):.2f}")
```

## Facility Location Problem

Select warehouse locations to minimize total cost:

```python
from pulp import *

potential_sites = ["Site1", "Site2", "Site3", "Site4"]
customers = ["CustA", "CustB", "CustC", "CustD"]
fixed_cost = {"Site1": 500, "Site2": 600, "Site3": 400, "Site4": 700}
shipping_cost = {
    ("Site1","CustA"): 10, ("Site1","CustB"): 15, ("Site1","CustC"): 20, ("Site1","CustD"): 25,
    ("Site2","CustA"): 12, ("Site2","CustB"): 8,  ("Site2","CustC"): 18, ("Site2","CustD"): 22,
    ("Site3","CustA"): 20, ("Site3","CustB"): 18, ("Site3","CustC"): 10, ("Site3","CustD"): 15,
    ("Site4","CustA"): 25, ("Site4","CustB"): 22, ("Site4","CustC"): 15, ("Site4","CustD"): 10,
}
demand = {"CustA": 30, "CustB": 40, "CustC": 35, "CustD": 25}
max_sites = 2

# Decision variables
build = LpVariable.dicts("Build", potential_sites, cat='Binary')
ship = LpVariable.dicts("Ship", ((s,c) for s in potential_sites for c in customers), lowBound=0)

prob = LpProblem("FacilityLocation", LpMinimize)

# Objective: fixed + shipping costs
prob += lpSum(fixed_cost[s] * build[s] for s in potential_sites), "FixedCost"
prob += lpSum(
    shipping_cost[(s,c)] * ship[(s,c)]
    for s in potential_sites for c in customers
), "ShippingCost"

# Each customer served by exactly one facility
for c in customers:
    prob += lpSum(ship[(s,c)] for s in potential_sites) == demand[c], f"Satisfy_{c}"

# Can only ship from built facilities
for s in potential_sites:
    for c in customers:
        prob += ship[(s,c)] <= demand[c] * build[s], f"Link_{s}_{c}"

# Limit number of facilities
prob += lpSum(build[s] for s in potential_sites) <= max_sites, "MaxFacilities"

prob.solve()
print("Built:", [s for s in potential_sites if value(build[s]) == 1])
```

## Set Partitioning — Wedding Seating Problem

Determine optimal guest seating to maximize table happiness (from official case study).

From the [official PuLP case study](https://coin-or.github.io/pulp/CaseStudies/a_set_partitioning_problem.html):

```python
import pulp
from typing import Tuple, Union

max_tables = 5
max_table_size = 4
guests = "A B C D E F G I J K L M N O P Q R".split()

def happiness(table: Union[Tuple[str, ...],]) -> int:
    """Happiness = max distance between first and last letter."""
    return abs(ord(table[0]) - ord(table[-1]))

# Generate all possible table combinations (up to max_table_size guests)
possible_tables = [tuple(c) for c in pulp.allcombinations(guests, max_table_size)]

prob = pulp.LpProblem("Wedding Seating Model", pulp.LpMinimize)

# Binary variable: 1 if this table configuration is used
_table_keys = ["_".join(t) for t in possible_tables]
vars_by_key = prob.add_variable_dict(
    "table_%s", (_table_keys,), lowBound=0, upBound=1, cat=pulp.LpInteger
)
x = {t: vars_by_key["_".join(t)] for t in possible_tables}

# Objective: minimize total unhappiness
prob += pulp.lpSum([happiness(table) * x[table] for table in possible_tables])

# At most max_tables tables
prob += (
    pulp.lpSum([x[table] for table in possible_tables]) <= max_tables,
    "Maximum_number_of_tables"
)

# Each guest seated at exactly one table (set partitioning constraint)
for guest in guests:
    prob += (
        pulp.lpSum([x[table] for table in possible_tables if guest in table]) == 1,
        f"Must_seat_{guest}"
    )

prob.solve()
print(f"The chosen tables are out of a total of {len(possible_tables)}:")
for table in possible_tables:
    if x[table].value() == 1.0:
        print(table)
```

**Key insight:** Set partitioning problems enumerate all feasible subsets and use binary variables to select which subsets form the partition. The constraint `sum(x[table] for table containing guest) == 1` ensures each element appears in exactly one subset.

## Two-Stage Stochastic Programming

See also the stochastic example in SKILL.md. This variant uses scenario trees:

```python
from pulp import *

# First-stage decisions (before uncertainty)
invest = LpVariable("Investment", lowBound=0, upBound=100000)

# Second-stage recourse variables per scenario
scenarios = ["optimistic", "neutral", "pessimistic"]
probabilities = [0.3, 0.5, 0.2]
recourse_returns = {"optimistic": 1.15, "neutral": 1.05, "pessimistic": 0.90}
shortfall = LpVariable.dicts("Shortfall", scenarios, lowBound=0)

prob = LpProblem("StochasticInvestment", LpMaximize)

# Objective: maximize expected return
prob += lpSum(
    probabilities[s] * (recourse_returns[s] * invest - shortfall[s])
    for s in scenarios
), "ExpectedReturn"

# Recourse constraints per scenario
for s in scenarios:
    prob += shortfall[s] >= 0, f"ShortfallNonNeg_{s}"

# Budget constraint
prob += invest <= 100000, "Budget"

prob.solve()
print(f"Invest: ${value(invest):,.2f}")
for s in scenarios:
    print(f"  {s}: return = ${value(recourse_returns[s] * invest):,.2f}, shortfall = ${value(shortfall[s]):,.2f}")
```
