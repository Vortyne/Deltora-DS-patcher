"""Story and place scripts: the ending, the Tower's rest rooms, the sound test, signs.

Part of the controls namespace (see __init__.py): names from every part are shared."""

TOWER_OPEN, TOWER_OPEN_ROOM = 0x02214478, 0x28    # after SAVE_WAIT: is the Tower of Illusion open
SOUND_FADE, SOUND_RELEASE = 0x02038B8C, 0x02038C14


def patch_debug_combos(script):
    """Disable the debug stage's R and L button cheats, which clash with the controls."""
    b = bytes(script)
    for mod, kind, key in ((256, 0x4000, 16), (256, 0x4000, 32), (256, 0x4000, 64),
                           (512, 0x4000, 1), (512, 0x4000, 2),
                           (512, 0x4001, 1024), (512, 0x4001, 2048)):
        old = struct.pack("<4H", 0x4001, mod, kind, key)
        assert b.count(old) == 1, key
        # bit 14 is never set in the pad state, so the combo can't match
        b = b.replace(old, struct.pack("<4H", 0x4001, 0x4000, kind, key))
    return b


ENDING_RESTART_MSG, ENDING_TOWER_MSG = 75, 76     # new messages in bank 2178 (the credits' bank, current here)
ENDING_TOWER_SE = 130           # the chime when the farmer hands over a crop
ENDING_CLEAR_AT, ENDING_FIN_AT = 770, 800        # ending StartScript: global byte 0 = 1 (before SavePoint(100)); the return after Fin
ENDING_THE_END_AT = 219         # Fin: MessageC(26, 165, 0, ...) "The End", its handle dropped
ENDING_END_VAR = (0x600A, 0x1F) # global int 31 (the belt puzzle's scratch): The End's message, to take down for the prompt


