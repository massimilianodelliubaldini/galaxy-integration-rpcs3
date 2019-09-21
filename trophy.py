import os
import sys

import xml.etree.ElementTree as ET

from config import Config
from galaxy.api.types import Achievement


class TropConf:
    def __init__(self, trophies_path):
        self.path = os.path.join(trophies_path, 'TROPCONF.SFM')
        self.tree = ET.parse(self.path)
        self.root = self.tree.getroot()


# This metaclass allows us to call 'len(TropUsrHeader)' and get '48'.
class TropMetaclass(type):
    def __len__(self):
        total = 0
        for v in vars(self)['__annotations__'].values():
            total += len(v)
        return total


class TropUsrHeader(object, metaclass=TropMetaclass):
    magic : bytes(4)
    unk1 : bytes(4)
    table_count : bytes(4)
    unk2 : bytes(4)
    reserved : bytes(32)

    # bytestring is only a portion of the file;
    # subscriptors are relative to the start of the portion, not the file.
    def __init__(self, bytestring):
        self.magic = bytestring[0 : 4]
        self.unk1 = bytestring[4 : 8]
        self.table_count = bytestring[8 : 12]
        self.unk2 = bytestring[12 : 16]
        self.reserved = bytestring[16 : 48]


class TropUsrTableHeader(object, metaclass=TropMetaclass):
    table_type : bytes(4)
    entries_size : bytes(4)
    unk1 : bytes(4)
    entries_count : bytes(4)
    offset : bytes(8)
    reserved : bytes(8)

    def __init__(self, bytestring):
        self.table_type = bytestring[0 : 4]
        self.entries_size = bytestring[4 : 8]
        self.unk1 = bytestring[8 : 12]
        self.entries_count = bytestring[12 : 16]
        self.offset = bytestring[16 : 24]
        self.reserved = bytestring[24 : 32]


class TropUsrEntry4(object, metaclass=TropMetaclass):
    # Entry Header
    entry_type : bytes(4)
    entry_size : bytes(4)
    entry_id : bytes(4)
    entry_unk1 : bytes(4)

    # Entry Contents
    trophy_id : bytes(4)
    trophy_grade : bytes(4)
    unk5 : bytes(4)
    unk6 : bytes(68)

    def __init__(self, bytestring):
        # Entry Header
        self.entry_type = bytestring[0 : 4]
        self.entry_size = bytestring[4 : 8]
        self.entry_id = bytestring[8 : 12]
        self.entry_unk1 = bytestring[12 : 16]

        # Entry Contents
        self.trophy_id = bytestring[16 : 20]
        self.trophy_grade = bytestring[20 : 24]
        self.unk5 = bytestring[24 : 28]
        self.unk6 = bytestring[28 : 96]


class TropUsrEntry6(object, metaclass=TropMetaclass):
    # Entry Header
    entry_type : bytes(4)
    entry_size : bytes(4)
    entry_id : bytes(4)
    entry_unk1 : bytes(4)

    # Entry Contents
    trophy_id : bytes(4)
    trophy_state : bytes(4)
    unk4 : bytes(4)
    unk5 : bytes(4)
    timestamp1 : bytes(8)
    timestamp2 : bytes(8)
    unk6 : bytes(64)

    def __init__(self, bytestring):
        # Entry Header
        self.entry_type = bytestring[0 : 4]
        self.entry_size = bytestring[4 : 8]
        self.entry_id = bytestring[8 : 12]
        self.entry_unk1 = bytestring[12 : 16]

        # Entry Contents
        self.trophy_id = bytestring[16 : 20]
        self.trophy_state = bytestring[20 : 24]
        self.unk4 = bytestring[24 : 28]
        self.unk5 = bytestring[28 : 32]
        self.timestamp1 = bytestring[32 : 40]
        self.timestamp2 = bytestring[40 : 48]
        self.unk6 = bytestring[48 : 112]


