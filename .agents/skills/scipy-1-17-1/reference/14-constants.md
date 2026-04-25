# scipy.constants - Physical and Mathematical Constants

The `scipy.constants` module provides access to a comprehensive collection of physical constants, mathematical constants, unit conversions, and related utilities for scientific computing.

## Accessing Constants

### Basic Usage

```python
from scipy import constants as const
import numpy as np

# Speed of light in vacuum
c = const.c  # 299792458 m/s

# Planck constant
h = const.h  # 6.62607015e-34 J·s

# Reduced Planck constant (h-bar)
hbar = const.hbar  # 1.054571817e-34 J·s

# Elementary charge
e = const.e  # 1.602176634e-19 C

# Electron mass
m_e = const.m_e  # 9.1093837015e-31 kg

# Avogadro constant
N_A = const.N_A  # 6.02214076e23 mol^-1
```

### Physical Constants Categories

```python
from scipy import constants as const

# Electromagnetic constants
alpha = const.alpha           # Fine-structure constant
epsilon_0 = const.epsilon_0   # Vacuum permittivity
mu_0 = const.mu_0             # Vacuum permeability
k_e = const.k_e               # Coulomb constant

# Atomic and nuclear physics
m_p = const.m_p               # Proton mass
m_n = const.m_n               # Neutron mass
r_e = const.classical_electron_radius  # Classical electron radius
a_0 = const.alpha             # Bohr radius

# Thermodynamics
k = const.k                   # Boltzmann constant
sigma = const.sigma           # Stefan-Boltzmann constant
R = const.R                   # Molar gas constant

# Gravitational
G = const.G                   # Gravitational constant
g_n = const.g_n               # Standard gravity (9.80665 m/s²)

# Quantum mechanics
m_e = const.m_e               # Electron mass
mu_B = const.mu_B             # Bohr magneton
mu_N = const.mu_N             # Nuclear magneton
```

### Mathematical Constants

```python
from scipy import constants as const
import numpy as np

# Basic mathematical constants
pi = const.pi                 # π ≈ 3.14159...
e = const.e                   # Euler's number e ≈ 2.71828...
phi = const.golden            # Golden ratio φ ≈ 1.61803...
ln2 = const.ln2               # ln(2)
ln10 = const.ln10             # ln(10)
log10e = const.log10e         # log₁₀(e)
log2e = const.log2e           # log₂(e)

# Special values
inf = const.inf               # Infinity
nan = const.nan               # Not a Number
```

## Unit Conversions

### Physical Quantity Conversions

```python
from scipy import constants as const

# Length conversions
meters_in_km = const.convert('km', 'm')  # 1000.0
inches_to_meters = const.convert('inch', 'm')  # 0.0254

# Mass conversions
kg_in_pound = const.convert('pound', 'kg')  # 0.45359237

# Time conversions
seconds_in_hour = const.convert('hour', 's')  # 3600.0

# Energy conversions
joules_in_eV = const.e_V  # Electron volt to joules: 1.602176634e-19
joules_in_calorie = const.convert('calorie', 'J')

# Temperature (note: these are offsets, not multipliers)
# Kelvin to Celsius: T_C = T_K - 273.15
```

### Common Conversion Examples

```python
from scipy import constants as const
import numpy as np

# Convert speed from km/h to m/s
speed_kmh = 100
speed_ms = speed_kmh * const.convert('km/h', 'm/s')

# Convert energy from eV to joules
energy_eV = 1.5
energy_J = energy_eV * const.e_V

# Convert pressure from atm to Pa
pressure_atm = 2.5
pressure_Pa = pressure_atm * const.atm

# Convert volume from liters to m³
volume_L = 5.0
volume_m3 = volume_L * const.convert('liter', 'm**3')
```

### Compound Unit Conversions