def patch_ending(script):
    """The ending, script 1798. After the credits it sets global byte 0 (the game cleared, which
    script 2608 reads at the start) and saves, then Fin shows Emily Rodda's note and the script
    ended there, leaving the note up for good.
    TowerNote takes the place of that byte's setting: the first time the game is cleared (the byte
    still 0), the black screen says the Tower of Illusion is open (it opened after Fallow), with a
    chime, until A or a touch; then the byte is set as before.
    RestartAsk takes the place of the return after Fin: A or a touch asks "Go back to title screen?" (the
    camp's Save prompt, but from the current bank: with no box shown, IsMessageYes answered yes);
    Yes resets the console (CallProgram(99), OS_ResetSystem), No waits again."""
    b = bytearray(script)
    funcs, imports = scr.recs(b)
    main = scr.rec(b, funcs[0])
    assert main["name"] == "StartScript" and main["n"] == 803
    clear = main["code"] + ENDING_CLEAR_AT * 2
    assert struct.unpack_from("<6H", b, clear) == (0x6008, 0, 0x4000, 1, 0x14, 0xA000)
    fin = main["code"] + ENDING_FIN_AT * 2
    assert struct.unpack_from("<3H", b, fin) == (0x4000, 0, 0x108)
    camp = open("work/lf2/02595.bin", "rb").read()
    cf, ci = scr.recs(camp)
    save = next(r for r in (scr.rec(camp, o) for o in cf if o) if r["name"] == "Save")
    ask = list(struct.unpack_from("<31H", camp, save["code"] + 4 * 2))
    cnames = [scr.rec(camp, o)["name"] for o in ci]
    assert ask[:2] == [0x4001, 188] and ask[-4:] == [0x2102, cnames.index("MessageWaitC"), 0x2102, cnames.index("IsMessageYes")]
    fin_f = scr.rec(b, funcs[3])
    assert fin_f["name"] == "Fin"
    the_end_at = fin_f["code"] + ENDING_THE_END_AT * 2
    the_end = struct.unpack_from("<21H", b, the_end_at)
    assert the_end[:4] == (0x4000, 26, 0x4001, 165) and the_end[-3:-1] == (0x2102, [scr.rec(b, o)["name"] for o in imports].index("MessageC")) and the_end[-1] == 0xA000
    ix = script_add(b, imports=(("GetTouchTrg", 1), ("GetPadData", 1), ("WaitVsync", 1), ("PlaySe", 2),
                                ("MessageWait", 2), ("MessageWaitC", 3), ("IsMessageYes", 1), ("CallProgram", 5),
                                ("DeleteMessage", 1)))
    ask[:2] = imm(ENDING_RESTART_MSG)
    assert ask[2:8] == [0x4003, 0, 0x8000, 0, 0, 0x11]     # | 0x80000000: from the second (system) message
    ask[4] = 0                                              # bank, not loaded here: so from the current, 2178
    ask[-3], ask[-1] = ix["MessageWaitC"], ix["IsMessageYes"]
    tower = (0x6008, 0, 0x4000, 0, 0x0D,                    # 0: global byte 0 == 0 (not cleared before)
             0x101, 0x4001, 20, 0x103,                     # 5: no: to 26 (a jump counts from its push)
             0x4000, 0, *imm(ENDING_TOWER_SE), 0x2102, ix["PlaySe"], 0xA000,                # 9: the chime
             *imm(ENDING_TOWER_MSG), 0x4000, 1, 0x4000, 1, 0x20, 0x2102, ix["MessageWait"], 0xA000,   # 16
             0x6008, 0, 0x4000, 1, 0x14, 0xA000,           # 26: as it was: the byte set
             0x4000, 0, 0x108)
    assert tower[26:28] == (0x6008, 0) and tower[6] == 0x4001 and tower[6 + 20] == 0x6008
    show_end = (*ENDING_END_VAR, *the_end[:-1], 0x14, 0xA000, 0x4000, 0, 0x108)   # global 31 = MessageC(26, ...)
    ix.update(script_add(b, funcs=(("TowerNote", 0, tower), ("TheEnd", 0, show_end))))
    restart = (0x4000, 0, 0x2102, ix["GetTouchTrg"],       # 0: a new touch
               0x4000, 1, 0x2102, ix["GetPadData"], 0x4000, 1, 0x0F,   # 4: or A newly pressed
               0x11,
               0x101, 0x4001, 70, 0x103,                   # 12: neither: to 83, a frame
               0x4000, 2, 0x2102, ix["WaitVsync"], 0xA000,  # 16: 2 frames: the press that asks mustn't answer
               *ENDING_END_VAR, 0x2102, ix["DeleteMessage"], 0xA000,   # 21: The End taken down
               *ask,                                       # 26: "Go back to title screen?" Yes / No
               0x101, 0x4001, 19, 0x103,                   # 57: No: to 77
               0x4000, 99, 0x4000, 0, 0x4000, 0, 0x4000, 0, 0x4000, 0, 0x2102, ix["CallProgram"], 0xA000,   # 61: reset
               0x4001, -74 & 0xFFFF, 0x103,                # 74
               0x2002, ix["TheEnd"], 0xA000,               # 77: No: The End again
               0x4001, -80 & 0xFFFF, 0x103,                # 80: to 0
               0x4000, 1, 0x2102, ix["WaitVsync"], 0xA000,  # 83: a frame
               0x4001, -88 & 0xFFFF, 0x103)                # 88: to 0
    assert len(ask) == 31 and restart[57] == 0x101 and restart[61:63] == (0x4000, 99) and restart[83:85] == (0x4000, 1)
    assert restart[13 + 70] == 0x4000 and restart[58 + 19] == 0x2002 and restart[16:18] == (0x4000, 2) and restart[21] == 0x600A
    assert restart[74] == restart[80] == restart[88] == 0x4001 and len(restart) == 91
    ix.update(script_add(b, funcs=(("RestartAsk", 0, restart),)))
    struct.pack_into("<6H", b, clear, 0x2002, ix["TowerNote"], 0xA000, 0x4000, 0, 0xA000)
    struct.pack_into("<3H", b, fin, 0x2002, ix["RestartAsk"], 0xA000)
    struct.pack_into("<21H", b, the_end_at, 0x2002, ix["TheEnd"], 0xA000, *[0x4000, 0, 0xA000] * 6)   # Fin: The End, kept
    return bytes(b)


TOWER_CAMP = 43                 # the Tower of Illusion's rest rooms: camp ids 43-45 were unused ("Save Data 43")
TOWER_LOADED = (0x6008, 20)     # global byte 20 (unused): a file was loaded at a rest room
TOWER_FLOOR = (0x600A, 21)      # global int 21: the floor (10, 20, ... 90, 99 in a rest room)
TOWER_REST_AREA = 16            # every rest room is area 16 of its stage, entered at (16, 19) facing 4
TOWER_STAGES = ((21, 3), (41, 5), (61, 4))     # floor below: stage; else 6 (as the floor exits warp)
TOWER_FLOOR_AT = FILE_SAVE + 0x1BEC + 21 * 4    # the title's file: its save image, global ints at +0x1BEC


