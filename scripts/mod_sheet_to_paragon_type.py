import sys
import yaml
from yaml import Dumper

with open(sys.argv[1], "r", encoding="utf-8") as f:
    raw = f.readlines()

size = 0
for line in raw:
    if not line:
        continue
    name, data_type = line.strip().split(": ")
    name = "_".join(map(lambda s: s.lower(), name.split(" ")))
    print("- id:", name)
    if data_type == "str":
        print("  type: string")
        size += 4
    elif data_type == "u8":
        print("  type: int")
        print("  format: u8")
        size += 1
    elif data_type == "s8":
        print("  type: int")
        print("  format: i8")
        size += 1
    elif data_type == "f32":
        print("  type: float")
        size += 4
    elif data_type == "u16":
        print("  type: int")
        print("  format: u16")
        size += 2
    elif data_type == "s16":
        print("  type: int")
        print("  format: i16")
        size += 2
    elif data_type == "u32" or data_type == "s32":
        print("  type: int")
        print("  format: i32")
        size += 4
    else:
        raise NotImplementedError(data_type)

print()
print("size:", size)
