"""The options page, the title menu, logos and the save screen.

Part of the controls namespace (see __init__.py): names from every part are shared."""

TITLE_CODE, TITLE_ROOM = 0x022128B0, 252    # SetMapGimmickSub, GetMapPosType, unused
DELETE_ASK, DELETE_ASK_ROOM = 0x02212CC0, 28
DELETE_SITE, TEXT_PLACE = 0x0206BB90, 0x02033C28    # the save screen's first delete question
SAVE_WAIT, SAVE_WAIT_ROOM = 0x02214440, 0x38      # "Save complete" waits for a press, not 90 frames
SAVE_WRITE_AT = 0x020364F0      # the save thread's bls after cmp r8, #0x3c: its 60 frames of "Saving...", then the write
SAVE_WRITE_SKIP = 0x02036600    # that bls's target: the thread's next frame
SAVE_TASK, SAVE_OF = 0x021D4A44, 0x0203A9E0            # how the card book finds it
SAVE_SHOWN_AT, SAVE_TAIL_AT = 0x02046C1C, 0x02046D90   # sb_SavePoint: the message's frame loop, the last 15 frames
OPT_TEXT = 0x022142E0            # the options page's six text slots, after its code
SAVE_BACK, SAVE_BACK_ROOM = 0x02212EA0, 140
SAVE_LEAVE = -2               # BuckupDataLoad's result for B on the save file screen
TITLE_DATA = 0x02212F48        # the two title buttons, then the one shown as selected
TITLE_GLOW, TITLE_GLOW_ROOM = 0x02212F58, 200
OPT_DATA = 0x02213020          # options, also at save offset 0x1F20: skip logos, biorhythm cue, music
OPT_VARS = 0x02213030          # gear made, options open, line chosen, info box, gear active
OPT_GEAR = 0x02213058          # the gear button's sprite object, 0x44 bytes
OPT_CODE, OPT_ROOM = 0x022130A0, 0x1240
OPT_SAVE_AT, OPT_SIZE = 0x1F20, 16     # never touched by the game's own saves
OPT_COUNTS = (2, 3, 2, 2, 2)
OPT_LOGOS, OPT_CUE, OPT_ALERT, OPT_BAG, OPT_MUSIC = range(5)      # their bytes in OPT_DATA, in the page's order
OPT_NAMES = ("Skip Logos", "Biorhythm Cue", "Low Health Alert", "Bag Icon", "Music")
OPT_VALUES = (("Off", "On"), ("On", "Battle Only", "Off"), ("On", "Off"), ("Show", "Hide"), ("On", "Off"))
OPT_INFO_BANK = 2198            # its three test messages, unused, hold each setting's info
OPT_GEAR_X, OPT_GEAR_Y = 208, 180       # left of the back button (244, 180)
OPT_TAP_AT = 12                 # OPT_DATA+12: a tap wanted next frame, for an info box page (talk boxes only read taps)
OPT_DIRTY_AT = 13               # OPT_DATA+13: settings changed, saved when the bag closes
OPT_BANK_KEPT = 14              # OPT_DATA+14: the message bank to restore after an info box
OPT_HELP = "Ⓧ: Info"
OPT_HELP_AT = 44, 148            # its centre x and top y: the board's bottom left
LOGO_MARK = 0x4C47             # GetTpTouch's argument when the title script asks about the logos
# The game's boot save check (its header read, then the backup unlock at 0x02035874) is left as it
# is: reading the settings inside it made nds-bootstrap (TWiLight Menu++) hang after the logos.
OPT_DRAW_SITE = 0x02066268     # the bag icons' draw, before the board
OPT_FREE_SITE = 0x020661F8     # the bag icons' free, before the board
TITLE_PAGE = 0x0206AFA0       # the title object's page setter
SAVE_HERO_SITE = 0x020905A8     # the save storing who is being played
SAVE_CODE, SAVE_ROOM = 0x0221182C, 220      # CheckUseBagItem and friends, unused
SAVE_PAGE = 0x0206B734
SAVE_SITE = 0x0206C310
SAVE_DOOR, SAVE_TRASH, SAVE_Y = 0x8C, 0xF0, 0xB2


def delete_ask_src(var):
    return f"""
    ldr r12, ={var:#x}
    ldr r3, [r12, #{SAVE_SEL}]
    orr r3, r3, #4
    str r3, [r12, #{SAVE_SEL}]
    b {TEXT_PLACE:#x}

.ltorg
"""


def save_back_src():
    return f"""
    b back_title
    b back_sound
    tst r6, #2
    bne back_title
    tst r6, #9              @ A or Start press the button through the page's own fields
    bxeq lr
    strh r7, [r4, #0x4C]
    mov r0, #{SAVE_Y}
    strh r0, [r4, #0x4E]
    mov r0, #1
    str r0, [r4, #0x44]
    bx lr

back_sound:                 @ the cursor sound between door and trash
    ldr r0, ={SOUND:#x}
    mov r1, #0
    mov r2, #0x67
    b {PLAY_SE:#x}

back_title:                 @ B on the save file screen: back to the title menu
    mov r0, #0
    str r0, [r4, #0x44]     @ B also tapped the corner, which is the trash
    ldr r0, [r4, #0x6C]
    cmp r0, #0
    beq back_freed
    bl {MESSAGE_FREE:#x}
    mov r0, #0
    str r0, [r4, #0x6C]
back_freed:
    mvn r0, #{-SAVE_LEAVE - 1}
    str r0, [r4, #0x24]
    mov r0, r4
    mov r1, #9              @ the page that closes the screen
    bl {TITLE_PAGE:#x}
    bl {KILL:#x}
    pop {{r4, r5, r6, r7, pc}}

.ltorg
"""


