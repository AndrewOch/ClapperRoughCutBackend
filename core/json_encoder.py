def object_to_json(obj):
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    elif isinstance(obj, list):
        return [object_to_json(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: object_to_json(value) for key, value in obj.items()}
    else:
        return obj
