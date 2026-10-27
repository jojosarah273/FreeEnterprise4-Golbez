from . import databases
from .address import UnheaderedAddress

STARTING_WHITE = [
    '#Hold', '#Mute', '#Charm', '#Blink',
    '#Fast', '#Peep', '#Cure1', '#Cure2',
    '#Heal', '#Life1', '#Size', '#Exit',
    '#Sight', '#Float'
    ]

STARTING_WHITE_JAPANESE = [
    '#Armor', '#Shell', '#Dspel'
    ]

STARTING_BLACK = [
    '#Toad', '#Piggy', '#Warp', '#Venom',
    '#Fire1', '#Fire2', '#Ice1', '#Ice2',
    '#Lit1', '#Lit2', '#Sleep', '#Stone',
    '#Drain', '#Psych'
    ]

JAPANESE_EXCLUSIVE_SPELLS = [
    '#spell.Armor', '#spell.Shell', '#spell.Dspel'
    ]

ALL_SPELLS_BY_LEVEL = {
    '#spell.Ice1'  : 1,
    '#spell.Cure1' : 0,
    '#spell.Sight' : 0,
    '#spell.Lit1'  : 1,
    '#spell.Peep'  : 0,
    '#spell.Fire1' : 1,
    '#spell.Hold'  : 0,
    '#spell.Sleep' : 1,
    '#spell.Slow'  : 0,
    '#spell.Venom' : 1,
    '#spell.Ice2'  : 1,
    '#spell.Life1' : 0,
    '#spell.Piggy' : 1,
    '#spell.Armor' : 0,
    '#spell.Fire2' : 1,
    '#spell.Cure2' : 0,
    '#spell.Lit2'  : 1,
    '#spell.Stop'  : 1,
    '#spell.Mute'  : 0,
    '#spell.Bersk' : 0,
    '#spell.Exit'  : 0,
    '#spell.Virus' : 1,
    '#spell.Heal'  : 0,
    '#spell.Toad'  : 1,
    '#spell.Blink' : 0,
    '#spell.Quake' : 1,
    '#spell.Charm' : 0,
    '#spell.Drain' : 1,
    '#spell.Shell' : 0,
    '#spell.Warp'  : 1,
    '#spell.Dspel' : 0,
    '#spell.Size'  : 0,
    '#spell.Ice3'  : 1,
    '#spell.Cure3' : 0,
    '#spell.Fire3' : 1,
    '#spell.Lit3'  : 1,
    '#spell.Stone' : 1,
    '#spell.Fast'  : 0,
    '#spell.Float' : 0,
    '#spell.Cure4' : 0,
    '#spell.Psych' : 1,
    '#spell.Wall'  : 0,
    '#spell.Life2' : 0,
    '#spell.Fatal' : 1,
    '#spell.Weak'  : 1,
    '#spell.White' : 0,
    '#spell.Meteo' : 1,
    '#spell.Nuke'  : 1,
    }

ALL_SPELLS_BY_GOODNESS = {
    '#spell.Sight' : 0,
    '#spell.Peep'  : 0,
    '#spell.Cure1' : 0,
    '#spell.Venom' : 1,
    '#spell.Toad'  : 1,
    '#spell.Piggy' : 1,
    '#spell.Ice1'  : 1,
    '#spell.Lit1'  : 1,
    '#spell.Fire1' : 1,
    '#spell.Sleep' : 1,
    '#spell.Charm' : 0,
    '#spell.Drain' : 1,
    '#spell.Shell' : 0,
    '#spell.Psych' : 1,
    '#spell.Mute'  : 0,
    '#spell.Size'  : 0,
    '#spell.Armor' : 0,
    '#spell.Dspel' : 0,

    '#spell.Slow'  : 0,
    '#spell.Cure2' : 0,
    '#spell.Float' : 0,
    '#spell.Hold'  : 0,
    '#spell.Blink' : 0,
    '#spell.Ice2'  : 1,
    '#spell.Life1' : 0,
    '#spell.Fire2' : 1,
    '#spell.Lit2'  : 1,
    '#spell.Stop'  : 1,
    '#spell.Exit'  : 0,
    '#spell.Heal'  : 0,
    '#spell.Warp'  : 1,
    '#spell.Cure3' : 0,
    '#spell.Stone' : 1,
    '#spell.Fast'  : 0,
    '#spell.Wall'  : 0,

    '#spell.Virus' : 1,
    '#spell.Fire3' : 1,
    '#spell.Ice3'  : 1,
    '#spell.Lit3'  : 1,
    '#spell.Quake' : 1,
    '#spell.Bersk' : 0,
    '#spell.Cure4' : 0,
    '#spell.Life2' : 0,
    '#spell.Fatal' : 1,
    '#spell.Weak'  : 1,
    '#spell.Meteo' : 1,
    '#spell.White' : 0,
    '#spell.Nuke'  : 1,
    }


