# utils.py
from datetime import datetime
import numpy as np

def calculate_age(dob):
    """Calculate age from date of birth."""
    today = datetime.now().date()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def weighted_choice(choices, weights):
    """Pick an item based on probability weights."""
    weights = np.array(weights, dtype=float)
    weights /= weights.sum()
    return choices[np.random.choice(len(choices), p=weights)]