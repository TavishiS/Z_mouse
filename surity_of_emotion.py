import numpy as np
import skfuzzy as fuzz

# Universes
x_time = np.linspace(0, 60, 100)      # Hold time in seconds
x_grip = np.linspace(0, 100, 100)     # Grip strength (0 to 100)
x_gsr = np.linspace(0, 1, 100)        # Skin conductance (0 = dry, 1 = sweaty)

# Membership functions
# Hold time
time_short = fuzz.trimf(x_time, [0, 0, 20])
time_med = fuzz.trimf(x_time, [10, 30, 50])
time_long = fuzz.trimf(x_time, [30, 60, 60])

# Grip strength
grip_weak = fuzz.trimf(x_grip, [0, 0, 40])
grip_med = fuzz.trimf(x_grip, [30, 50, 70])
grip_strong = fuzz.trimf(x_grip, [60, 100, 100])

# GSR (low = dry = confident)
gsr_dry = fuzz.trimf(x_gsr, [0.0, 0.0, 0.5])
gsr_normal = fuzz.trimf(x_gsr, [0.3, 0.5, 0.7])
gsr_sweaty = fuzz.trimf(x_gsr, [0.5, 1.0, 1.0])

def get_certainty_label(hold_time, grip_strength, gsr):
    """Return certainty level based on Z-mouse inputs."""
    
    # Fuzzy memberships
    time_conf = fuzz.interp_membership(x_time, time_long, hold_time)
    grip_conf = fuzz.interp_membership(x_grip, grip_strong, grip_strength)
    gsr_conf = fuzz.interp_membership(x_gsr, gsr_dry, gsr)
    
    # Combine scores (simple average)
    certainty_score = (time_conf + grip_conf + gsr_conf) / 3

    # Certainty label
    if certainty_score >= 0.75:
        certainty_label = "very sure"
    elif certainty_score >= 0.5:
        certainty_label = "sure"
    else:
        certainty_label = "uncertain"

    return certainty_label, certainty_score

# Example inputs from Z-mouse
example_hold_time = 60        # seconds
example_grip_strength = 100    # strong grip
example_gsr = 0.2             # dry hand

# Run certainty evaluator
certainty_label, certainty_score = get_certainty_label(example_hold_time, example_grip_strength, example_gsr)

print(f"Certainty of emotion being 'tired': {certainty_label} (score = {certainty_score:.2f})")