def _aid_to_character_name(gd, aid):
    if aid and aid.startswith("AID_"):
        pid = "PID_" + aid[4:]
        rid = gd.key_to_rid("characters", pid)
        if rid:
            return gd.display(rid)
    return None


def _aid_to_accessory_name(gd, aid):
    if aid and aid.startswith("ac"):
        rid, field_id = gd.table("accessories")
        try:
            target_field_value = int(aid[2:])
            if accessory_rid := gd.list_get_by_field_value(
                rid, field_id, "asset_entry", target_field_value
            ):
                return gd.display(accessory_rid)
        except:
            pass
    return None


def _to_name(gd, key, table, prefix):
    if key and key.startswith(prefix):
        rid = gd.key_to_rid(table, key)
        if rid:
            return gd.display(rid)
    return None


def _display_aid_default(aid):
    return aid if aid else None


def _format_aid(gd, aid):
    if character_name := _aid_to_character_name(gd, aid):
        return character_name
    elif job_name := _to_name(gd, aid, "jobs", "JID_"):
        return job_name
    elif item_name := _to_name(gd, aid, "items", "IID_"):
        return item_name
    elif character_name := _to_name(gd, aid, "characters", "PID_"):
        return character_name
    elif accessory_name := _aid_to_accessory_name(gd, aid):
        return f"{accessory_name} ({aid})"
    return _display_aid_default(aid)


def display_asset(gd, rid, _row):
    aid = gd.string(rid, "name")
    name_part = _format_aid(gd, aid)
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
    name_part = _format_aid(gd, aid)
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


def display_fe13_character(gd, rid, _row):
    key = gd.key(rid)
    if key == "PID_プレイヤー男" or key == "PID_プレイヤー女":
        message = gd.message("m/GameData.bin.lz", True, "MPID_デフォルト名")
        suffix = "(M)" if key == "PID_プレイヤー男" else "(F)"
        if message:
            return f"{message} {suffix}"
        else:
            return f"Robin {suffix}"
    else:
        display = gd.display(rid)
        if display and display != key:
            return f"{display} ({key})"
        else:
            return display


def display_fe13_sprite_data(gd, _rid, row):
    table_rid, table_field_id = gd.table("jobs")
    if row < gd.list_size(table_rid, table_field_id):
        job_rid = gd.list_get(table_rid, table_field_id, row)
        return display_job(gd, job_rid, row)
    return f"Class #{row}"


def display_fe13_reliance_list(gd, _rid, row):
    table_rid, table_field_id = gd.table("characters")
    if row < gd.list_size(table_rid, table_field_id):
        character_rid = gd.list_get(table_rid, table_field_id, row)
        return display_fe13_character(gd, character_rid, row)
    return f"Reliance List #{row}"


def display_fe13_reliance_list_data(gd, rid, row):
    rid = gd.rid(rid, "data")
    if not rid:
        return f"Reliance List Data #{row}"
    character1 = gd.rid(rid, "character1")
    character2 = gd.rid(rid, "character2")
    character1_display = (
        display_fe13_character(gd, character1, 0)
        if character1
        else "{Unknown Character}"
    )
    character2_display = (
        display_fe13_character(gd, character2, 0)
        if character2
        else "{Unknown Character}"
    )
    return f"{character1_display} x {character2_display}"


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


def display_init_buildings_entry(_gd, _rid, _row):
    return f"Building"


def display_fe14_forge_level(_gd, _rid, _row):
    return f"Forge Level"


def display_fe14_forge_upgrade_level(_gd, _rid, _row):
    return f"Upgrade Level"


def display_fe15_event_decl(gd, rid, _row):
    name = None
    event_table = gd.rid(rid, "events")
    if event_table:
        name = gd.string(event_table, "name")
    return name if name else f"Event Decl."


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


def display_fe15_job(gd, rid, _):
    mjid = gd.string(rid, "name")
    if not mjid:
        return gd.display(rid)
    name = gd.message("m/Job.bin.lz", True, mjid)
    if not name:
        return gd.display(rid)
    jid = gd.string(rid, "jid")
    if jid and jid.endswith("男"):
        return f"{name} ♂"
    elif jid and jid.endswith("女"):
        return f"{name} ♀"
    else:
        return name


