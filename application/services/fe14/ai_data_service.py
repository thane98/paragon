import logging
from typing import List

from core.bin_streams import BinArchiveReader
from services.service_locator import locator

_AI_DATA_PATH = "/GameData/AIData.bin.lz"


class AIDataService:
    def __init__(self):
        self._loaded = False
        self.ac = []
        self.at = []
        self.mi = []
        self.mv = []

    def get_ac_labels(self) -> List[str]:
        if not self._loaded:
            self._try_load_ai_data()
        return self.ac

    def get_at_labels(self) -> List[str]:
        if not self._loaded:
            self._try_load_ai_data()
        return self.at

    def get_mi_labels(self) -> List[str]:
        if not self._loaded:
            self._try_load_ai_data()
        return self.mi

    def get_mv_labels(self) -> List[str]:
        if not self._loaded:
            self._try_load_ai_data()
        return self.mv

    def _try_load_ai_data(self):
        self._loaded = True
        open_files_service = locator.get_scoped("OpenFilesService")
        try:
            bin_archive = open_files_service.open(_AI_DATA_PATH)
            reader = BinArchiveReader(bin_archive)
            ac_ptr = reader.read_internal_pointer()
            mi_ptr = reader.read_internal_pointer()
            at_ptr = reader.read_internal_pointer()
            mv_ptr = reader.read_internal_pointer()
            ac_table = self._read_null_terminated_list(reader, ac_ptr)
            mi_table = self._read_null_terminated_list(reader, mi_ptr)
            at_table = self._read_null_terminated_list(reader, at_ptr)
            mv_table = self._read_null_terminated_list(reader, mv_ptr)

            ac_labels = self._read_mapped_pointers(reader, ac_table)
            mi_labels = self._read_mapped_pointers(reader, mi_table)
            at_labels = self._read_mapped_pointers(reader, at_table)
            mv_labels = self._read_mapped_pointers(reader, mv_table)

            self.ac = ac_labels
            self.mi = mi_labels
            self.at = at_labels
            self.mv = mv_labels
        except:
            logging.exception("Unable to load AI data.")

    @staticmethod
    def _read_null_terminated_list(reader: BinArchiveReader, address: int) -> List[int]:
        result = []
        reader.seek(address)
        next_pointer = reader.read_internal_pointer()
        while next_pointer:
            result.append(next_pointer)
            next_pointer = reader.read_internal_pointer()
        return result

    @staticmethod
    def _read_mapped_pointers(reader: BinArchiveReader, addresses: List[int]) -> List[str]:
        result = []
        for address in addresses:
            reader.seek(address)
            label = reader.read_mapped()
            if label:
                result.append(label)
        return result
