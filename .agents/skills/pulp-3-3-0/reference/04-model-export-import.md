# Model Export and Import

## Export Formats

PuLP supports three export formats:

- **LP file** — Human-readable format showing the full model with named variables and constraints. Best for debugging and inspection.
- **MPS file** — Industry-standard format used by most solvers. Stores variables and constraints but not variable values or solver output.
- **JSON / dict** — PuLP-native format that preserves all information including solution values, shadow prices, and reduced costs. Can fully reconstruct the model.

## Writing LP Files

```python
prob.writeLP("model.lp")
```

The LP file is human-readable and shows the complete model structure:

```
\Minimize
OBJ: +1 x +4 y +9 z
\Subject To
c1: x + y <= 5
c2: x + z >= 10
c3: -y + z = 7
\General
z
\End
```

Use `writeLP()` for debugging — open the file in a text editor to verify constraints are built correctly.

## Writing MPS Files

```python
# Basic export
prob.writeMPS("model.mps")

# With normalized names (X0000001, C0000001)
var_names, constr_names, obj_name, pulp_names = prob.writeMPS(
    "model.mps",
    rename=True,
    mip=True,              # Include integer/binary markers
    with_objsense=False,   # Write OBJSENSE section
    mpsSense=0             # 0=use problem sense, 1=minimize, -1=maximize
)
```

MPS is the standard interchange format. Most solvers can read it directly. It does not store solution values — only the model structure.

## JSON Export and Import

JSON preserves complete model state including solutions:

```python
# Export to dictionary
data = prob.to_dict()

# Export to JSON file
prob.toJson("model.json")

# Import from JSON file
variables, new_prob = LpProblem.fromJson("model.json")

# Import from dictionary
variables, new_prob = LpProblem.from_dict(data)
```

The returned tuple contains:
1. A dictionary mapping variable names to `LpVariable` objects
2. The reconstructed `LpProblem` object

After importing, you can solve the model and access solution values through the variable dictionary:

```python
variables, new_prob = LpProblem.fromJson("model.json")
new_prob.solve()
print(variables["x"].varValue)  # Solution value for x
```

## MPS Import

```python
# Import from MPS file
variables, new_prob = LpProblem.fromMPS("model.mps")
new_prob.solve()
```

Returns the same tuple as JSON import: `(variables_dict, LpProblem)`.

## Complete Example — Export and Re-import

```python
from pulp import *

# Build model
prob = LpProblem("test_export", LpMinimize)
x = prob.add_variable("x", 0, 4)
y = prob.add_variable("y", -1, 1)
z = prob.add_variable("z", 0, None, LpInteger)

prob += x + 4 * y + 9 * z, "obj"
prob += x + y <= 5, "c1"
prob += x + z >= 10, "c2"
prob += -y + z == 7.5, "c3"

# Export to JSON
prob.toJson("model.json")

# Re-import and solve
vars_dict, prob2 = LpProblem.fromJson("model.json")
prob2.solve()

# Access solution through re-imported variables
print(vars_dict["x"].varValue)  # 3.0
```

## Trade-offs: JSON vs MPS

| Aspect | JSON | MPS |
|--------|------|-----|
| Preserves solution values | Yes | No |
| Preserves shadow prices | Yes | No |
| Human readable | Partially | No |
| Solver interoperability | PuLP only | Universal |
| File size | Larger | Smaller |
| Variable grouping | Flat list | Flat list |

Use JSON when you need to save and restore complete model state including solutions. Use MPS for sharing models with external solvers or other optimization tools.

## Considerations

- **Variable names must be unique** — PuLP uses internal codes internally, but exports identify variables by name only. Duplicate names cause issues on import.
- **Variables are not grouped on export** — Multiple dictionaries of variables flatten into a single list in the exported format.
- **JSON uses `ujson` if available** — Falls back to standard `json`. Install `ujson` for faster serialization.
- **Output information in JSON** — Status, solution status, variable values, shadow prices, and reduced costs are all exported, enabling you to save a solved model and reload it later just to inspect results.
