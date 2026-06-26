CONSTRUCTORS : dict = {}

def constructor(*names):
    """Register a callable under one or more names in CONSTRUCTORS."""
    def decorator(fn):
        for name in names:
            CONSTRUCTORS[name] = fn
        return fn
    return decorator

def get(step):
    if isinstance(step, dict):
        return next(iter(step.items()))
    return step, None

def is_pipeline(value):
    """A pipeline is a list of dicts where the first dict is a known constructor."""
    return (
        isinstance(value, list)
        and value
        and isinstance(value[0], dict)
        and get(value[0])[0] in CONSTRUCTORS
    )

def resolve(value):
    """Recursively resolve a value — if it's a nested pipeline, run it first."""
    if is_pipeline(value):
        return run(value)
    elif isinstance(value, dict):
        return {k: resolve(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [resolve(v) for v in value]
    return value

def evaluate(data, step):
    method, args = get(step)
    args = resolve(args)

    if isinstance(args, dict):
        result = getattr(data, method)(**args)
    else:
        result = getattr(data, method)(args)

    return result

def complie(task):
    obj, args = get(task[0])
    args = resolve(args)
    if isinstance(args, dict):
        data = CONSTRUCTORS[obj](**args)
    else:
        data = CONSTRUCTORS[obj](args)
    return data, task[1:]

def run(task):
    data, transforms = complie(task)
    for step in transforms:
        data = evaluate(data, step)
    return data