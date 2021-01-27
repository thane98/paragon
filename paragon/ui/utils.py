def capitalize(field_id, name):
    if name:
        return name
    else:
        return " ".join(map(lambda s: s.capitalize(), field_id.split("_")))