```python
from scipy import constants as const

# Force: Newtons to pounds-force
N_to_lbf = const.convert('N', 'lbf')

# Power: Watts to horsepower
W_to_hp = const.convert('W', 'hp')

# Electric field: V/m to statV/cm
V_m_to_statV_cm = const.convert('V/m', 'statV/cm')

# Magnetic field: Tesla to Gauss
T_to_G = const.convert('T', 'G')  # 1 T = 10000 G
```

## Atomic Data

### Atomic Numbers and Symbols

```python
from scipy import constants as const

# Get atomic number from symbol
Z_H = const.atomic_number['H']      # Hydrogen: 1
Z_He = const.atomic_number['He']    # Helium: 2
Z_U = const.atomic_number['U']      # Uranium: 92

# Get symbol from atomic number
symbol_6 = const.elements[6]        # 'C' (Carbon)
```

### Atomic Masses and Properties

```python
from scipy import constants as const
import numpy as np

# Atomic masses (in kg)
mass_H = const.m_p + const.m_e  # Approximate hydrogen atom mass
mass_C12 = const.physical_constant('atomic mass constant') * 12

# Electron properties
m_e = const.m_e                  # Electron mass
e_charge = const.e                # Elementary charge
a_0 = const.alpha                # Bohr radius (approx)

# Rydberg constant
R_inf = const.Rydberg            # Rydberg constant (in m^-1)
```

### Isotope Information

```python
from scipy import constants as const

# Access isotope data
isotopes_H = const.isotopic_mass_number['H']  # Hydrogen isotopes

# Nuclear properties
r_nucleon = const.nuclear_magneton  # Nuclear magneton
g_p = const.g_p                     # Proton g-factor
```

## Physical Formulas and Calculations

### Electromagnetic Calculations

```python
from scipy import constants as const
import numpy as np

# Calculate wavelength from frequency
frequency = 5e14  # 500 THz (visible light)
wavelength = const.c / frequency  # λ = c/f

# Energy of photon
E_photon = const.h * frequency  # E = hf

# Fine-structure constant applications
alpha = const.alpha  # ≈ 1/137
v_electron_H = alpha * const.c  # Electron velocity in hydrogen ground state

# Coulomb force
q1, q2 = const.e, const.e  # Two elementary charges
r = 1e-10  # 1 Ångstrom
F = const.k_e * q1 * q2 / r**2  # F = k·q₁·q₂/r²
```

### Quantum Mechanics Calculations

```python
from scipy import constants as const
import numpy as np

# De Broglie wavelength
p = 1e-24  # Momentum in kg·m/s
lambda_db = const.h / p  # λ = h/p

# Uncertainty principle (minimum)
delta_x = 1e-10  # Position uncertainty
delta_p_min = const.hbar / (2 * delta_x)  # Δp ≥ ℏ/(2Δx)

# Bohr model energy levels
n = 2  # Principal quantum number
E_n = -13.6 * const.e_V / n**2  # Energy in joules

# Compton wavelength
lambda_C_e = const.h / (const.m_e * const.c)  # Electron Compton wavelength
```

### Thermodynamic Calculations

```python
from scipy import constants as const
import numpy as np

# Ideal gas law: PV = nRT
P = 101325  # 1 atm in Pa
V = 0.0224  # m³ (molar volume at STP)
n = 1  # moles
T = P * V / (const.R * n)  # Temperature in K

# Thermal energy at temperature T
T_room = 298.15  # 25°C in Kelvin
kT = const.k * T_room  # Thermal energy kT

# Blackbody radiation (Stefan-Boltzmann law)
sigma = const.sigma  # Stefan-Boltzmann constant
T_star = 5778  # Sun's surface temperature in K
power_per_area = sigma * T_star**4  # W/m²
```

### Relativistic Calculations

```python
from scipy import constants as const
import numpy as np

# Rest mass energy: E₀ = mc²
m_electron = const.m_e
E_rest_e = m_electron * const.c**2  # Joules
E_rest_e_MeV = E_rest_e / (const.e_V * 1e6)  # ~0.511 MeV

# Relativistic energy: E = γmc²
v = 0.9 * const.c  # 90% speed of light
gamma = 1 / np.sqrt(1 - (v/const.c)**2)
E_rel = gamma * const.m_e * const.c**2

# Mass-energy equivalence
mass_kg = 1.0  # 1 kg
energy_J = mass_kg * const.c**2  # ~9×10¹⁶ J
```