def patch_tower_fire(script):
    """The rest rooms' campfire, script 2375: CallCamp(0, 3), camp 0 (no save point) and type 3
    (no Save). It now names TOWER_CAMP, so the camp's Save saves there (patch_camp lets type 3 save)."""
    b = bytearray(script)
    funcs, _ = scr.recs(b)
    touch = scr.rec(b, funcs[3])
    assert touch["name"] == "Mob_Touch"
    at = touch["code"] + 99 * 2
    assert struct.unpack_from("<4H", b, at) == (0x4000, 0, 0x4000, 3)
    struct.pack_into("<H", b, at + 2, TOWER_CAMP)
    return bytes(b)


def patch_tower_load(script):
    """Loading a file, script 2608: StartScript(camp) warps to the camp's stage. Camp TOWER_CAMP
    goes to the rest room of the saved floor; the old StartScript (now LoadBase) still runs first
    for its set-up (no camp matches, so it only resets, loads sounds and fades in)."""
    b = bytearray(script)
    funcs, imports = scr.recs(b)
    main = scr.rec(b, funcs[0])
    assert main["name"] == "StartScript" and len(main["types"]) == 2
    b[main["off"] + 0x20:main["off"] + 0x30] = b"LoadBase".ljust(16, b"\0")
    ix = script_add(b, imports=(("StageSet2", 7),))
    stage = (0x601A, 2)
    code = [0x109, 2, 2, 0xA000,                                # 0: local 2, the stage
            0x601A, 0, *imm(TOWER_CAMP), 0x0D,                  # 4: camp == TOWER_CAMP
            0x101, 0x4001, None, 0x103,                         # 9: other camps: to the old start
            0x601A, 0, 0x601A, 1, 0x2002, 0, 0xA000,            # 13: LoadBase(camp, ...): set-up only
            *TOWER_LOADED, 0x4000, 1, 0x14, 0xA000,             # the rest room skips its fight
            0x6008, 11, *imm(TOWER_REST_AREA), 0x14, 0xA000,    # global byte 11 = 16, as the floors' warp sets
            *stage, 0x4000, 6, 0x14, 0xA000]
    for below, s in reversed(TOWER_STAGES):                     # 61: 4, 41: 5, 21: 3, the last that holds
        code += [*TOWER_FLOOR, *imm(below), 0x09, 0x101, 0x4001, 9, 0x103, *stage, 0x4000, s, 0x14, 0xA000]
    code += [*imm(9), *stage, *imm(TOWER_REST_AREA), *imm(16), *imm(19), *imm(4), *imm(0),
             0x2102, ix["StageSet2"], 0xA000, 0x4000, 0, 0x108]
    code[11] = len(code) - 10                                   # a jump counts from its push (10)
    code += [0x601A, 0, 0x601A, 1, 0x2002, 0, 0x108]            # the old start
    assert code[10] == 0x4001 and code[10 + code[11]] == 0x601A and code[12] == 0x103
    script_add(b, funcs=(("StartScript", 2, tuple(code)),))
    return bytes(b)


def patch_tower_rest(script):
    """A rest room, script 2613: StartScript spawns the floor's boss, waits for it, gives its card
    and chest, then puts out the exit and campfire (ExitSet). After loading a file saved here
    (TOWER_LOADED), it fades in to the exit and campfire only; the old StartScript is StartBase."""
    b = bytearray(script)
    funcs, _ = scr.recs(b)
    main = scr.rec(b, funcs[0])
    assert main["name"] == "StartScript" and len(main["types"]) == 2
    assert scr.rec(b, funcs[4])["name"] == "ExitSet"
    b[main["off"] + 0x20:main["off"] + 0x30] = b"StartBase".ljust(16, b"\0")
    ix = script_add(b, imports=(("FadeInT", 2), ("FadeIn", 2), ("PlayBGM", 3), ("KeyOn", 1)))
    code = (*TOWER_LOADED, 0x4000, 0, 0x0D,                     # 0: not loaded here
            0x101, 0x4001, 10, 0x103,                           # 5: loaded: to 16
            0x601A, 0, 0x601A, 1, 0x2002, 0, 0x108,             # 9: the old start
            *TOWER_LOADED, 0x4000, 0, 0x14, 0xA000,
            0x4000, 43, *imm(127), 0x4000, 0, 0x2102, ix["PlayBGM"], 0xA000,     # the tower's music
            0x4000, 1, 0x4000, 30, 0x2102, ix["FadeInT"], 0xA000,
            0x4000, 0, 0x4000, 30, 0x2102, ix["FadeIn"], 0xA000,
            0x4000, 0, 0x2102, ix["KeyOn"], 0xA000,
            0x4000, 0, 0x2002, 4, 0xA000,                       # ExitSet: the exit and campfire
            0x4000, 0, 0x108)
    assert code[6 + 10] == TOWER_LOADED[0] and code[9:11] == (0x601A, 0)
    script_add(b, funcs=(("StartScript", 2, code),))
    return bytes(b)


