import os, json


class ModuleDataService:
    def __init__(self):
        self.entries = {}
        self._parse_data_dir()

    def _parse_data_dir(self):
        files = os.walk("Modules/Data")
        for dir_path, _, file_names in files:
            for file in file_names:
                if file.endswith(".json"):
                    enum = self._try_parse_data_file(os.path.join(dir_path, file))
                    if enum:
                        key = os.path.splitext(os.path.basename(file))[0]
                        self.entries[key] = enum

    @staticmethod
    def _try_parse_data_file(path):
        with open(path, "r") as f:
            js = json.load(f)
            return js
