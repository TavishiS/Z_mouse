import numpy as np
import skfuzzy as fuzz

# Define universe of discourse
x_valence = np.linspace(0, 1, 100)
x_arousal = np.linspace(0, 1, 100)

# Fuzzy membership functions for valence
valence_low = fuzz.trimf(x_valence, [0.0, 0.0, 0.5])
valence_med = fuzz.trimf(x_valence, [0.2, 0.5, 0.8])
valence_high = fuzz.trimf(x_valence, [0.5, 1.0, 1.0])

# Fuzzy membership functions for arousal
arousal_low = fuzz.trimf(x_arousal, [0.0, 0.0, 0.5])
arousal_med = fuzz.trimf(x_arousal, [0.2, 0.5, 0.8])
arousal_high = fuzz.trimf(x_arousal, [0.5, 1.0, 1.0])

def fuzzy_label(value, x_range, low_mf, med_mf, high_mf):
    """
    Returns the fuzzy label and membership strength for a given value.
    """
    low_strength = fuzz.interp_membership(x_range, low_mf, value)
    med_strength = fuzz.interp_membership(x_range, med_mf, value)
    high_strength = fuzz.interp_membership(x_range, high_mf, value)

    strengths = {
        "low": low_strength,
        "medium": med_strength,
        "high": high_strength
    }

    best_label = max(strengths, key=strengths.get)
    return best_label, strengths[best_label]

# Example valence-arousal from previous step
if __name__=="__main__":
    valence = 0.9
    arousal = 0.8

    valence_label, valence_strength = fuzzy_label(valence, x_valence, valence_low, valence_med, valence_high)
    arousal_label, arousal_strength = fuzzy_label(arousal, x_arousal, arousal_low, arousal_med, arousal_high)

    print(f"Fuzzy Valence: {valence_label} with a membership of ({valence_strength:.2f})")
    print(f"Fuzzy Arousal: {arousal_label} with a membership of ({arousal_strength:.2f})")