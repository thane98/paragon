def _aid_to_character_name(gd, aid):
    if aid and aid.startswith("AID_"):
        pid = "PID_" + aid[4:]
        rid = gd.key_to_rid("characters", pid)
        if rid:
            return gd.display(rid)
    return None


def _to_name(gd, key, table, prefix):
    if key and key.startswith(prefix):
        rid = gd.key_to_rid(table, key)
        if rid:
            return gd.display(rid)
    return None


def display_asset(gd, rid):
    aid = gd.string(rid, "name")
    if character_name := _aid_to_character_name(gd, aid):
        name_part = character_name
    elif job_name := _to_name(gd, aid, "jobs", "JID_"):
        name_part = job_name
    elif item_name := _to_name(gd, aid, "items", "IID_"):
        name_part = item_name
    elif aid:
        name_part = aid
    else:
        return None

    conditional1 = gd.string(rid, "conditional1")
    conditional2 = gd.string(rid, "conditional2")
    if job_name := _to_name(gd, conditional1, "jobs", "JID_"):
        conditional1 = job_name
    if job_name := _to_name(gd, conditional2, "jobs", "JID_"):
        conditional2 = job_name
    if conditional1 and conditional2:
        cond_part = f" ({conditional1} or {conditional2})"
    elif conditional1:
        cond_part = f" ({conditional1})"
    elif conditional2:
        cond_part = f" ({conditional2})"
    else:
        cond_part = ""

    return name_part + cond_part


_DISPLAY_FUNCTIONS = {
    "asset": display_asset
}


def display_rid(gd, rid, fn):
    if fn in _DISPLAY_FUNCTIONS:
        return _DISPLAY_FUNCTIONS[fn](gd, rid)
    else:
        return None