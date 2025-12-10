#!/usr/bin/env python3
"""
Skylanders Core Library v3.0
============================
Bibliothèque sans GUI pour la manipulation des fichiers .sky.
"""

import hashlib
from Crypto.Cipher import AES
from enum import Enum
from typing import Tuple, Optional


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class SkylandersGame(Enum):
    """Enumération des jeux Skylanders avec leur niveau maximum."""
    SPYROS_ADVENTURE = ("Spyro's Adventure", 10)
    GIANTS = ("Giants", 15)
    SWAP_FORCE = ("Swap Force", 20)
    TRAP_TEAM = ("Trap Team", 20)
    SUPERCHARGERS = ("SuperChargers", 20)
    IMAGINATORS = ("Imaginators", 20)
    UNKNOWN = ("Inconnu", 20)
    
    def __init__(self, display_name: str, max_level: int):
        self.display_name = display_name
        self.max_level = max_level


SKYLANDER_SIZE = 1024

HASH_CONST = bytes([
    0x20, 0x43, 0x6F, 0x70, 0x79, 0x72, 0x69, 0x67, 0x68, 0x74, 0x20, 0x28, 0x43, 0x29, 0x20, 0x32,
    0x30, 0x31, 0x30, 0x20, 0x41, 0x63, 0x74, 0x69, 0x76, 0x69, 0x73, 0x69, 0x6F, 0x6E, 0x2E, 0x20,
    0x41, 0x6C, 0x6C, 0x20, 0x52, 0x69, 0x67, 0x68, 0x74, 0x73, 0x20, 0x52, 0x65, 0x73, 0x65, 0x72,
    0x76, 0x65, 0x64, 0x2E, 0x20
])

SECTOR_TRAILERS = [0x03, 0x07, 0x0B, 0x0F, 0x13, 0x17, 0x1B, 0x1F, 
                   0x23, 0x27, 0x2B, 0x2F, 0x33, 0x37, 0x3B, 0x3F]

MAX_MONEY = 65000
MAX_HERO_POINTS = 255  # Byte max (8-bit), représente probablement les Heroic Challenges complétés

# Tables XP par niveau (index = niveau, valeur = XP minimum pour ce niveau)
# SSA: Niveau 10 max = 33,000 XP
# Index 1 = niveau 1, Index 10 = niveau 10
XP_TABLE_LEVEL_10 = {
    1: 0, 2: 100, 3: 400, 4: 1000, 5: 2000,
    6: 4000, 7: 7500, 8: 13000, 9: 20000, 10: 28000
}
XP_MAX_LEVEL_10 = 33000

# Giants: Niveau 15 max ≈ 96,500 XP
XP_TABLE_LEVEL_15 = {
    1: 0, 2: 100, 3: 400, 4: 1000, 5: 2000,
    6: 4000, 7: 7500, 8: 13000, 9: 20000, 10: 28000,
    11: 33000, 12: 45000, 13: 58000, 14: 73000, 15: 88000
}
XP_MAX_LEVEL_15 = 96500

# Swap Force/Trap Team/SuperChargers/Imaginators: Niveau 20 max ≈ 197,000 XP
XP_TABLE_LEVEL_20 = {
    1: 0, 2: 100, 3: 400, 4: 1000, 5: 2000,
    6: 4000, 7: 7500, 8: 13000, 9: 20000, 10: 28000,
    11: 33000, 12: 45000, 13: 58000, 14: 73000, 15: 88000,
    16: 105000, 17: 125000, 18: 148000, 19: 175000, 20: 190000
}
XP_MAX_LEVEL_20 = 197000


# ============================================================================
# BASE DE DONNÉES SKYLANDERS
# ============================================================================

