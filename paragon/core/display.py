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


def _format_aid(gd, _rid, aid):
    if character_name := _aid_to_character_name(gd, aid):
        return character_name
    elif job_name := _to_name(gd, aid, "jobs", "JID_"):
        return job_name
    elif item_name := _to_name(gd, aid, "items", "IID_"):
        return item_name
    elif character_name := _to_name(gd, aid, "characters", "PID_"):
        return character_name
    elif aid:
        return aid
    else:
        return None


def display_asset(gd, rid, _row):
    aid = gd.string(rid, "name")
    name_part = _format_aid(gd, rid, aid)
    if not name_part:
        return None

    conditional1 = gd.string(rid, "conditional1")
    conditional2 = gd.string(rid, "conditional2")
    if job_name := _to_name(gd, conditional1, "jobs", "JID_"):
        conditional1 = job_name
    if job_name := _to_name(gd, conditional2, "jobs", "JID_"):
        conditional2 = job_name
    if conditional1 and conditional2:
        cond_part = f" ({conditional1} and {conditional2})"
    elif conditional1:
        cond_part = f" ({conditional1})"
    elif conditional2:
        cond_part = f" ({conditional2})"
    else:
        cond_part = ""

    return name_part + cond_part


def display_combo_tbl(gd, rid, _row):
    aid = gd.string(rid, "name")
    name_part = _format_aid(gd, rid, aid)
    if not name_part:
        return None

    conditional = gd.string(rid, "conditional")
    if job_name := _to_name(gd, conditional, "jobs", "JID_"):
        conditional = job_name
    if conditional:
        cond_part = f" ({conditional})"
    else:
        cond_part = ""

    return name_part + cond_part


def display_fe13_chapter(gd, rid, _row):
    display = gd.display(rid)
    key = gd.key(rid)
    if display and display != key:
        return f"{display} ({key})"
    else:
        return key


def display_fe14_character(gd, rid, _row):
    key = gd.key(rid)
    if key == "PID_プレイヤー男" or key == "PID_プレイヤー女":
        message = gd.message("m/GameData.bin.lz", True, "MPID_デフォルト名")
        suffix = "(M)" if key == "PID_プレイヤー男" else "(F)"
        if message:
            return f"{message} {suffix}"
        else:
            return f"Corrin {suffix}"
    else:
        display = gd.display(rid)
        if display and display != key:
            return f"{display} ({key})"
        else:
            return display


def display_fe14_support_table(gd, rid, _row):
    table = gd.rid(rid, "table")
    if table:
        owner = gd.rid(table, "owner")
        if owner:
            return display_fe14_character(gd, owner, None)
    return None


def display_fe14_support(gd, rid, _row):
    char = gd.rid(rid, "character")
    if char:
        return display_fe14_character(gd, char, None)
    else:
        return None


def display_fe14_chapter(gd, rid, _row):
    cid = gd.key(rid)
    if not cid:
        return None
    name = gd.message("m/GameData.bin.lz", True, f"M{cid}")
    if name:
        return f"{name} ({cid})"
    else:
        return cid


def display_job(gd, rid, _row):
    mjid = gd.string(rid, "name")
    if not mjid:
        return gd.display(rid)
    name = gd.message("m/GameData.bin.lz", True, mjid)
    if not name:
        return gd.display(rid)
    jid = gd.string(rid, "jid")
    if jid and jid.endswith("男"):
        return f"{name} ♂"
    elif jid and jid.endswith("女"):
        return f"{name} ♀"
    else:
        return name
    

def display_buildings_route_set(_gd, _rid, row):
    if row == 0:
        return "Building Set (Birthright)"
    elif row == 1:
        return "Building Set (Conquest)"
    elif row == 2:
        return "Building Set (Revelation)"
    else:
        return f"Building Set {row}"


def display_init_buildings_entry(_gd, _rid, row):
    return f"Building {row}"


def display_fe14_forge_level(_gd, _rid, row):
    return f"Forge Level {row}"


def display_fe14_forge_upgrade_level(_gd, _rid, row):
    return f"Upgrade Level {row}"


def display_fe15_event_decl(gd, rid, row):
    name = None
    event_table = gd.rid(rid, "events")
    if event_table:
        name = gd.string(event_table, "name")
    return name if name else f"Event Decl. {row}"


def display_fe15_event(gd, rid, row):
    sequence = gd.string(rid, "sequence")
    if sequence:
        return f"--- {sequence} ---"
    elif command := gd.string(rid, "command"):
        return command
    else:
        return f"(Invalid Event Entry {row})"


def display_fe15_character(gd, rid, _):
    key = gd.key(rid)
    display = gd.display(rid)
    if display and display != key:
        return f"{display} ({key})"
    else:
        return display


_DISPLAY_FUNCTIONS = {
    "asset": display_asset,
    "combotbl": display_combo_tbl,
    "fe13_chapter": display_fe13_chapter,
    "fe14_character": display_fe14_character,
    "fe14_support_table": display_fe14_support_table,
    "fe14_support": display_fe14_support,
    "fe14_chapter": display_fe14_chapter,
    "job": display_job,
    "fe14_buildings_route_set": display_buildings_route_set,
    "fe14_init_buildings_entry": display_init_buildings_entry,
    "fe14_forge_level": display_fe14_forge_level,
    "fe14_forge_upgrade_level": display_fe14_forge_upgrade_level,
    "fe15_event_decl": display_fe15_event_decl,
    "fe15_event": display_fe15_event,
    "fe15_character": display_fe15_character,
}


def display_rid(gd, rid, fn, row):
    if fn in _DISPLAY_FUNCTIONS:
        return _DISPLAY_FUNCTIONS[fn](gd, rid, row)
    else:
        return None
