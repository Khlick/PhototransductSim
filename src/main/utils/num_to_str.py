import numpy as np

def num_to_str(value, display):
    # print(type(value))
    if isinstance(value, (list, np.ndarray, tuple)) and len(np.atleast_1d(value)) > 1:
        return '[' + ', '.join(f"{v:{display}}" for v in np.atleast_1d(value)) + ']'
    return f"{value:{display}}"