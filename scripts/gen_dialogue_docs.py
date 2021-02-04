import sys
import yaml
import json
from yaml import Loader


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Format: python gen_dialogue_docs.py <Spec Path>")
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = yaml.load(f, Loader=Loader)
    
    result = []
    for entry in data:
        key = entry
        entry = data[entry]
        hint = entry["hint"]
        args = entry["args"]
        arg_hints = list(map(lambda a: f"<strong><font color=\"#0000FF\">{a}</font></strong>: <strong><font color=\"#1b8b51\">{args[a]}</font></strong>", args))
        if arg_hints:
            arg_str = "(" + ", ".join(arg_hints) + ")"
        else:
            arg_str = ""
        hint_str = f"<strong><font color =\"#8b008b\">{key}</font></strong>{arg_str}<br><strong>Effect</strong>: {hint}"
        result.append({
            "Command": key,
            "Args": entry.get("completion_type", ""),
            "Hint": hint_str
        })
    print(json.dumps(result, ensure_ascii=False, indent=2))
