def read_key_optional(js, key, default=None):
    if key in js:
        return js[key]
    return default

