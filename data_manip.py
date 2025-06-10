import math
import constants as c

force_grade_resistance = lambda mass, angle : mass * c.FORCE_GRAVITY * math.sin(angle)
#kg/m^3
air_pressure_altitude = lambda height: c.SEA_LEVEL_PRESSURE * (1 - ((c.TEMPERATURE_LAPSE_RATE * height)/ c.SEA_LEVEL_STANDARD_TEMP))**((c.FORCE_GRAVITY * c.MOLAR_MASS_AIR)/(c.UNIVERSAL_GAS_cANT * c.TEMPERATURE_LAPSE_RATE))
#TEMP: K, Height: M
air_density = lambda height, temperature  : air_pressure_altitude(height) / (temperature * c.DRY_AIR_cANT)
#N
force_aero_drag = lambda height, temperature, velocity, drag_coeff, area_front : .5 * air_density(height=height, temperature=temperature) * drag_coeff * area_front * velocity^2

#rolling resistance


#instantaneous fuel efficiency
#g/s, Watch units MAF ANd fuel density is assumed ot be in gal
fuel_rate = lambda maf, afr: maf/(afr * c.DENSITY_GASOLINE)
#^
#air_fuel_ratio = lambda # TODO Figure this out

fuel_mass = lambda volume: volume * c.MASS_GASOLINE_LITER

force_rolling = lambda mass_car, fuel_volume : (fuel_mass(fuel_volume) + mass_car) * c.ROLLING_RESISTANCE_COEFF * c.FORCE_GRAVITY


print(force_grade_resistance(mass=1000, angle=5))



#chat generated Air-fuel-ratio based off of o2 sensor voltage because I dont have
#a direct afr variable
def estimate_afr(o2_voltage):
    # This is a rough approximation, valid near stoichiometric point
    # 0.45 V -> AFR 14.7
    # Voltages < 0.45 indicate lean (AFR > 14.7)
    # Voltages > 0.45 indicate rich (AFR < 14.7)
    # This simple linear model is not super accurate but a start

    if o2_voltage < 0.1:
        return 20.0  # Very lean
    elif o2_voltage > 0.8:
        return 10.0  # Very rich
    else:
        # Linear approx between 0.1-0.8 volts
        # AFR range from 20 to 10
        return 20 - (o2_voltage - 0.1) * (10 / 0.7)