# Sound test buttons (script 2618's SoundMode hit boxes): held key bit -> the spot it touches
SOUND_KEYS = ((0x20, 93, 96),      # Left: back a track
              (0x01, 122, 104),    # A: play
              (0x10, 153, 113),    # Right: forward a track
              (0x02, 240, 176))    # B: the exit in the corner
SOUND_NOW_MSG = 335                 # bank 2197 (the system bank, | 0x80000000): "Currently playing:\nBGM n"
SOUND_NOW_Y = 4
SOUND_NOW_FLAGS = 0x84101           # as the sound test's own track number (no panel, no wait), but 1: the top
                                    # screen (its number, without 1, is on the touch screen), and 0x4000: each
                                    # line right-aligned to x 255 (entext's measure, mode 0)
SOUND_NOW_VAR = (0x600A, 23)        # global int 23, which no script uses: the message's handle


def patch_sound_test(script):
    """The secret sound test, script 2618: SoundMode reads GetTpTouch(0) (held), (1) x and (2) y each
    frame, and acts when the button under the touch changes. Those three calls go to PadTouch, which
    passes a real touch through, and otherwise answers with a button's spot while its key is held, so
    the buttons light up and act once per press, as with the stylus."""
    b = bytearray(script)
    funcs, imports = scr.recs(b)
    mode = scr.rec(b, funcs[1])
    assert mode["name"] == "SoundMode"
    ix = script_add(b, imports=(("GetTpTouch", 1), ("GetPadData", 1)))
    tp = ix["GetTpTouch"]
    sites = [i for i in range(mode["n"] - 3)
             if struct.unpack_from("<4H", b, mode["code"] + i * 2) in [(0x4000, n, 0x2102, tp) for n in range(3)]]
    assert len(sites) == 3, sites
    bit = lambda k: (0x601A, 1, *imm(k), 0x06, 0x601A, 1, *imm(2 * k), 0x06, 0x4000, 2, 0x05, 0x08)  # (keys / k) - (keys / 2k) * 2
    code = [0x109, 2, 1, 0xA000,                           # 0: local 1
            0x4000, 0, 0x2102, tp, 0x4000, 0, 0x0E,        # 4: touching
            0x101, 0x4001, 8, 0x103,                       # 11: no: to 20 (a jump counts from its push)
            0x601A, 0, 0x2102, tp, 0x108,                  # 15: GetTpTouch(n)
            0x601A, 1, 0x4000, 0, 0x2102, ix["GetPadData"], 0x14, 0xA000]   # 20: local 1 = keys held
    assert code[12 + code[13]:12 + code[13] + 2] == [0x601A, 1]
    for k, x, y in SOUND_KEYS:
        test = bit(k)
        value = (0x601A, 0, 0x4000, 0, 0x0D,                           # n == 0: 1
                 0x601A, 0, 0x4000, 1, 0x0D, *imm(x), 0x05, 0x07,      # n == 1: x
                 0x601A, 0, 0x4000, 2, 0x0D, *imm(y), 0x05, 0x07,      # n == 2: y
                 0x108)
        code += [*test, 0x101, 0x4001, 3 + len(value), 0x103, *value]  # not held: on to the next key
    code += [0x4000, 0, 0x108]
    ix.update(script_add(b, funcs=(("PadTouch", 1, tuple(code)),)))
    for i in sites:
        struct.pack_into("<H", b, mode["code"] + i * 2 + 4, 0x2002)
        struct.pack_into("<H", b, mode["code"] + i * 2 + 6, ix["PadTouch"])

    # "Currently playing: / BGM n" at the top right of the top screen once a track is played
    names = [scr.rec(b, o)["name"] for o in funcs]
    start, bgm_start, bgm_clear = (names.index(n) for n in ("StartScript", "BgmStart", "BgmClear"))
    ix.update(script_add(b, imports=(("MessageIC", 4), ("DeleteMessage", 1))))
    handle = SOUND_NOW_VAR
    drop = (*handle, 0x4000, 0, 0x0E, 0x101, 0x4001, 8, 0x103,     # 0: shown: taken down (to 14 if not)
            *handle, 0x2102, ix["DeleteMessage"], 0xA000)
    assert drop[6] == 0x4001 and 6 + drop[7] == len(drop)
    now = (0x601A, 0, 0x2002, bgm_start, 0xA000) + drop + (           # the track starts, as before
           *handle, 0x4003, SOUND_NOW_MSG, 0x8000, 0, 0, 0x601A, 0, *imm(SOUND_NOW_Y),    # 0x4003: 64 bits
           0x4003, SOUND_NOW_FLAGS & 0xFFFF, SOUND_NOW_FLAGS >> 16, 0, 0, 0x2102, ix["MessageIC"], 0x14, 0xA000,
           0x4000, 0, 0x108)
    clear = (0x601A, 0, 0x2002, bgm_clear, 0xA000) + drop + (*handle, 0x4000, 0, 0x14, 0xA000, 0x4000, 0, 0x108)
    enter = (*handle, 0x4000, 0, 0x14, 0xA000, 0x601A, 0, 0x2002, names.index("SoundMode"), 0x108)
    ix.update(script_add(b, funcs=(("NowPlaying", 1, now), ("NowClear", 1, clear), ("SoundModeNow", 1, enter))))
    for f, call, new in ((start, (0x4000, 0, 0x2002, names.index("SoundMode"), 0xA000), "SoundModeNow"),
                         (start, (0x4000, 0, 0x2002, bgm_clear, 0xA000), "NowClear"),
                         (names.index("SoundMode"), (0x601A, 4, 0x2002, bgm_start, 0xA000), "NowPlaying")):
        r = scr.rec(b, funcs[f])
        at = [i for i in range(r["n"] - 4) if struct.unpack_from("<5H", b, r["code"] + i * 2) == call]
        assert len(at) == 1, (new, at)
        struct.pack_into("<H", b, r["code"] + at[0] * 2 + 6, ix[new])
    return bytes(b)