SKYLANDERS_DB = {
    # Spyro's Adventure (0-32)
    0: ("Whirlwind", SkylandersGame.SPYROS_ADVENTURE),
    1: ("Sonic Boom", SkylandersGame.SPYROS_ADVENTURE),
    2: ("Warnado", SkylandersGame.SPYROS_ADVENTURE),
    3: ("Lightning Rod", SkylandersGame.SPYROS_ADVENTURE),
    4: ("Bash", SkylandersGame.SPYROS_ADVENTURE),
    5: ("Terrafin", SkylandersGame.SPYROS_ADVENTURE),
    6: ("Dino-Rang", SkylandersGame.SPYROS_ADVENTURE),
    7: ("Prism Break", SkylandersGame.SPYROS_ADVENTURE),
    8: ("Sunburn", SkylandersGame.SPYROS_ADVENTURE),
    9: ("Eruptor", SkylandersGame.SPYROS_ADVENTURE),
    10: ("Ignitor", SkylandersGame.SPYROS_ADVENTURE),
    11: ("Flameslinger", SkylandersGame.SPYROS_ADVENTURE),
    12: ("Zap", SkylandersGame.SPYROS_ADVENTURE),
    13: ("Wham-Shell", SkylandersGame.SPYROS_ADVENTURE),
    14: ("Gill Grunt", SkylandersGame.SPYROS_ADVENTURE),
    15: ("Slam Bam", SkylandersGame.SPYROS_ADVENTURE),
    16: ("Spyro", SkylandersGame.SPYROS_ADVENTURE),
    17: ("Voodood", SkylandersGame.SPYROS_ADVENTURE),
    18: ("Double Trouble", SkylandersGame.SPYROS_ADVENTURE),
    19: ("Trigger Happy", SkylandersGame.SPYROS_ADVENTURE),
    20: ("Drobot", SkylandersGame.SPYROS_ADVENTURE),
    21: ("Drill Sergeant", SkylandersGame.SPYROS_ADVENTURE),
    22: ("Boomer", SkylandersGame.SPYROS_ADVENTURE),
    23: ("Wrecking Ball", SkylandersGame.SPYROS_ADVENTURE),
    24: ("Camo", SkylandersGame.SPYROS_ADVENTURE),
    25: ("Zook", SkylandersGame.SPYROS_ADVENTURE),
    26: ("Stealth Elf", SkylandersGame.SPYROS_ADVENTURE),
    27: ("Stump Smash", SkylandersGame.SPYROS_ADVENTURE),
    28: ("Dark Spyro", SkylandersGame.SPYROS_ADVENTURE),
    29: ("Hex", SkylandersGame.SPYROS_ADVENTURE),
    30: ("Chop Chop", SkylandersGame.SPYROS_ADVENTURE),
    31: ("Ghost Roaster", SkylandersGame.SPYROS_ADVENTURE),
    32: ("Cynder", SkylandersGame.SPYROS_ADVENTURE),
    
    # Giants (100-115)
    100: ("Jet-Vac", SkylandersGame.GIANTS),
    101: ("Swarm", SkylandersGame.GIANTS),
    102: ("Crusher", SkylandersGame.GIANTS),
    103: ("Flashwing", SkylandersGame.GIANTS),
    104: ("Hot Head", SkylandersGame.GIANTS),
    105: ("Hot Dog", SkylandersGame.GIANTS),
    106: ("Chill", SkylandersGame.GIANTS),
    107: ("Thumpback", SkylandersGame.GIANTS),
    108: ("Pop Fizz", SkylandersGame.GIANTS),
    109: ("Ninjini", SkylandersGame.GIANTS),
    110: ("Bouncer", SkylandersGame.GIANTS),
    111: ("Sprocket", SkylandersGame.GIANTS),
    112: ("Tree Rex", SkylandersGame.GIANTS),
    113: ("Shroomboom", SkylandersGame.GIANTS),
    114: ("Eye-Brawl", SkylandersGame.GIANTS),
    115: ("Fright Rider", SkylandersGame.GIANTS),
    
    # Trap Team (450-485)
    450: ("Gusto", SkylandersGame.TRAP_TEAM),
    451: ("Thunderbolt", SkylandersGame.TRAP_TEAM),
    452: ("Fling Kong", SkylandersGame.TRAP_TEAM),
    453: ("Blades", SkylandersGame.TRAP_TEAM),
    454: ("Wallop", SkylandersGame.TRAP_TEAM),
    455: ("Head Rush", SkylandersGame.TRAP_TEAM),
    456: ("Fist Bump", SkylandersGame.TRAP_TEAM),
    457: ("Rocky Roll", SkylandersGame.TRAP_TEAM),
    458: ("Wildfire", SkylandersGame.TRAP_TEAM),
    459: ("Ka-Boom", SkylandersGame.TRAP_TEAM),
    460: ("Trail Blazer", SkylandersGame.TRAP_TEAM),
    461: ("Torch", SkylandersGame.TRAP_TEAM),
    462: ("Snap Shot", SkylandersGame.TRAP_TEAM),
    463: ("Lob-Star", SkylandersGame.TRAP_TEAM),
    464: ("Flip Wreck", SkylandersGame.TRAP_TEAM),
    465: ("Echo", SkylandersGame.TRAP_TEAM),
    466: ("Blastermind", SkylandersGame.TRAP_TEAM),
    467: ("Enigma", SkylandersGame.TRAP_TEAM),
    468: ("Déjà Vu", SkylandersGame.TRAP_TEAM),
    469: ("Cobra Cadabra", SkylandersGame.TRAP_TEAM),
    470: ("Jawbreaker", SkylandersGame.TRAP_TEAM),
    471: ("Gearshift", SkylandersGame.TRAP_TEAM),
    472: ("Chopper", SkylandersGame.TRAP_TEAM),
    473: ("Tread Head", SkylandersGame.TRAP_TEAM),
    474: ("Bushwhack", SkylandersGame.TRAP_TEAM),
    475: ("Tuff Luck", SkylandersGame.TRAP_TEAM),
    476: ("Food Fight", SkylandersGame.TRAP_TEAM),
    477: ("High Five", SkylandersGame.TRAP_TEAM),
    478: ("Krypt King", SkylandersGame.TRAP_TEAM),
    479: ("Short Cut", SkylandersGame.TRAP_TEAM),
    480: ("Bat Spin", SkylandersGame.TRAP_TEAM),
    481: ("Funny Bone", SkylandersGame.TRAP_TEAM),
    482: ("Knight Light", SkylandersGame.TRAP_TEAM),
    483: ("Spotlight", SkylandersGame.TRAP_TEAM),
    484: ("Knight Mare", SkylandersGame.TRAP_TEAM),
    485: ("Blackout", SkylandersGame.TRAP_TEAM),
    
    # Imaginators Senseis (601-631)
    601: ("King Pen", SkylandersGame.IMAGINATORS),
    602: ("Tri-Tip", SkylandersGame.IMAGINATORS),
    603: ("Chopscotch", SkylandersGame.IMAGINATORS),
    604: ("Boom Bloom", SkylandersGame.IMAGINATORS),
    605: ("Pit Boss", SkylandersGame.IMAGINATORS),
    606: ("Barbella", SkylandersGame.IMAGINATORS),
    607: ("Air Strike", SkylandersGame.IMAGINATORS),
    608: ("Ember", SkylandersGame.IMAGINATORS),
    609: ("Ambush", SkylandersGame.IMAGINATORS),
    610: ("Dr. Krankcase", SkylandersGame.IMAGINATORS),
    611: ("Hood Sickle", SkylandersGame.IMAGINATORS),
    612: ("Tae Kwon Crow", SkylandersGame.IMAGINATORS),
    613: ("Golden Queen", SkylandersGame.IMAGINATORS),
    614: ("Wolfgang", SkylandersGame.IMAGINATORS),
    615: ("Pain-Yatta", SkylandersGame.IMAGINATORS),
    616: ("Mysticat", SkylandersGame.IMAGINATORS),
    617: ("Starcast", SkylandersGame.IMAGINATORS),
    618: ("Buckshot", SkylandersGame.IMAGINATORS),
    619: ("Aurora", SkylandersGame.IMAGINATORS),
    620: ("Flare Wolf", SkylandersGame.IMAGINATORS),
    621: ("Chompy Mage", SkylandersGame.IMAGINATORS),
    622: ("Bad Juju", SkylandersGame.IMAGINATORS),
    623: ("Grave Clobber", SkylandersGame.IMAGINATORS),
    624: ("Blaster-Tron", SkylandersGame.IMAGINATORS),
    625: ("Ro-Bow", SkylandersGame.IMAGINATORS),
    626: ("Chain Reaction", SkylandersGame.IMAGINATORS),
    627: ("Kaos", SkylandersGame.IMAGINATORS),
    628: ("Wild Storm", SkylandersGame.IMAGINATORS),
    629: ("Tidepool", SkylandersGame.IMAGINATORS),
    630: ("Crash Bandicoot", SkylandersGame.IMAGINATORS),
    631: ("Dr. Neo Cortex", SkylandersGame.IMAGINATORS),
    
    # SWAP Force - Tops (2000-2015)
    2000: ("Boom (Top)", SkylandersGame.SWAP_FORCE),
    2001: ("Free (Top)", SkylandersGame.SWAP_FORCE),
    2002: ("Rubble (Top)", SkylandersGame.SWAP_FORCE),
    2003: ("Doom (Top)", SkylandersGame.SWAP_FORCE),
    2004: ("Blast (Top)", SkylandersGame.SWAP_FORCE),
    2005: ("Fire (Top)", SkylandersGame.SWAP_FORCE),
    2006: ("Stink (Top)", SkylandersGame.SWAP_FORCE),
    2007: ("Grilla (Top)", SkylandersGame.SWAP_FORCE),
    2008: ("Hoot (Top)", SkylandersGame.SWAP_FORCE),
    2009: ("Trap (Top)", SkylandersGame.SWAP_FORCE),
    2010: ("Magna (Top)", SkylandersGame.SWAP_FORCE),
    2011: ("Spy (Top)", SkylandersGame.SWAP_FORCE),
    2012: ("Night (Top)", SkylandersGame.SWAP_FORCE),
    2013: ("Rattle (Top)", SkylandersGame.SWAP_FORCE),
    2014: ("Freeze (Top)", SkylandersGame.SWAP_FORCE),
    2015: ("Wash (Top)", SkylandersGame.SWAP_FORCE),
    
    # SuperChargers (3400-3428)
    3400: ("Fiesta", SkylandersGame.SUPERCHARGERS),
    3401: ("High Volt", SkylandersGame.SUPERCHARGERS),
    3402: ("Splat", SkylandersGame.SUPERCHARGERS),
    3406: ("Stormblade", SkylandersGame.SUPERCHARGERS),
    3411: ("Smash Hit", SkylandersGame.SUPERCHARGERS),
    3412: ("Spitfire", SkylandersGame.SUPERCHARGERS),
    3413: ("Hurricane Jet-Vac", SkylandersGame.SUPERCHARGERS),
    3414: ("Double Dare Trigger Happy", SkylandersGame.SUPERCHARGERS),
    3415: ("Super Shot Stealth Elf", SkylandersGame.SUPERCHARGERS),
    3416: ("Shark Shooter Terrafin", SkylandersGame.SUPERCHARGERS),
    3417: ("Bone Bash Roller Brawl", SkylandersGame.SUPERCHARGERS),
    3420: ("Big Bubble Pop Fizz", SkylandersGame.SUPERCHARGERS),
    3421: ("Lava Lance Eruptor", SkylandersGame.SUPERCHARGERS),
    3422: ("Deep Dive Gill Grunt", SkylandersGame.SUPERCHARGERS),
    3423: ("Turbo Charge Donkey Kong", SkylandersGame.SUPERCHARGERS),
    3424: ("Hammer Slam Bowser", SkylandersGame.SUPERCHARGERS),
    3425: ("Dive-Clops", SkylandersGame.SUPERCHARGERS),
    3426: ("Astroblast", SkylandersGame.SUPERCHARGERS),
    3427: ("Nightfall", SkylandersGame.SUPERCHARGERS),
    3428: ("Thrillipede", SkylandersGame.SUPERCHARGERS),
}