def display_fe15_amiibo(gd, rid, _):
    odd = gd.rid(rid, "odd")
    return display_fe15_character(gd, odd, None) if odd else "null"


def display_fe15_call_table(gd, rid, _):
    rsid = gd.string(rid, "rsid")
    if rsid and rsid.startswith("RSID_"):
        pid = "PID_" + rsid[5:]
        character_rid = gd.key_to_rid("characters", pid)
        if character_rid:
            character_display = display_fe15_character(gd, character_rid, None)
            if character_display:
                return f"{character_display} ({rsid})"
    return rsid


def display_fe15_job_cc(gd, rid, _):
    cc = gd.string(rid, "cc")
    if cc and cc.startswith("CC_"):
        jid = "JID_" + cc[3:]
        job_rid = gd.key_to_rid("jobs", jid)
        if job_rid:
            job_display = display_fe15_job(gd, job_rid, _)
            if job_display:
                return f"{job_display} ({cc})"
    return cc


def display_fe15_job_cc_data_item(gd, rid, _):
    job = gd.rid(rid, "job")
    if job:
        return display_fe15_job(gd, job, _)
    return job


def display_fe15_food_preferences(gd, rid, _):
    fid = gd.string(rid, "fid")
    if fid and fid.startswith("FID_"):
        pid = "PID_" + fid[4:]
        character_rid = gd.key_to_rid("characters", pid)
        if character_rid:
            character_display = gd.display(character_rid)
            if character_display:
                return f"{character_display} ({fid})"
    return fid


def display_fe15_item_evolution(gd, rid, _):
    eid = gd.string(rid, "eid")
    if eid and eid.startswith("EID_"):
        iid = "IID_" + eid[4:]
        item_rid = gd.key_to_rid("items", iid)
        if item_rid:
            item_display = gd.display(item_rid)
            if item_display:
                return f"{item_display} ({eid})"
    return eid


def display_fe15_item_forge(gd, rid, _):
    forge_id = gd.string(rid, "rid")
    if forge_id and forge_id.startswith("RID_"):
        iid = "IID_" + forge_id[4:]
        item_rid = gd.key_to_rid("items", iid)
        if item_rid:
            item_display = gd.display(item_rid)
            if item_display:
                return f"{item_display} ({forge_id})"
    return forge_id


def display_fe15_dungeon_enemy_information(gd, rid, _):
    key = gd.key(rid)
    character = gd.rid(rid, "character")
    if key and character:
        character_display = gd.display(character)
        if character_display:
            return f"{character_display} ({key})"
    return key


def display_fe15_spell_list(gd, rid, _):
    key = gd.key(rid)
    if key and key.startswith("MSID"):
        pid = "PID_" + key[5:]
        character_rid = gd.key_to_rid("characters", pid)
        if character_rid:
            character_display = gd.display(character_rid)
            if character_display:
                return f"{character_display} ({key})"
    return key


_DISPLAY_FUNCTIONS = {
    "asset": display_asset,
    "combotbl": display_combo_tbl,
    "fe13_character": display_fe13_character,
    "fe13_chapter": display_fe13_chapter,
    "fe13_sprite_data": display_fe13_sprite_data,
    "fe13_reliance_list": display_fe13_reliance_list,
    "fe13_reliance_list_data": display_fe13_reliance_list_data,
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
    "fe15_amiibo": display_fe15_amiibo,
    "fe15_call_table": display_fe15_call_table,
    "fe15_job": display_fe15_job,
    "fe15_job_cc": display_fe15_job_cc,
    "fe15_job_cc_data_item": display_fe15_job_cc_data_item,
    "fe15_food_preferences": display_fe15_food_preferences,
    "fe15_item_evolution": display_fe15_item_evolution,
    "fe15_item_forge": display_fe15_item_forge,
    "fe15_dungeon_enemy_information": display_fe15_dungeon_enemy_information,
    "fe15_spell_list": display_fe15_spell_list,
}


def display_rid(gd, rid, fn, row):
    if fn in _DISPLAY_FUNCTIONS:
        return _DISPLAY_FUNCTIONS[fn](gd, rid, row)
    else:
        return None