def patch_mix_sign(script):
    """Jasmine's mixing room, script 2606: once the game is cleared (global byte 0, set by the
    ending), a signpost lists the gear mixes that no recipe item gives. The old StartScript is
    StartBase; the new one puts the sign up first, so it's there when the room fades in."""
    b = bytearray(script)
    funcs, _ = scr.recs(b)
    main = scr.rec(b, funcs[0])
    assert main["name"] == "StartScript" and len(main["types"]) == 2
    b[main["off"] + 0x20:main["off"] + 0x30] = b"StartBase".ljust(16, b"\0")
    ix = script_add(b, imports=(("SpawnObj", 7), ("MessageWait", 2), ("RangeButtonEvent", 7),
                                ("PlaySe", 2), ("KeyOff", 1), ("KeyOn", 1)), strings=("TouchKanban",))
    zone = (0x4005, ix["TouchKanban"], *imm(0), *imm(0), *imm(MIX_SIGN_X), *imm(MIX_SIGN_Y - 14),
            *imm(MIX_SIGN_ZONE), *imm(64), 0x2102, ix["RangeButtonEvent"], 0xA000)
    spawn = (*imm(0), *imm(0), *imm(SIGN_OBJ), *imm(0), *imm(MIX_SIGN_X), *imm(MIX_SIGN_Y), *imm(0),
             0x2102, ix["SpawnObj"], 0xA000)
    code = (0x6008, 0, 0x4000, 0, 0x0E,                     # 0: cleared
            0x101, 0x4001, 3 + len(spawn + zone), 0x103) + spawn + zone + (   # 5: no: to the old start
            0x601A, 0, 0x601A, 1, 0x2002, 0, 0x108)
    assert code[6 + code[7]:6 + code[7] + 2] == (0x601A, 0) and code[-3:-1] == (0x2002, 0)
    touch = (0x4000, 0, *imm(103), 0x2102, ix["PlaySe"], 0xA000,
             0x4000, 0, 0x2102, ix["KeyOff"], 0xA000,
             *imm(MIX_SIGN_MSG), 0x4000, 1, 0x4000, 1, 0x20, 0x2102, ix["MessageWait"], 0xA000) + zone + (
             0x4000, 0, 0x2102, ix["KeyOn"], 0xA000, 0x4000, 0, 0x108)
    script_add(b, funcs=(("StartScript", 2, code), ("TouchKanban", 2, touch)))
    return bytes(b)