# ============================================================================
# CRYPTO FUNCTIONS
# ============================================================================

def compute_key(sector0: bytes, block_index: int) -> bytes:
    key_material = bytearray(sector0[:0x20])
    key_material.append(block_index & 0xFF)
    key_material.extend(HASH_CONST)
    return hashlib.md5(bytes(key_material)).digest()


def decrypt_block(encrypted: bytes, sector0: bytes, block_index: int) -> bytes:
    return AES.new(compute_key(sector0, block_index), AES.MODE_ECB).decrypt(encrypted)


def encrypt_block(plain: bytes, sector0: bytes, block_index: int) -> bytes:
    return AES.new(compute_key(sector0, block_index), AES.MODE_ECB).encrypt(plain)


# ============================================================================
# CRC-16 CCITT
# ============================================================================

class CRC16:
    _table: Optional[list] = None
    
    @classmethod
    def _init_table(cls) -> None:
        if cls._table is not None:
            return
        cls._table = []
        for i in range(256):
            crc = i << 8
            for _ in range(8):
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
            cls._table.append(crc)
    
    @classmethod
    def calculate(cls, data: bytes) -> int:
        cls._init_table()
        crc = 0xFFFF
        for byte in data:
            crc = ((crc << 8) ^ cls._table[((crc >> 8) ^ byte) & 0xFF]) & 0xFFFF
        return crc