class TropUsr:
    def __init__(self, trophies_path):
        
        self.file = None
        self.header = None
        self.table_headers = {}
        self.table4 = {}
        self.table6 = {}

        self.path = os.path.join(trophies_path, 'TROPUSR.DAT')
        if os.path.exists(self.path):
            with open(self.path, 'rb') as file:
                self.file = file.read()
        
        self.load()


    def load(self) -> bool:

        # TODO - Generate if none exists.

        if not self.file:
            return False

        if not self.load_header(): 
            raise UnknownError('Error in load_header')
            return False

        if not self.load_table_headers():
            raise UnknownError('Error in load_table_headers')
            return False

        if not self.load_tables():
            raise UnknownError('Error in load_tables')
            return False

        return True


    def load_header(self) -> bool:

        self.header = TropUsrHeader(self.file[0 : len(TropUsrHeader)])

        if b'\x81\x8F\x54\xAD' not in self.header.magic:
            return False

        return True


    def load_table_headers(self) -> bool:

        table_header = None
        table_count = int.from_bytes(self.header.table_count, byteorder='big')

        self.table_headers = {}
        for i in range(table_count):

            table_header = TropUsrTableHeader(self.file[
                len(TropUsrHeader) + (len(TropUsrTableHeader) * i) :
                len(TropUsrHeader) + (len(TropUsrTableHeader) * (i + 1))
                ])

            if b'\x00\x00\x00\x04' not in table_header.table_type and b'\x00\x00\x00\x06' not in table_header.table_type:
                return False

            self.table_headers[i] = table_header

        return True


    def load_tables(self) -> bool:

        table_header = None
        table_count = int.from_bytes(self.header.table_count, byteorder='big')

        for i in range(table_count):

            table_header = self.table_headers[i]
            offset = int.from_bytes(table_header.offset, byteorder='big')
            entries_count = int.from_bytes(table_header.entries_count, byteorder='big')

            if b'\x00\x00\x00\x04' in table_header.table_type:
                self.table4 = {}
                for i in range(entries_count):

                    entry = TropUsrEntry4(self.file[
                        offset + (len(TropUsrEntry4) * i) :
                        offset + (len(TropUsrEntry4) * (i + 1))
                        ])

                    if b'\x00\x00\x00\x04' not in entry.entry_type:
                        return False

                    if b'\x00\x00\x00\x50' not in entry.entry_size:
                        return False

                    trophy_id = int.from_bytes(entry.trophy_id, byteorder='big')
                    self.table4[trophy_id] = entry

            if b'\x00\x00\x00\x06' in table_header.table_type:
                self.table6 = {}
                for i in range(entries_count):

                    entry = TropUsrEntry6(self.file[
                        offset + (len(TropUsrEntry6) * i) :
                        offset + (len(TropUsrEntry6) * (i + 1))
                        ])

                    if b'\x00\x00\x00\x06' not in entry.entry_type:
                        return False

                    if b'\x00\x00\x00\x60' not in entry.entry_size:
                        return False

                    trophy_id = int.from_bytes(entry.trophy_id, byteorder='big')
                    self.table6[trophy_id] = entry

        return True


class Trophy:
    config : Config
    tropconf : TropConf
    tropusr : TropUsr

    def __init__(self, config : Config, game_path : str):

        try:
            self.config = config
            tropdir_path = os.path.join(game_path, 'TROPDIR')
            trophies = os.listdir(tropdir_path)[0]

            trophies_path = self.config.config2path(
                self.config.main_directory, 
                self.config.user_path, 
                'trophy',
                trophies)

            self.tropconf = TropConf(trophies_path)
            self.tropusr = TropUsr(trophies_path)

        except:
            pass


    def trop2ach(self, trophy_id : int) -> Achievement:

        trophy_state = self.tropusr.table6[trophy_id].trophy_state
        unlocked = int.from_bytes(trophy_state, byteorder='big')

        unlock_time = None
        if bool(unlocked):
            unlock_timestamp = self.tropusr.table6[trophy_id].timestamp2
            unlock_time = int.from_bytes(unlock_timestamp, byteorder='big')
        
        pad_tid = format(trophy_id, '03d')
        name = self.tropconf.root.find('.//trophy[@id="' + pad_tid + '"]/name')

        ach = Achievement(unlock_time, None, name.text)
        return ach