## Unit Systems and Prefixes

### SI Prefixes

```python
from scipy import constants as const

# Common SI prefixes
kilo = const.kilo      # 10³
mega = const.mega      # 10⁶
giga = const.giga      # 10⁹
tera = const.tera      # 10¹²

milli = const.milli    # 10⁻³
micro = const.micro    # 10⁻⁶
nano = const.nano      # 10⁻⁹
pico = const.pico      # 10⁻¹²

# Usage example
nanometers = 500 * const.nano  # 500 nm in meters
microseconds = 100 * const.micro  # 100 μs in seconds
```

### Named Units

```python
from scipy import constants as const

# Length units
angstrom = const.angstrom      # 1 Å = 10⁻¹⁰ m
nanometer = const.nano         # 1 nm
fermi = const.fermi            # 1 fm (nuclear physics)
light_year = const.ly          # 1 light year

# Mass units
amu = const.u                  # Atomic mass unit
dalton = const.Dalton          # Same as amu

# Energy units
eV = const.e_V                 # Electron volt
Ry = const.Rydberg * const.h * const.c  # Rydberg energy

# Pressure units
atm = const.atm                # Standard atmosphere
bar = const.bar                # 1 bar = 10⁵ Pa
torr = const.torr              # 1 torr ≈ 133.322 Pa
```

## Accessing All Constants

### Listing Available Constants

```python
from scipy import constants as const

# Get all physical constants
physical_constants = const.physical_constants
print(f"Number of physical constants: {len(physical_constants)}")

# Iterate through constants
for name, info in list(physical_constants.items())[:10]:
    value, unit, uncertainty = info
    print(f"{name}: {value} {unit} (±{uncertainty})")

# Get mathematical constants
mathematical_constants = const.mathematical_constants

# Get physical quantities (derived)
physical_quantities = const.physical_quantities
```

### Detailed Constant Information

```python
from scipy import constants as const

# Get detailed info for a specific constant
c_info = const.physical_constants['speed of light in vacuum']
print(f"Speed of light: {c_info}")
# Output: (299792458.0, 'm / s', 0.0)

# Value, unit, and uncertainty
value, unit, uncertainty = c_info

# Access by short name
c_value = const.c  # Direct access without tuple unpacking
```

## Troubleshooting

### Unit Conversion Issues

```python
from scipy import constants as const

# Always check units before converting
print(const.convert('inch', 'm'))  # Verify conversion factor

# For compound units, use explicit notation
factor = const.convert('km/h', 'm/s')  # Not 'km/h to m/s'

# Temperature conversions require care (offsets vs multipliers)
# Kelvin to Celsius: T_C = T_K - 273.15 (not a simple multiply)
```

### Precision and Uncertainty

```python
from scipy import constants as const
import numpy as np

# Constants have defined uncertainties
h_info = const.physical_constants['Planck constant']
h_value, h_unit, h_uncertainty = h_info

relative_uncertainty = h_uncertainty / h_value
print(f"Planck constant relative uncertainty: {relative_uncertainty:.2e}")

# For most calculations, the nominal value is sufficient
# Use uncertainties for error propagation if needed
```

### Deprecated Names

```python
from scipy import constants as const

# Some old names may be deprecated
# Use modern SI names when possible

# Instead of 'c_light', use 'c'
speed_of_light = const.c

# Check documentation for current naming conventions
print(const.__dict__.keys())  # List all available attributes
```

## See Also

- [`scipy.special`](references/12-special.md) - Mathematical functions using constants
- [NIST Reference on Constants, Units, and Uncertainty](https://www.nist.gov/pml/special-publication-811)
- [CODATA Recommended Values](https://www.nist.gov/pml/codata-recommended-values-physical-constants)
