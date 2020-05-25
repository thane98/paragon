class BinArchiveReader:
    def __init__(self, archive, position=0):
        self.position = position
        self.archive = archive
        self.read_cache = {}

    def get_archive(self):
        return self.archive

    def seek(self, position):
        self.position = position

    def tell(self):
        return self.position

    def read_object(self, template):
        target_addr = self.read_internal_pointer()
        if not target_addr:
            return None
        if target_addr in self.read_cache:
            return self.read_cache[target_addr]

        end_addr = self.position
        self.position = target_addr
        elem = template.duplicate()
        for prop in elem.values():
            prop.offset = self.position - target_addr
            prop.read(self)
        self.read_cache[target_addr] = elem
        self.position = end_addr
        return elem

    def read_u8(self):
        value = self.archive.read_u8(self.position)
        self.position += 1
        return value

    def read_i8(self):
        value = self.archive.read_i8(self.position)
        self.position += 1
        return value

    def read_u16(self):
        value = self.archive.read_u16(self.position)
        self.position += 2
        return value

    def read_i16(self):
        value = self.archive.read_i16(self.position)
        self.position += 2
        return value

    def read_u32(self):
        value = self.archive.read_u32(self.position)
        self.position += 4
        return value

    def read_i32(self):
        value = self.archive.read_i32(self.position)
        self.position += 4
        return value

    def read_f32(self):
        value = self.archive.read_f32(self.position)
        self.position += 4
        return value

    def read_string(self):
        value = self.archive.read_string(self.position)
        self.position += 4
        return value

    def read_utf16_string(self):
        byte1 = self.read_u8()
        byte2 = self.read_u8()
        raw_str = bytearray()
        while byte1 != 0 or byte2 != 0:
            raw_str.append(byte1)
            raw_str.append(byte2)
            byte1 = self.read_u8()
            byte2 = self.read_u8()
        while self.position % 4 != 0:
            self.position += 1
        return raw_str.decode("utf-16")

    def read_shift_jis_string(self):
        next_char = self.read_u8()
        raw_str = bytearray()
        while next_char != 0:
            raw_str.append(next_char)
            next_char = self.read_u8()
        while self.position % 4 != 0:
            self.position += 1
        return raw_str.decode("shift-jis")

    def read_mapped(self, index=0):
        return self.archive.read_mapped(self.position, index)

    def read_internal_pointer(self):
        result = self.archive.read_internal(self.position)
        self.position += 4
        return result

    def read_bytes(self, amount):
        result = []
        for _ in range(0, amount):
            result.append(self.read_u8())
        return result


class BinArchiveWriter:
    def __init__(self, archive, position=0):
        self.position = position
        self.archive = archive

    def get_archive(self):
        return self.archive

    def seek(self, position):
        self.position = position

    def tell(self):
        return self.position

    def write_u8(self, value):
        if value is None:
            value = 0
        self.archive.put_u8(self.position, value)
        self.position += 1

    def write_i8(self, value):
        if value is None:
            value = 0
        self.archive.put_i8(self.position, value)
        self.position += 1

    def write_u16(self, value):
        if value is None:
            value = 0
        self.archive.put_u16(self.position, value)
        self.position += 2

    def write_i16(self, value):
        if value is None:
            value = 0
        self.archive.put_i16(self.position, value)
        self.position += 2

    def write_u32(self, value):
        if value is None:
            value = 0
        self.archive.put_u32(self.position, value)
        self.position += 4

    def write_i32(self, value):
        if value is None:
            value = 0
        self.archive.put_i32(self.position, value)
        self.position += 4

    def write_f32(self, value):
        if value is None:
            value = 0
        self.archive.put_f32(self.position, value)
        self.position += 4

    def write_string(self, value):
        if not value:
            self.archive.clear_text_pointer(self.position)
            self.write_u32(0)
        else:
            self.archive.set_text_pointer(self.position, value)
            self.position += 4

    def write_mapped(self, value):
        if not value:
            self.archive.clear_mapped_pointer(self.position)
        else:
            self.archive.set_mapped_pointer(self.position, value)

    def write_pointer(self, value):
        if not value:
            self.archive.clear_internal_pointer(self.position)
        else:
            self.archive.set_internal_pointer(self.position, value)
        self.position += 4

    def write_bytes(self, value):
        for byte in value:
            self.write_u8(byte)
