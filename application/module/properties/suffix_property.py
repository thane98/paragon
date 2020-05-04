from module.properties.reference_property import ReferenceProperty


class SuffixProperty(ReferenceProperty):
    def __init__(self, name: str, target_module: str, target_property: str, prefix: str):
        super().__init__(name, target_module, target_property)
        self.prefix = prefix

    @classmethod
    def _from_json(cls, name, json):
        result = SuffixProperty(name, json["target_module"], json["target_property"], json["prefix"])
        result.is_display = json.get("display", False)
        result.is_fallback_display = json.get("fallback_display", False)
        return result

    def read(self, reader):
        self.value = reader.read_string()
        if self.value:
            self.value = self.prefix + self.value

    def write(self, writer):
        if self.value:
            writer.write_string(self.value[len(self.prefix):])
        else:
            writer.write_u32(0)