def _build_stats_record():
    # CharProp_000c: the Golbez job record used by the playable slot.
    # Level 30 Golbez baseline.
    record = bytearray(0x20)
    record[0] = 0x93          # axtor 0x13 + flags
    record[1] = 0x0D          # job: Golbez slot
    record[2] = 30            # level
    record[7:9] = (2971).to_bytes(2, 'little')   # max HP
    record[9:11] = (2971).to_bytes(2, 'little')  # HP
    record[11:13] = (230).to_bytes(2, 'little')  # max MP
    record[13:15] = (230).to_bytes(2, 'little')  # MP
    # STR, SPD/AGI, STA, INT, SPR
    record[15:20] = bytes([30, 20, 33, 30, 25])
    record[20:32] = bytes.fromhex('000032f9600f001000f9600f')
    return bytes(record)


def _build_levelup_table():
    # Entries are 5 bytes: [stat gain mask | 0-7 amount], HP gain,
    # MP gain (low 5 bits), EXP to next level (16-bit).
    # This table starts at level 30 and is pointed at by LevelUpPropPtrs.
    entries = []
    for i in range(99 - 30):  # 30 -> 98
        bits = 0x01           # gain amount 1
        if i < 44: bits |= 0x80  # STR
        if i < 25: bits |= 0x40  # SPD
        if i < 48: bits |= 0x20  # STA
        if i < 38: bits |= 0x10  # INT
        if i < 17: bits |= 0x08  # SPR
        hp_gain = 64
        mp_gain = 7 if i < 46 else 6
        exp = 0x1000
        entries.append(bytes([bits, hp_gain, mp_gain, exp & 0xFF, (exp >> 8) & 0xFF]))
    entries.append(bytes([0, 0, 0, 0, 0]))  # level 99 placeholder
    return b''.join(entries)


def apply(env):
    initial_black = [
        '#Fire1', '#Fire2', '#Fire3',
        '#Ice1', '#Ice2', '#Ice3',
        '#Lit1', '#Lit2', '#Lit3',
        '#Virus'
    ]
    learned_black = [
        (32, '#Psych'),
        (35, '#Drain'),
        (42, '#Quake'),
        (55, '#Nuke'),
        (60, '#Meteo'),
    ]
    learned_text = '\n        '.join(f'{level} {spell}' for level, spell in learned_black)
    env.add_scripts(
        'spellset(#FusoyaWhite) { initial { } }',
        'spellset(#FusoyaBlack) { initial { ' + ' '.join(initial_black) + ' }\n'
        '    learned {\n        ' + learned_text + '\n    }\n}'
    )

    # Level 30 Golbez stats + growth table.
    env.add_binary(UnheaderedAddress(0x7AA80), _build_stats_record(), as_script=True)
    env.add_binary(UnheaderedAddress(0x7C400), _build_levelup_table(), as_script=True)
    env.add_binary(UnheaderedAddress(0x7B524), [0x6F, 0xC3], as_script=True)

    # Abyss Sword, stored in the dummy custom-weapon item slot 0x46.
    env.add_script('text(item name $46) {[sword]Abyss}')
    env.add_binary(UnheaderedAddress(0x79100 + 0x46 * 0x08),
        [0x80, 200, 99, 0x00, 0x3B, 0x00, 0x10, 0x00], as_script=True)
    env.add_binary(UnheaderedAddress(0x79070 + 0x46), [0x00], as_script=True)
    env.add_binary(UnheaderedAddress(0x7D4E0 + 0x46), [0x00], as_script=True)
    env.add_binary(UnheaderedAddress(0x79E10 + 0x46 * 0x04),
        [0x1F, 0x04, 0x00, 0x01], as_script=True)
    # Custom weapon equip table index 0x10: bit 13 = golbez
    env.add_binary(UnheaderedAddress(0x7A550 + 0x10 * 0x02), [0x00, 0x20], as_script=True)
    # No elements
    env.add_binary(UnheaderedAddress(0x7A590 + 0x3B * 0x03), [0x00, 0x00, 0x00], as_script=True)
