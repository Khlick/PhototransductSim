import numpy as np
from functools import reduce

def safe_eval(expr):
    # Allowed built-in functions
    allowed_builtins = {
        'abs', 'divmod', 'max', 'min', 'round', 'len', 'sum', 'range',
        'any', 'all', 'sorted', 'enumerate', 'zip', 'filter', 'map', 'float'
    }

    # Include all numpy functions and allowed built-in functions
    allowed_names = {name: obj for name, obj in vars(np).items() if callable(obj)}
    allowed_names.update({name: __builtins__[name] for name in allowed_builtins})

    # Add reduce from functools and numpy alias
    allowed_names['reduce'] = reduce
    allowed_names['np'] = np
    allowed_names['inf'] = np.inf

    code = compile(expr, "<string>", "eval")
    for name in code.co_names:
        if name not in allowed_names:
            raise NameError(f"Use of {name} is not allowed")
        if name == "inf":
            name = "np.inf"
    result = eval(code, {"__builtins__": {}}, allowed_names)

    # Check if the result is a scalar or a 1D numpy array
    if np.isscalar(result):
        return result
    elif isinstance(result, (list,np.ndarray,tuple)) and all(np.isscalar(x) for x in result):
        return result
    else:
        raise ValueError("The result must be a scalar or a 1D array.")