def patch_title(script):
    """Title, script 1797: B on the save file screen returns to the title menu.
    StartGame returns 1 when BuckupDataLoad gives SAVE_LEAVE, and StartScript then loops
    back to the title instead of ending. StartGame's new steps go after the file's end."""
    b = bytearray(script)
    funcs, _ = scr.recs(b)
    main, start = scr.rec(b, funcs[0]), scr.rec(b, funcs[3])
    assert (main["name"], start["name"]) == ("StartScript", "StartGame")
    words = lambda r, i, n: list(struct.unpack_from(f"<{n}H", b, r["code"] + i * 2))
    # StartScript: call StartGame, drop its result, return 0 -> return 0 only if it gave 0
    assert words(main, 192, 6) == [0x2002, 3, 0xA000, 0x4000, 0, 0x108]
    assert words(main, 198, 2) == [0x4001, 35] and words(main, 236, 3) == [0x4000, 0, 0x108]
    struct.pack_into("<4H", b, main["code"] + 194 * 2, 0x101, 0x4001, 236 - 195, 0x103)
    # StartGame: after var 1 = BuckupDataLoad(0), leave with 1 on SAVE_LEAVE
    old = words(start, 12, 9)
    assert old == [0x4000, 0, 0x2102, 5, 0x4000, 1, 0x2102, 7, 0xA000]
    if len(b) % 2:
        b.append(0)
    at = (len(b) - start["code"]) // 2
    struct.pack_into("<3H", b, start["code"] + 12 * 2, 0x4001, at - 12, 0x103)
    steps = [0x601A, 1, 0x4001, SAVE_LEAVE & 0xFFFF, 0xD, 0x101, 0x4001, 6, 0x103,
             0x4000, 1, 0x108] + old
    steps += [0x4001, (21 - (at + len(steps))) & 0xFFFF, 0x103]
    b += struct.pack(f"<{len(steps)}H", *steps)
    struct.pack_into("<I", b, start["off"] + 16, (len(b) - start["code"]) // 2)
    # StartScript: the logos (Credit) play unless the Skip Logos option is on; the movie stays
    assert words(main, 123, 7) == [0x601A, 0, 0x3, 0x101, 0x4001, 23, 0x103]
    assert words(main, 130, 4) == [0x4000, 0, 0x2002, 1] and words(main, 134, 3) == [0xA000, 0x4000, 0]
    at = (len(b) - main["code"]) // 2
    struct.pack_into("<3H", b, main["code"] + 123 * 2, 0x4001, at - 123, 0x103)
    ask = [0x4001, LOGO_MARK, 0x2102, 0x30, 0x101, 0x4001, (135 - (at + 5)) & 0xFFFF, 0x103,
           0x4001, (130 - (at + 8)) & 0xFFFF, 0x103]       # GetTpTouch(LOGO_MARK): play them?
    b += struct.pack(f"<{len(ask)}H", *ask)
    struct.pack_into("<I", b, main["off"] + 16, (len(b) - main["code"]) // 2)
    return bytes(b)


TITLE_BANK = 2199               # the title's text, which StartScript loads only once
TITLE_VERSION_MSG = 139         # bank 2199 (the title's), added: "English patch v<version_number.txt>"
TITLE_VERSION_Y = 179           # the touch screen's last line, 3 px lower
TITLE_VERSION_FLAGS = 0x82100   # the touch screen, left-aligned, no panel, no wait
TITLE_VERSION_VAR = (0x600A, 14)    # global int 14, which no script uses: the message's handle


def title_version_text(version):
    return f" English patch v{version}"     # the space: a little room from the screen's edge


TITLE_PRESSED_AT = 355         # Title: the DeleteMessage of "Press Any Button", once a button is pressed


def patch_title_version(script):
    """Title, script 1797, after patch_title: the patch's version at the bottom left of the touch
    screen, from the press of a button at "Press Any Button" until the title ends. That message's
    DeleteMessage (TITLE_PRESSED_AT) now calls PressGone, which takes it down and puts the version
    line up. Title is now TitleBase; the new Title loads the title's bank (2199) first, runs it,
    and takes the line down before returning its result. Back from the file screen (B), the file
    screen's bank was still loaded, so the title's lines came from the wrong bank and the version
    line's number, past that bank's end, crashed."""
    b = bytearray(script)
    funcs, _ = scr.recs(b)
    names = [scr.rec(b, o)["name"] for o in funcs]
    title = names.index("Title")
    b[funcs[title] + 0x20:funcs[title] + 0x30] = b"TitleBase".ljust(16, b"\0")
    ix = script_add(b, imports=(("MessageC", 3), ("DeleteMessage", 1), ("SetMessageFile", 1)))
    f = TITLE_VERSION_FLAGS
    gone = (0x601A, 0, 0x2102, ix["DeleteMessage"], 0xA000,             # "Press Any Button" down
            *TITLE_VERSION_VAR, *imm(TITLE_VERSION_MSG), *imm(TITLE_VERSION_Y),
            0x4003, f & 0xFFFF, f >> 16, 0, 0, 0x2102, ix["MessageC"], 0x14, 0xA000,
            0x4000, 0, 0x108)
    code = (0x109, 2, 1, 0xA000,                                            # local 1: Title's result
            *imm(TITLE_BANK), 0x2102, ix["SetMessageFile"], 0xA000,          # the title's own text
            *TITLE_VERSION_VAR, 0x4000, 0, 0x14, 0xA000,                     # no line yet
            0x601A, 1, 0x601A, 0, 0x2002, title, 0x14, 0xA000,
            *TITLE_VERSION_VAR, 0x4000, 0, 0x0E, 0x101, 0x4001, 8, 0x103,    # shown: taken down
            *TITLE_VERSION_VAR, 0x2102, ix["DeleteMessage"], 0xA000,
            0x601A, 1, 0x108)
    assert code[29] == 0x4001 and code[29 + code[30]:29 + code[30] + 2] == (0x601A, 1)
    ix.update(script_add(b, funcs=(("PressGone", 1, gone), ("Title", 1, code))))
    funcs, _ = scr.recs(b)
    base = scr.rec(b, funcs[title])
    at = base["code"] + TITLE_PRESSED_AT * 2
    assert struct.unpack_from("<5H", b, at - 4) == (0x601A, 1, 0x2102, ix["DeleteMessage"], 0xA000)
    struct.pack_into("<2H", b, at, 0x2002, ix["PressGone"])
    n = 0
    for k, o in enumerate(funcs):
        if k in (ix["Title"], ix["PressGone"]):
            continue
        for a, x in scr.walk(b, scr.rec(b, o)):
            if x[0] == "call" and x[1] == 0x2002 and x[2] == title:
                struct.pack_into("<H", b, a + 2, ix["Title"])
                n += 1
    assert n >= 1, n
    return bytes(b)


def leave_quiet_src():
    return f"""
    ldr r12, [r4, #0x24]    @ no walk-away sound when B closed the save file screen
    cmn r12, #{-SAVE_LEAVE}
    moveq r0, #0
    bxeq lr
    b {PLAY_SE:#x}
"""


def title_glow_src(var):
    return f"""
    b glow_spawned
    b glow_begin
    push {{r4, lr}}         @ the selected title button pulses (sequence 2), the other is plain
    ldr r12, ={TITLE_DATA:#x}
    ldr r1, [r9, #{TITLE_SEL}]
    ldr r0, [r12, #8]
    cmp r0, r1
    popeq {{r4, pc}}
    str r1, [r12, #8]
    mov r4, #0
glow_next:
    ldr r3, [r12, r4, lsl #2]
    cmp r3, #0
    beq glow_skip
    cmp r4, r1
    moveq r0, #2
    movne r0, #0
    add r3, r3, #0x200
    str r0, [r3, #0xE8]
    mvn r0, #0
    str r0, [r3, #0xEC]
    mov r0, #0x1000
    str r0, [r3, #0xF0]
glow_skip:
    add r4, r4, #1
    cmp r4, #2
    blt glow_next
    pop {{r4, pc}}

glow_spawned:               @ the title menu's two spawns are its buttons
    ldr r12, ={var:#x}
    ldr r3, [r12, #{TITLE}]
    cmp r3, #0
    beq {SPAWN_DONE:#x}
    ldr r12, ={TITLE_DATA:#x}
    ldr r3, [r12]
    cmp r3, #0
    streq r1, [r12]
    strne r1, [r12, #4]
    b {SPAWN_DONE:#x}

glow_begin:                 @ the title: the sound system is up, so the music option holds
    push {{lr}}
    bl {OPT_CODE + 20:#x}
    pop {{lr}}
    ldr r12, ={TITLE_DATA:#x}
    mov r1, #0
    str r1, [r12]
    str r1, [r12, #4]
    mvn r1, #0
    str r1, [r12, #8]
    b {SB_BACK_INFO:#x}

.ltorg
"""


OPT_WIDTH = 32                  # tokens per line in the tables, 0xFFFD and zeros after the text


def opt_lines():
    """Each setting's line for each value, plain then chosen, then the help line."""
    rows = []
    for name, values in zip(OPT_NAMES, OPT_VALUES):
        for v in range(3):
            text = f"{name}: {values[min(v, len(values) - 1)]}"
            rows += [entext.encode(text), entext.encode("{fff8}" + text + "{fffc}")]
    table = []
    for r in rows + [entext.encode(OPT_HELP)]:
        r = r + [0xFFFD]
        assert len(r) <= OPT_WIDTH, r
        table.append(".short " + ", ".join(f"{x:#x}" for x in r + [0] * (OPT_WIDTH - len(r))))
    return chr(10).join(table[:-1]), table[-1]


def opt_src(var):
    """The options. A gear button left of the bag's back button opens three settings drawn on
    the board; both buttons take the arrow. Settings live in OPT_DATA and in the save's unused
    bytes at OPT_SAVE_AT, written when the bag closes."""
    rows, help_line = opt_lines()
    line_bytes = OPT_WIDTH * 2
    MADE, OPEN, LINE, MSG, ACTIVE, TEXT = 0, 4, 8, 12, 16, 20
    gear_x, back_x, arrow_y = OPT_GEAR_X, 244, OPT_GEAR_Y - 31
    return f"""
    b opt_load
    b opt_draw
    b opt_free
    b opt_nav
    b kill_sound
    b music_apply
    b script_ask
    b bio_cue
    b stream_volume
    b corner_tap
    b page_tap

in_battle:                  @ r0 the player: nonzero in a monster area battle or near a live enemy
    push {{lr}}
    ldr r3, ={AREA_BATTLE:#x}
    ldr r3, [r3]
    cmp r3, #0
    movne r0, #1
    popne {{pc}}
    mov r1, #4
    mov r2, #{BATTLE_RANGE:#x}
    mov r3, #1
    bl {NEAREST:#x}
    cmp r0, #0
    popeq {{pc}}
    ldr r0, [r0, #0xBC]
    cmp r0, #0x1000
    movge r0, #1
    movlt r0, #0
    pop {{pc}}

page_tap:                   @ start of a frame: one tap anywhere, so the info box turns a page
    ldr r1, ={OPT_DATA + OPT_TAP_AT:#x}
    ldrb r0, [r1]
    cmp r0, #0
    bxeq lr
    mov r0, #0
    strb r0, [r1]
    mov r5, #128
    mov r6, #100
    b {ON:#x}               @ the input's own tap: it returns from the input's frame

corner_tap:
    ldr r0, ={OPT_VARS:#x}
    ldr r0, [r0, #{OPEN}]
    cmp r0, #0
    bne {OFF:#x}
    mov r5, #{BAG_X}
    mov r6, #{BAG_Y}
    b {ON:#x}

kill_sound:
    push {{lr}}
    bl {KILL:#x}
    pop {{lr}}
    b cursor_sound

music_apply:                @ music off: the two music players and the four stream slots go silent
    push {{r0, r1, r2, r3, lr}}
    ldr r0, ={OPT_DATA:#x}
    ldrb r0, [r0, #{OPT_MUSIC}]
    cmp r0, #0
    moveq r0, #0x7F
    movne r0, #0
    ldr r1, ={MUSIC_PLAYERS[0]:#x}
    strb r0, [r1]
    ldr r1, ={MUSIC_PLAYERS[1]:#x}
    strb r0, [r1]
    ldr r1, ={STREAM_SLOTS:#x}
    mov r2, #0
stream_next:
    str r0, [r1, #0x158]
    add r1, r1, #0x174
    add r2, r2, #1
    cmp r2, #4
    blt stream_next
    pop {{r0, r1, r2, r3, pc}}

stream_volume:              @ a stream starting: its volume, 0 while music is off
    ldr r1, ={OPT_DATA:#x}
    ldrb r1, [r1, #{OPT_MUSIC}]
    cmp r1, #0
    moveq r1, #0x7F
    movne r1, #0
    str r1, [r4, #0x158]
    bx lr

script_ask:                 @ GetTpTouch with one of our marks: the options and the D-pad answer
    push {{r4, lr}}
    mov r4, r0
    mov r1, #0
    bl {SCRIPT_ARG:#x}
    ldr r1, ={LOGO_MARK:#x}
    cmp r0, r1
    beq ask_logos
    ldr r1, ={HOLE_HELD:#x}
    cmp r0, r1
    beq ask_held
    ldr r1, ={HOLE_X:#x}
    cmp r0, r1
    beq ask_x
    b {CHEST_CODE:#x}       @ the map's chest count, the quiz's marks, or the plain touch read
ask_logos:                  @ 1 when the opening logos should play
    bl opt_load             @ the settings come from the save the first time this is asked
    ldr r1, ={OPT_DATA:#x}
    ldrb r1, [r1, #{OPT_LOGOS}]
    eor r1, r1, #1
    b ask_answer
ask_held:                   @ the Disposal Pit: left or right held counts as the stylus held
    ldr r0, ={PAD:#x}
    ldrh r0, [r0]
    tst r0, #0x30
    movne r1, #1
    bne ask_answer
    bl {TOUCH_HELD:#x}
    mov r1, r0
    b ask_answer
ask_x:                      @ and as a touch at that side of the screen, so Barda heads that way
    ldr r0, ={PAD:#x}
    ldrh r0, [r0]
    tst r0, #0x10
    movne r1, #255
    bne ask_answer
    tst r0, #0x20
    movne r1, #0
    bne ask_answer
    bl {TOUCH_HELD:#x}
    cmp r0, #0
    mvneq r1, #0
    ldrne r1, ={TOUCH_STATE:#x}
    ldrhne r1, [r1, #0x12]
ask_answer:
    mov r0, r4
    bl {SET_RESULT:#x}
    mov r0, #1
    pop {{r4, pc}}

bio_cue:                    @ r0 the player: the biorhythm voice cues, as the option allows
    push {{r0, r1, r2, lr}}
    ldr r3, ={OPT_DATA:#x}
    ldrb r3, [r3, #{OPT_CUE}]
    cmp r3, #1
    blt cue_play
    bgt cue_quiet
    bl in_battle
    cmp r0, #0
    beq cue_quiet
cue_play:
    pop {{r0, r1, r2, lr}}
    b {PLAY_VOICE:#x}
cue_quiet:
    pop {{r0, r1, r2, lr}}
    mov r0, #0
    bx lr

opt_load:                   @ the settings, read when the title asks about the logos (once, at boot)
    push {{r4, lr}}         @ a read of its own, taking and releasing the card as opt_save does
    ldr r0, ={BACKUP_READ:#x}   @ (squeezed into the game's own boot read, it broke nds-bootstrap's)
    bl opt_io               @ no lock to be had: the defaults stay
    ldr r1, ={OPT_DATA:#x}
    ldr r2, =counts
    mov r3, #0
load_next:                  @ unset bytes read 0xFF: anything out of range is the default
    ldrb r0, [r1, r3]
    ldrb r12, [r2, r3]
    cmp r0, r12
    movhs r0, #0
    strb r0, [r1, r3]
    add r3, r3, #1
    cmp r3, #{len(OPT_COUNTS)}
    blt load_next
    bl music_apply
    pop {{r4, pc}}

opt_save:
    ldr r0, ={BACKUP_WRITE:#x}
opt_io:                     @ r0 BACKUP_READ or BACKUP_WRITE: the settings, with the card taken and released
    push {{r4, r5, lr}}
    mov r5, r0
    bl {LOCK_ID:#x}
    mov r4, r0
    cmn r0, #3
    beq io_none
    bl {CARD_LOCK:#x}
    ldr r0, ={OPT_SAVE_AT:#x}
    ldr r1, ={OPT_DATA:#x}
    mov r2, #{OPT_SIZE}
    blx r5
    mov r0, r4
    bl {CARD_UNLOCK:#x}
    mov r0, r4
    bl {LOCK_RELEASE:#x}
io_none:
    pop {{r4, r5, pc}}

opt_draw:                   @ r7 the menu: the gear zooms in with the back button, to its left
    push {{r4, r5, r6, r8, lr}}
    sub sp, sp, #16
    ldr r4, ={OPT_GEAR:#x}
    add r5, r7, #0x1100
    add r5, r5, #0xA4       @ the back button, the fifth sprite
    mov r0, r5
    bl {SPRITE_MADE:#x}
    cmp r0, #0
    beq draw_end
    ldr r6, ={OPT_VARS:#x}
    ldr r0, [r6, #{MADE}]
    cmp r0, #0
    bne draw_ready
    mov r0, r4
    bl {SPRITE_INIT:#x}
    mov r0, #1
    str r0, [r6, #{MADE}]
draw_ready:
    mov r0, r4
    bl {SPRITE_MADE:#x}
    cmp r0, #0
    bne draw_made
    ldr r0, =5311
    ldr r1, =5312
    stm sp, {{r0, r1}}
    mov r0, r4
    mov r1, #1
    ldr r2, =5310
    ldr r3, =5308
    bl {SPRITE_MAKE:#x}
    mov r0, r4
    mov r1, #0
    bl {SPRITE_FLAG:#x}
    mov r0, r4
    mov r1, #6
    bl {SPRITE_ANIM:#x}
    ldr r0, [r6, #{ACTIVE}]
    bl gear_speed
draw_made:
    ldr r0, [r6, #{OPEN}]   @ the options page hides the gear
    cmp r0, #0
    bne draw_end
    ldr r1, [r5, #0x30]     @ the back button's scale and place, as it zooms in or sits still
    ldr r2, [r5, #0x34]
    mov r0, r4
    bl {SPRITE_SCALE:#x}
    mov r0, r5
    mov r1, sp
    bl {SPRITE_GETPOS:#x}
    ldr r1, [sp]            @ it zooms out from x 240 to 244; the gear, from 240 to 208
    ldr r3, ={(240 << 12) * 9:#x}
    sub r1, r3, r1, lsl #3
    ldr r2, [sp, #4]
    mov r0, r4
    bl {SPRITE_POS:#x}
    ldr r1, [sp, #4]
    add r1, r1, #0xC0000
    ldr r0, [r4, #4]
    bl {SPRITE_DEPTH:#x}
    mov r0, r4
    bl {SPRITE_DRAW:#x}
draw_end:
    add sp, sp, #16
    add r0, r7, #0x2BC
    pop {{r4, r5, r6, r8, pc}}

gear_speed:                 @ r0 nonzero: the gear animates, as the selected icon does
    push {{r4, lr}}
    sub sp, sp, #8
    ldr r1, ={OPT_VARS:#x}
    str r0, [r1, #{ACTIVE}]
    movs r2, r0
    movne r2, #0x1000
    ldr r3, [r1, #{MADE}]
    cmp r3, #0
    beq speed_end
    ldr r0, ={OPT_GEAR:#x}
    ldr r0, [r0, #4]
    cmp r0, #0
    beq speed_end
    mov r1, #0
    str r1, [sp]
    mov r1, #6
    bl {SPRITE_SEQ:#x}
speed_end:
    add sp, sp, #8
    pop {{r4, pc}}

opt_free:                   @ r6 the menu: the bag's sprites are going
    push {{r4, lr}}
    ldr r4, ={OPT_VARS:#x}
    ldr r0, [r4, #{MSG}]
    cmp r0, #0
    blne {MESSAGE_FREE:#x}
    mov r0, #0
    str r0, [r4, #{MSG}]
    ldr r1, ={OPT_DATA:#x}
    ldrb r0, [r1, #{OPT_DIRTY_AT}]
    cmp r0, #0
    beq free_saved
    mov r0, #0
    strb r0, [r1, #{OPT_DIRTY_AT}]
    bl opt_save
free_saved:
    ldr r0, [r4, #{MADE}]
    cmp r0, #0
    beq free_text
    ldr r0, ={OPT_GEAR:#x}
    bl {SPRITE_MADE:#x}
    cmp r0, #0
    ldrne r0, ={OPT_GEAR:#x}
    blne {SPRITE_FREE:#x}
free_text:
    bl clear_lines
    mov r0, #0
    str r0, [r4, #{OPEN}]
    add r0, r6, #0x2BC
    pop {{r4, pc}}

opt_nav:                    @ r4 the menu, r5 its selection (5 gear, 6 back); returns 0, 1 or 2
    push {{r4, r5, r6, r7, lr}}
    ldr r6, ={OPT_VARS:#x}
    ldr r0, [r4, #0x10]
    cmp r0, #2
    bne nav_ret0
    ldr r0, [r6, #{OPEN}]
    cmp r0, #0
    bne page
    ldr r0, ={TOUCH:#x}
    bl {TOUCH_TRIG:#x}
    cmp r0, #0
    beq gear_keys
    ldr r0, ={TOUCH:#x}
    ldrh r1, [r0, #0x14]
    ldrh r2, [r0, #0x16]
    sub r1, r1, #{gear_x - 16}
    cmp r1, #32
    bhs gear_keys
    cmp r2, #{OPT_GEAR_Y - 16}
    bhs open
gear_keys:
    ldr r0, ={PAD:#x}
    ldrh r7, [r0, #2]
    ldr r1, [r5]
    cmp r1, #5
    bge bottom
    tst r7, #0x80           @ Down from any icon: the gear
    beq nav_ret0
    mov r0, r1
    mov r2, #0
    bl {ICON_SEQ:#x}
    bl {ICONS_CODE + 4:#x}
    mov r1, #5
    b to_bottom
bottom:
    tst r7, #1
    beq not_press
    cmp r1, #5
    beq open
    ldr r0, ={var:#x}       @ A on back: tap it, as B does
    ldr r1, ={BAG_X | BAG_Y << 8:#x}
    str r1, [r0, #{TAP}]
    b nav_ret1
not_press:
    tst r7, #0x40           @ Up: back to Cards
    movne r1, #3
    bne leave_bottom
    tst r7, #0x10
    movne r1, #6
    tst r7, #0x20
    movne r1, #5
    ldr r0, [r5]
    cmp r0, r1
    beq arrow
to_bottom:
    str r1, [r5]
    subs r0, r1, #6
    movne r0, #1
    bl gear_speed
    bl kill_sound
arrow:
    ldr r1, [r5]
    cmp r1, #5
    mov r0, #{gear_x}
    movne r0, #{back_x}
    mov r1, #{arrow_y}
    bl {DRAW:#x}
    b nav_ret1
leave_bottom:
    str r1, [r5]
    mov r0, #0
    bl gear_speed
    bl kill_sound
    b nav_ret1
open:
    mov r0, #1
    str r0, [r6, #{OPEN}]
    mov r0, #0
    str r0, [r6, #{LINE}]
    ldr r1, [r5]
    cmp r1, #5
    beq open_now
    blt open_icon
    mov r0, #5
    str r0, [r5]
    b open_gear
open_icon:
    mov r0, r1
    mov r2, #0
    bl {ICON_SEQ:#x}
    bl {ICONS_CODE + 4:#x}
    mov r0, #5
    str r0, [r5]
open_gear:
    mov r0, #1
    bl gear_speed
open_now:
    bl {KILL:#x}
    mov r0, #0
    bl icons_shown
    ldr r0, ={SOUND:#x}
    mov r1, #0
    mov r2, #100
    bl {PLAY_SE:#x}
    mov r0, #0
    bl draw_line
    mov r0, #1
    bl draw_line
    mov r0, #2
    bl draw_line
    mov r0, #3
    bl draw_line
    mov r0, #4
    bl draw_line
    bl help_line
    b nav_ret2
page:
    ldr r0, [r6, #{OPEN}]   @ 2: B closed the page last frame, after the buttons' corner tap was held back
    cmp r0, #2
    beq close
    ldr r0, [r6, #{MSG}]    @ an info box: A turns its pages; wait for it to close, then its bank goes back
    cmp r0, #0
    beq page_keys
    ldr r1, ={PAD:#x}
    ldrh r1, [r1, #2]
    tst r1, #1
    ldrne r1, ={OPT_DATA + OPT_TAP_AT:#x}
    movne r2, #1
    strbne r2, [r1]
    bl {MESSAGE_DONE:#x}
    cmp r0, #0
    beq nav_ret2
    mov r0, #0
    str r0, [r6, #{MSG}]
    ldr r0, ={OPT_DATA:#x}
    ldrh r0, [r0, #{OPT_BANK_KEPT}]
    bl {MESSAGE_BANK:#x}
    bl help_line            @ the help comes back with the box gone
    b nav_ret2
page_keys:
    ldr r0, ={TOUCH:#x}     @ the stylus on the back button returns to the bag's icons
    bl {TOUCH_TRIG:#x}
    cmp r0, #0
    beq page_pad
    ldr r0, ={TOUCH:#x}
    ldrh r1, [r0, #0x14]
    ldrh r2, [r0, #0x16]
    cmp r1, #228
    blo page_pad
    cmp r2, #164
    bhs close
page_pad:
    ldr r0, ={PAD:#x}
    ldrh r7, [r0, #2]
    ldr r1, [r6, #{LINE}]
    tst r7, #2
    movne r0, #2
    strne r0, [r6, #{OPEN}]
    bne nav_ret2
    tst r7, #0x40
    beq not_up
    subs r1, r1, #1
    movmi r1, #{len(OPT_COUNTS) - 1}
    b moved
not_up:
    tst r7, #0x80
    beq not_down
    add r1, r1, #1
    cmp r1, #{len(OPT_COUNTS)}
    movge r1, #0
    b moved
not_down:
    tst r7, #0x400          @ X: the setting's info
    bne info
    tst r7, #0x31           @ Right, Left or A change the value
    beq nav_ret2
    ldr r2, ={OPT_DATA:#x}
    ldrb r3, [r2, r1]
    ldr r0, =counts
    ldrb r0, [r0, r1]
    tst r7, #0x20
    subne r3, r3, #1
    addeq r3, r3, #1
    cmp r3, #0
    addlt r3, r3, r0
    cmp r3, r0
    subge r3, r3, r0
    strb r3, [r2, r1]
    mov r0, #1              @ saved when the bag closes: a write here stalls the screen
    ldr r2, ={OPT_DATA:#x}
    strb r0, [r2, #{OPT_DIRTY_AT}]
    bl music_apply
    bl cursor_sound
    ldr r0, [r6, #{LINE}]
    bl draw_line
    b nav_ret2
info:                       @ the talk box, from the debug bank's spare messages, as scripts open it
    bl {MESSAGE_BANK_NOW:#x}
    ldr r1, ={OPT_DATA:#x}
    strh r0, [r1, #{OPT_BANK_KEPT}]
    ldr r0, ={OPT_INFO_BANK:#x}
    bl {MESSAGE_BANK:#x}
    mov r0, #5              @ the help hides while the box is up
    mov r1, #0
    bl put_line
    sub sp, sp, #16
    mov r0, #0
    str r0, [sp]
    mov r0, #1
    str r0, [sp, #4]
    mov r0, #0xA0
    str r0, [sp, #8]
    ldr r0, ={TALK_FLAGS:#x}
    str r0, [sp, #12]
    ldr r0, [r6, #{LINE}]    @ the message number in the current bank, as the smith's notices use
    mov r1, #0
    mvn r2, #0
    mov r3, #0
    bl {MESSAGE_WINDOW:#x}
    add sp, sp, #16
    str r0, [r6, #{MSG}]
    bl cursor_sound
    b nav_ret2
moved:
    ldr r0, [r6, #{LINE}]
    str r1, [r6, #{LINE}]
    bl draw_line
    ldr r0, [r6, #{LINE}]
    bl draw_line
    bl cursor_sound
    b nav_ret2
close:
    bl clear_lines
    mov r0, #0
    str r0, [r6, #{OPEN}]
    mov r0, #1
    bl icons_shown
    bl cursor_sound
nav_ret2:
    mov r0, #2
    pop {{r4, r5, r6, r7, pc}}
nav_ret1:
    mov r0, #1
    pop {{r4, r5, r6, r7, pc}}
nav_ret0:
    mov r0, #0
    pop {{r4, r5, r6, r7, pc}}

cursor_sound:
    ldr r0, ={SOUND:#x}
    mov r1, #0
    mov r2, #0x67
    b {PLAY_SE:#x}

icons_shown:                @ r4 the menu; r0 0 hides the five icons and their labels, 1 shows them
    push {{r4, r5, r6, lr}}
    mov r6, r0
    add r5, r4, #0x1000
    add r5, r5, #0x94
    mov r4, #0
shown_next:
    cmp r4, #4              @ the fifth sprite is the back button
    beq shown_skip
    mov r0, r5
    mov r1, r6
    bl {SPRITE_SHOW:#x}
shown_skip:
    add r5, r5, #0x44
    add r4, r4, #1
    cmp r4, #6
    blt shown_next
    pop {{r4, r5, r6, pc}}

draw_line:                  @ r0 the setting: its line, coloured when it is the chosen one
    push {{r4, lr}}
    mov r4, r0
    ldr r1, ={OPT_DATA:#x}
    ldrb r1, [r1, r4]
    add r1, r1, r4, lsl #1
    add r1, r1, r4          @ setting * 3 + value
    lsl r1, r1, #1
    ldr r2, ={OPT_VARS:#x}
    ldr r2, [r2, #{LINE}]
    cmp r2, r4
    addeq r1, r1, #1
    mov r2, #{line_bytes}
    ldr r3, =rows
    mla r1, r2, r1, r3
    mov r2, #50
    add r2, r2, r4, lsl #4
    add r2, r2, r4, lsl #1  @ 18 apart
    mov r0, r4
    bl put_line
    pop {{r4, pc}}

clear_lines:
    push {{r4, lr}}
    mov r4, #0
clear_next:
    mov r0, r4
    mov r1, #0
    bl put_line
    add r4, r4, #1
    cmp r4, #6
    blt clear_next
    pop {{r4, pc}}

help_line:                  @ bottom left of the board, clear of its carved title
    mov r0, #5
    ldr r1, =help
    mov r2, #{OPT_HELP_AT[1]}
    mov r3, #{OPT_HELP_AT[0]}
    b put_line_at

put_line:                   @ r0 line, r1 tokens (0 clears), r2 top y; centred on x 128
    mov r3, #128
put_line_at:                @ r3 centre x
    push {{r4, r5, r6, r7, r8, lr}}
    mov r8, r3
    sub sp, sp, #16
    mov r5, r0
    mov r6, r1
    mov r7, r2
    ldr r3, ={OPT_TEXT:#x}
    ldr r0, [r3, r5, lsl #2]
    subs r0, r0, #1
    bmi line_fresh
    mov r2, #0
    str r2, [r3, r5, lsl #2]
    ldr r1, ={TEXT_BUFS + 4:#x}  @ free the slot only while it still holds this line's buffer
    ldr r2, [r1, r5, lsl #2]
    ldr r1, ={TEXT_SLOTS:#x}
    ldr r1, [r1, r0, lsl #5]
    cmp r1, r2
    bne line_fresh
    bl {TEXT_FREE:#x}
line_fresh:
    cmp r6, #0
    beq line_end
    bl {FREE_SLOT:#x}
    cmn r0, #1
    beq line_end
    mov r4, r0
    mov r0, #0x80
    bl {ALLOC:#x}
    bl {ARROW_SLOT:#x}
    ldr r3, ={OPT_TEXT:#x}
    add r2, r4, #1
    str r2, [r3, r5, lsl #2]
    ldr r3, ={TEXT_BUFS + 4:#x}
    str r0, [r3, r5, lsl #2]
    cmp r0, #0
    beq line_end
    mov r1, #0xC
    str r1, [sp]
    mov r1, #1
    str r1, [sp, #4]
    mov r1, #0
    str r1, [sp, #8]
    str r6, [sp, #12]
    mov r1, r8
    mov r2, r7
    mov r3, #0
    bl {TEXT_CREATE:#x}
line_end:
    add sp, sp, #16
    pop {{r4, r5, r6, r7, r8, pc}}

.ltorg
counts:
.byte {", ".join(str(c) for c in OPT_COUNTS + (0,) * (-len(OPT_COUNTS) % 4 or 4))}
rows:
{rows}
help:
{help_line}
"""


def save_wait_src():
    return f"""
    ldr r12, ={PAD:#x}      @ r8: the buttons held last frame; starts all set, so a held A is not new
    ldr r1, [r12]
    lsl r1, r1, #20
    bic r0, r1, r8
    mov r8, r1
    ldr r12, ={TOUCH:#x}    @ or a new touch, as TOUCH_TRIG reads it
    ldr r1, [r12, #4]
    cmp r1, #1
    ldreq r1, [r12, #8]
    cmpeq r1, #0
    orreq r0, r0, #1
    bx lr
.ltorg
"""


def title_src(var):
    return f"""
    b title
    b title_on

title:                      @ the title menu, script 1797
    ldr r0, [r9, #{LIVE}]
    mov r1, #0
    str r1, [r9, #{LIVE}]
    cmp r0, #0
    beq {OFF:#x}
    ldr r0, [r9, #{TITLE_N}]
    cmp r0, #2
    bne title_show
    tst r7, #0xC0
    beq title_show
    ldr r0, [r9, #{TITLE_SEL}]
    eor r0, r0, #1
    str r0, [r9, #{TITLE_SEL}]
    bl {SAVE_BACK + 4:#x}    @ the cursor sound
title_show:
    bl {TITLE_GLOW + 8:#x}
title_keys:
    tst r7, #9              @ A or Start
    beq {OFF:#x}
    mov r0, #0
    str r0, [r9, #{TITLE}]
    bl {KILL:#x}
    ldr r1, [r9, #{TITLE_SEL}]
    cmp r1, #0
    mov r5, #128
    mov r6, #135
    addne r6, r6, #32
    b {ON:#x}

title_on:
    ldr r12, ={var:#x}
    mov r1, #1
    str r1, [r12, #{TITLE}]
    mov r1, #0
    str r1, [r12, #{TITLE_SEL}]
    str r1, [r12, #{LIVE}]
    str r1, [r12, #{ANY_KEY}]
    ldr r1, ={BACK_INFO:#x}
    ldr r1, [r1]
    str r1, [r12, #{TITLE_N}]
    b {TITLE_GLOW + 4:#x}

.ltorg
"""


def save_src(var):
    return f"""
save:                       @ the save file screen's page; the door exists once there is a signature or a save
    push {{r4, r5, r6, r7, lr}}
    mov r4, r0
    ldr r5, ={var:#x}
    add r0, r4, #0x2000
    ldr r0, [r0]            @ the door sprite
    ldr r2, [r5, #{SAVE_SEL}]   @ 0 door, 1 right button, 2 right button with no door
    bic r2, r2, #4          @ back from the delete questions
    str r2, [r5, #{SAVE_SEL}]
    ldr r12, ={PAD:#x}
    ldrh r6, [r12, #2]
    bic r1, r2, #2
    cmp r0, #0
    moveq r1, #2
    cmp r1, r2
    bne save_store
    cmp r1, #2
    beq save_draw
    tst r6, #0x30
    beq save_draw
    bl save_anim
    bl {SAVE_BACK + 4:#x}
    b save_moved
save_store:
    str r1, [r5, #{SAVE_SEL}]
save_moved:
    bl {KILL:#x}
save_draw:
    ldr r2, [r5, #{SAVE_SEL}]
    cmp r2, #0
    mov r7, #{SAVE_DOOR}
    movne r7, #{SAVE_TRASH}
    mov r0, r7
    mov r1, #{SAVE_Y - 26}
    bl {DRAW:#x}
    bl {SAVE_BACK + 8:#x}
    mov r0, r4
    bl {SAVE_PAGE:#x}
    ldr r0, [r4, #0x34]
    cmp r0, #4
    popeq {{r4, r5, r6, r7, pc}}
    bl {KILL:#x}
    pop {{r4, r5, r6, r7, pc}}

save_anim:                  @ the door only animates while selected
    eor r1, r2, #1
    str r1, [r5, #{SAVE_SEL}]
    rsb r2, r1, #1
    lsl r2, r2, #12
    mov r3, #0
    push {{r3, lr}}
    mov r1, #3
    bl {SET_SEQ:#x}
    pop {{r3, pc}}

.ltorg
"""
