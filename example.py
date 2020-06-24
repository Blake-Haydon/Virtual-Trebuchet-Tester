from VirtualTrebuchet import VirtualTrebuchet

# ALL Initial values must be given to the VirtualTrebuchet constructor
initial_values = {
    "length_short_arm": 0.9,        # [m]
    "length_long_arm": 4.5,         # [m]
    "length_sling": 0.9,            # [m]
    "length_weight": 0.45,          # [m]
    "height_pivot": 1.5,            # [m]
    # ------------------------------------------------------------------------
    "arm_mass": 10,                 # [kg]
    # ------------------------------------------------------------------------
    "weight_mass": 300,             # [kg]
    "weight_inertia": 26.25,        # [kg.m^2]
    # ------------------------------------------------------------------------
    "projectile_mass": 7,           # [kg]
    "projectile_diameter": 0.25,    # [m]
    "wind_speed": 0,                # [m/s]
    # ------------------------------------------------------------------------
    "release_angle": 45             # [degrees]
}

# Initialise the virtual trebuchet with a dict of initial_values
vt = VirtualTrebuchet(initial_values)

# Test different values for length long arm and save data to test_length_long_arm.csv
vt.save_data("test_length_long_arm", length_long_arm=[4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5])

# Test many different variables at once and save data to multi_variable.csv
vt.save_data("multi_variable",
             length_long_arm=[4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5],
             projectile_mass=[3, 5, 7],
             arm_mass=[7, 10, 13])

# Quit the virtual trebuchet (closes chrome)
vt.quit()
