import numpy as np

def num_to_str(value, display):
    if isinstance(value, (list, np.ndarray, tuple)):
        if len(np.atleast_1d(value)) > 1:
            return '[' + ', '.join(f"{v:{display}}" for v in np.atleast_1d(value)) + ']'
        else:
            return f"{np.atleast_1d(value)[0]:{display}}"
    return f"{value:{display}}"