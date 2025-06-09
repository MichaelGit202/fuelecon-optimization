import math
import constants

force_grade_resistance = lambda mass, angle : mass * FORCE_GRAVITY * math.sin(angle)
#kg/m^3
air_pressure_altitude = lambda height: SEA_LEVEL_PRESSURE * (1 - ((TEMPERATURE_LAPSE_RATE * height)/ SEA_LEVEL_STANDARD_TEMP))**((FORCE_GRAVITY * MOLAR_MASS_AIR)/(UNIVERSAL_GAS_CONSTANT * TEMPERATURE_LAPSE_RATE))
#TEMP: K, Height: M
air_density = lambda height, temperature  : air_pressure_altitude(height) / (temperature * DRY_AIR_CONSTANT)
#N
force_aero_drag = lambda height, temperature, velocity, drag_coeff, area_front : .5 * air_density(height=height, temperature=temperature) * drag_coeff * area_front * velocity^2

#rolling resistance


#instantaneous fuel efficiency
#g/s, Watch units MAF ANd fuel density is assumed ot be in gal
fuel_rate = lambda maf, afr: maf/(afr * DENSITY_GASOLINE)
#^
#air_fuel_ratio = lambda # TODO Figure this out

fuel_mass = lambda volume: volume * MASS_GASOLINE

force_rolling = lambda mass_car, fuel_volume : (fuel_mass(fuel_volume) + mass_car) * ROLLING_RESISTANCE_COEFF * FORCE_GRAVITY

print(force_grade_resistance(mass=1000, angle=5))