# ============================================================================
# SKYLANDER CLASS
# ============================================================================

class Skylander:
    def __init__(self, data: bytes):
        if len(data) != SKYLANDER_SIZE:
            raise ValueError(f"Taille invalide: {len(data)} octets (attendu: {SKYLANDER_SIZE})")
        self.data = bytearray(data)
        self._decrypted = False
    
    def decrypt(self) -> None:
        if self._decrypted:
            return
        sector0 = bytes(self.data[:0x20])
        for block in range(0x08, 0x40):
            if block in SECTOR_TRAILERS:
                continue
            offset = block * 16
            decrypted = decrypt_block(bytes(self.data[offset:offset+16]), sector0, block)
            self.data[offset:offset+16] = decrypted
        self._decrypted = True
    
    def encrypt(self) -> bytes:
        sector0 = bytes(self.data[:0x20])
        result = bytearray(self.data)
        for block in range(0x08, 0x40):
            if block in SECTOR_TRAILERS:
                continue
            offset = block * 16
            encrypted = encrypt_block(bytes(self.data[offset:offset+16]), sector0, block)
            result[offset:offset+16] = encrypted
        return bytes(result)
    
    def get_character_id(self) -> int:
        return self.data[0x10] | (self.data[0x11] << 8)
    
    def get_variant_id(self) -> int:
        return self.data[0x1C] | (self.data[0x1D] << 8)
    
    def get_character_info(self) -> Tuple[str, SkylandersGame]:
        cid = self.get_character_id()
        if cid in SKYLANDERS_DB:
            return SKYLANDERS_DB[cid]
        return (f"Inconnu (ID: {cid})", self._detect_game_from_id(cid))
    
    def _detect_game_from_id(self, cid: int) -> SkylandersGame:
        if 0 <= cid <= 32 or (400 <= cid <= 450):
            return SkylandersGame.SPYROS_ADVENTURE
        elif 100 <= cid <= 199:
            return SkylandersGame.GIANTS
        elif 450 <= cid <= 599:
            return SkylandersGame.TRAP_TEAM
        elif 600 <= cid <= 699:
            return SkylandersGame.IMAGINATORS
        elif 1000 <= cid <= 3099:
            return SkylandersGame.SWAP_FORCE
        elif 3400 <= cid <= 3599:
            return SkylandersGame.SUPERCHARGERS
        return SkylandersGame.UNKNOWN
    
    def get_game(self) -> SkylandersGame:
        _, game = self.get_character_info()
        return game
    
    def get_max_level(self) -> int:
        return self.get_game().max_level
    
    def get_xp_table(self) -> dict:
        """Retourne la table XP appropriée pour ce jeu."""
        max_level = self.get_max_level()
        if max_level == 10:
            return XP_TABLE_LEVEL_10
        elif max_level == 15:
            return XP_TABLE_LEVEL_15
        return XP_TABLE_LEVEL_20
    
    def get_max_xp(self) -> int:
        """Retourne l'XP maximum pour ce jeu."""
        max_level = self.get_max_level()
        if max_level == 10:
            return XP_MAX_LEVEL_10
        elif max_level == 15:
            return XP_MAX_LEVEL_15
        return XP_MAX_LEVEL_20
    
    def get_active_area(self) -> int:
        seq0 = self.data[0x80 + 0x09]
        seq1 = self.data[0x240 + 0x09]
        return 0 if seq0 >= seq1 else 1
    
    def _header_offset(self, area: Optional[int] = None) -> int:
        if area is None:
            area = self.get_active_area()
        return 0x80 if area == 0 else 0x240
    
    def get_xp(self) -> int:
        off = self._header_offset()
        return self.data[off] | (self.data[off+1] << 8) | (self.data[off+2] << 16)
    
    def set_xp(self, xp: int) -> None:
        xp = max(0, min(xp, self.get_max_xp()))
        for area in [0, 1]:
            off = self._header_offset(area)
            self.data[off] = xp & 0xFF
            self.data[off+1] = (xp >> 8) & 0xFF
            self.data[off+2] = (xp >> 16) & 0xFF
    
    def get_level(self) -> int:
        """Calcule le niveau actuel basé sur l'XP."""
        xp = self.get_xp()
        xp_table = self.get_xp_table()
        max_level = self.get_max_level()
        
        # Parcourir du niveau max vers le niveau 1
        for level in range(max_level, 0, -1):
            if xp >= xp_table[level]:
                return level
        return 1
    
    def set_level(self, level: int) -> None:
        """Définit le niveau en ajustant l'XP au minimum requis pour ce niveau."""
        xp_table = self.get_xp_table()
        max_level = self.get_max_level()
        level = max(1, min(level, max_level))
        self.set_xp(xp_table[level])
    
    def get_money(self) -> int:
        off = self._header_offset()
        return self.data[off+3] | (self.data[off+4] << 8)
    
    def set_money(self, money: int) -> None:
        money = max(0, min(money, MAX_MONEY))
        for area in [0, 1]:
            off = self._header_offset(area)
            self.data[off+3] = money & 0xFF
            self.data[off+4] = (money >> 8) & 0xFF
    
    def get_hero_points(self) -> int:
        off = self._header_offset()
        return self.data[off+5]
    
    def set_hero_points(self, points: int) -> None:
        points = max(0, min(points, MAX_HERO_POINTS))
        for area in [0, 1]:
            off = self._header_offset(area)
            self.data[off+5] = points
    
    def update_checksums(self) -> None:
        for area in [0, 1]:
            hdr_block = 0x08 if area == 0 else 0x24
            hb = hdr_block * 16
            
            if area == 0:
                type2_blocks = [0x09, 0x0A, 0x0C]
                type3_blocks = [0x0D, 0x0E, 0x10]
            else:
                type2_blocks = [0x25, 0x26, 0x28]
                type3_blocks = [0x29, 0x2A, 0x2C]
            
            type3_data = b''.join(bytes(self.data[b*16:(b+1)*16]) for b in type3_blocks)
            type3_data += b'\x00' * (0x0E * 16)
            crc3 = CRC16.calculate(type3_data)
            self.data[hb + 0x0A] = crc3 & 0xFF
            self.data[hb + 0x0B] = (crc3 >> 8) & 0xFF
            
            type2_data = b''.join(bytes(self.data[b*16:(b+1)*16]) for b in type2_blocks)
            crc2 = CRC16.calculate(type2_data)
            self.data[hb + 0x0C] = crc2 & 0xFF
            self.data[hb + 0x0D] = (crc2 >> 8) & 0xFF
            
            self.data[hb + 0x09] = (self.data[hb + 0x09] + 1) & 0xFF
            
            header_copy = bytearray(self.data[hb:hb+16])
            header_copy[0x0E] = 0x05
            header_copy[0x0F] = 0x00
            crc1 = CRC16.calculate(bytes(header_copy))
            self.data[hb + 0x0E] = crc1 & 0xFF
            self.data[hb + 0x0F] = (crc1 >> 8) & 0xFF
        
        crc0 = CRC16.calculate(bytes(self.data[:0x1E]))
        self.data[0x1E] = crc0 & 0xFF
        self.data[0x1F] = (crc0 >> 8) & 0xFF
    
    def max_out(self) -> None:
        self.set_xp(self.get_max_xp())
        self.set_money(MAX_MONEY)
        self.set_hero_points(MAX_HERO_POINTS)
    
    def reset_stats(self) -> None:
        self.set_xp(0)
        self.set_money(0)
        self.set_hero_points(0)
