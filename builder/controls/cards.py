"""The Deltora Card book: kill counts, Item and Detailed Info, places, the special card.

Part of the controls namespace (see __init__.py): names from every part are shared."""

HEX_CODE, HEX_ROOM = 0x02215760, 0x80           # the 21st kilobyte: the card book hexagon, built at its end state once seen
CARD_ADDED, CARD_ADDED_ROOM = 0x022157E0, 0x20  # a card's count stored: the hexagon is new again
LOC_CODE, LOC_ROOM = 0x022171A8, 0x978  # the card book: once the game is cleared, an unowned card's place
LOC_SITE = 0x020619A0           # FUN_02061964 (r6 the book), message 9999: bl FUN_02033528(1, 0x80, y, 1, "??????"),
UNKNOWN_SHOW, NAME_SHOW = 0x02033528, 0x020335B0   # that (an ASCII string) and (1, 0, y, tokens), as a card's name
HEX_SITE, HEX_TARGET = 0x020A5C5C, 0x020A59DC   # the hexagon setup's last level target
CARD_SET_SITE, CARD_ADD_SITE = 0x02091040, 0x020910A8    # the item store's card count set and add
GOLD_VIEW_SITES = (0x02064098, 0x02064664, 0x02065098)   # the card book asks if the special card is owned:
                                                          # now also yes from GOLD_KILLS defeated
GOLD_DROP_SITE = 0x0207CA88    # the drop roll: 1 in 128 turns an owned card's drop into the special one; never now
CARDS_CODE, CARDS_ROOM = 0x0221473C, 0x6E4     # card Item Info, Detailed Info and kill counts
CARD_STRS, CARD_STRS_ROOM = 0x0221570C, 0x54    # the cards block's text buffer and longest hint, after TEXT_BUFS
KILLS_FOR_CARD = 10            # from this many defeated, an enemy always drops its card if it isn't owned
KILL_SAVE_AT = 0x1F40          # backup bytes after the options, unused by the game
CARD_LINE_Y, CARD_HINT_X, CARD_COUNT_X = 152, 72, 176    # the card page: under the notes, inside the frame
GOLD_KILLS = 50               # this many defeated gives a card the special (gold) look
KILL_ROLL_SITE, DROP_ROLL = 0x0207CEC4, 0x0207C8D8     # an enemy's death asks its drop roll
CARD_COUNT = 0x0209165C        # (save, card) -> how many owned
CARD_TEXT_SITE, CARD_TEXT = 0x02064070, 0x02061AF4     # the card page's notes
CARD_FREE = 0x02061BD4         # the bag pages' text clear
KILL, DRAW = SHARED_BASE + 4, SHARED_BASE + 8
CARD = 0x02210EF8                 # the end of the NEXT_ITEM block: the card page's left and right arrows
CARD_COL = 0x0221259C             # the end of the INPUT block


def card_places():
    """[label or None] per card: where it is first found, in the game's order (cardinfo's places,
    as the Detailed Info names them: "Ch. 2: Grasslands", "Final Ch.: Sewers", "Tower of Illusion").
    People met and cards no enemy drops have none."""
    data = drops.enemies()
    found, records = cardinfo.where(), cardinfo.card_records(data)
    order = []
    for key in sorted(cardinfo.place_names()):
        p = cardinfo.place_names()[key]
        if p not in order:
            order.append(p)
    chests = {}                 # card -> places: chests and pots (spawn kind 3) hold an item at +14 (cards 116 + card, gold + 112)
    givers = {}                 # script -> cards it gives (SetBagItemNum, AddBagItemNum, CardGetW of a card item)
    starts = {}                 # script -> events it starts (EventV and the like): an event's card is found where it starts
    for fid in range(1700, 2700):
        for name, ints in cardinfo.script_ops(fid) or ():
            if name in ("SetBagItemNum", "AddBagItemNum", "CardGetW"):
                for v in ints:
                    if ITEM_CARD0 <= v < ITEM_CARD0 + 2 * drops.CARDS:
                        givers.setdefault(fid, set()).add((v - ITEM_CARD0) % drops.CARDS)
            elif name in ("EventV", "Event", "LoadExecEvent", "SetEvent", "SetEventNoWait", "EventSet"):
                starts.setdefault(fid, set()).update(v for v in ints if 1700 < v < 2700)
    for _ in range(4):          # events that start events
        for fid in list(starts):
            for e in list(starts[fid]):
                givers.setdefault(fid, set()).update(givers.get(e, ()))
    names = cardinfo.place_names()
    for key, scripts in sorted(cardinfo.stage_areas().items()):
        if key not in names:
            continue
        for sc in scripts:
            for c in givers.get(sc, ()):    # the area's own events
                chests.setdefault(c, set()).add(names[key])
            for name, ints in cardinfo.script_ops(sc) or ():
                if name != "push" or ints not in cardinfo.SPAWN_FILES:
                    continue
                d = open(f"work/lf2/{ints:05d}.bin", "rb").read()
                for k in {v for v in struct.unpack_from("<64h", d, 0) if v >= 0}:
                    p = 0x80 + k * 0x1C
                    while p + 0x1C <= len(d) and struct.unpack_from("<H", d, p)[0] != 0xFFFF:
                        w = struct.unpack_from("<14H", d, p)
                        if w[0] == 3 and w[12] in CHEST_SCRIPTS and ITEM_CARD0 <= w[7] < ITEM_CARD0 + 2 * drops.CARDS:
                            chests.setdefault((w[7] - ITEM_CARD0) % drops.CARDS, set()).add(names[key])
                        elif w[0] == 1 and w[12] in givers:     # someone whose script gives a card (the painter)
                            for c in givers[w[12]]:
                                chests.setdefault(c, set()).add(names[key])
                        p += 0x1C
    out = []
    for card in range(drops.CARDS):
        places = {p for r in records.get(card, []) for p in found.get(r, [])} | chests.get(card, set())
        out.append(CARD_PLACE_FIX.get(card) or (cardinfo.chapter_lines([min(places, key=order.index)])[0] if places else None))
    return out


CARD_PLACE_FIX = {              # cards from bosses, events and the shop, which the data above can't place
    60: "Ch. 2: Lake of Tears",         # Jin & Jod
    61: "Ch. 3: City of the Rats",      # Ra-Kacharz
    69: "Ch. 5: Dread Mountain",        # Kin
    36: "Ch. 6: Maze of the Beast",     # Mary and Ida
    37: "Ch. 6: Maze of the Beast",     # Woman in the Pink Dress
    38: "Ch. 7: Valley of the Lost",    # Goat
    81: "Tom's Shop",                  # Tom
    104: "Mokeet's Mansion",            # Mokeet
    105: "Mokeet's Mansion",            # Mikeeta
    **{c: "Tower of Illusion" for c in range(95, 100)},     # the five dragons
}
ITEM_CARD0 = 0x74               # FUN_0207c6f8: items from 0x74 are cards (0x70-0x73 money, below that the rest)


def loc_src(places):
    """The card book's list, an unowned card: its name is message 9999, the "???????" text. Once
    the game is cleared (global byte 0, which the ending sets), a card with a place shows that
    instead: where to find it."""
    labels = sorted({p for p in places if p})
    index = [labels.index(p) if p else 0xFF for p in places]
    texts = "\n".join(f"loc_{i}:\n.short " + ", ".join(f"{t:#x}" for t in entext.encode(l) + [0xFFFD]) + "\n.align 2"
                      for i, l in enumerate(labels))
    return f"""
card_loc:                   @ for bl UNKNOWN_SHOW (r0-r3 and [sp] its arguments, r2 the y): r6 the book
    push {{r0, r1, r2, r3, r4, lr}}
    mov r4, #0
    ldr r0, ={SCRIPT_BYTES:#x}
    ldr r0, [r0]            @ (set once the scripts start: always, by the card book)
    ldrb r0, [r0]
    cmp r0, #0
    beq loc_none            @ not cleared yet
    add r0, r6, #0x1000
    ldr r0, [r0, #0xAEC]    @ the card
    cmp r0, #{drops.CARDS}
    bhs loc_none
    adr r1, loc_of
    ldrb r0, [r1, r0]
    cmp r0, #0xFF
    beq loc_none
    adr r1, loc_texts
    ldr r4, [r1, r0, lsl #2]
loc_none:
    cmp r4, #0
    ldmia sp, {{r0, r1, r2, r3}}
    beq loc_unknown
    mov r3, r4              @ its place, drawn as a name is
    mov r1, #0
    mov r0, #1
    bl {NAME_SHOW:#x}
    add sp, sp, #16
    pop {{r4, pc}}
loc_unknown:
    add sp, sp, #16
    pop {{r4, lr}}
    b {UNKNOWN_SHOW:#x}     @ as it was (its string still at [sp])
.ltorg
loc_texts:
.word {", ".join(f"loc_{i}" for i in range(len(labels)))}
loc_of:
.byte {", ".join(str(i) for i in index)}
.align 2
{texts}
"""


def kill_size(n_slots):
    """The kill counts' bytes: a halfword each, then the hexagon's seen flag (byte), rounded to words."""
    return (2 * n_slots + 1 + 3) // 4 * 4


def hex_src(seen):
    """The card book hexagon, after its setup sets the six levels: on the first opening since a
    card was added it climbs as usual (and the seen flag is set); after that every category
    starts at its level, with its sprite frame, and neither the step nor the full-level sound plays."""
    return f"""
    push {{r4, r5, lr}}
    bl {HEX_TARGET:#x}      @ the call this replaced
    ldr r3, ={seen:#x}
    ldrb r0, [r3]
    cmp r0, #0
    moveq r0, #1
    strbeq r0, [r3]
    popeq {{r4, r5, pc}}
    mov r4, #0
hex_level:                  @ r10 the hexagon: +0x1F0 shown levels, +0x1F6 their targets
    add r5, r10, r4
    ldrb r1, [r5, #0x1F6]
    strb r1, [r5, #0x1F0]
    subs r1, r1, #1
    bmi hex_next
    mov r2, #0x44
    mul r0, r4, r2
    add r0, r0, r10
    add r0, r0, #0x58       @ its sprite: frame level - 1, as each step sets it
    bl {SPRITE_ANIM:#x}
hex_next:
    add r4, r4, #1
    cmp r4, #6
    blt hex_level
    mov r0, #1
    str r0, [r10, #0x23C]   @ the full-level sound counts as started
    pop {{r4, r5, pc}}
.ltorg
"""


def card_added_src(seen):
    """The item store's two card count writes, then the hexagon is new again (r3, r12 are free)."""
    return f"""
    strb r7, [r0, #0x9FC]   @ set
    b card_new
    strb r4, [r2, r1]       @ add
card_new:
    ldr r3, ={seen:#x}
    mov r12, #0
    strb r12, [r3]
    bx lr
.ltorg
"""


def cards_src(slots, n_slots):
    """Card book Item Info, kill counts and the guaranteed card.
    Kill counts: one halfword per card an enemy can drop (slots maps card -> counter; 254 a
    boss with no counter, 255 someone met, with no Item or Detailed Info), kept in
    the backup at KILL_SAVE_AT, read when the save file is opened, cleared for a new game and
    written when a save succeeds. On a fought enemy's page, X steps from its notes to its Item
    Info (message 112 + card), its Detailed Info (224 + card) and back; people met keep their
    notes. The notes also show how many were defeated once the card is owned."""
    VIEW, LOADED, TXT = 0, 4, 8
    KILL_SIZE = kill_size(n_slots)
    assert KILL_SAVE_AT + KILL_SIZE <= 0x2000
    hint = [entext.encode(t) + [0xFFFD] for t in ("Ⓧ: Item Info", "Ⓧ: Card Info")]    # Detailed Info's is in card_strs_src
    defeated = entext.encode("Defeated: ")
    digit0 = entext.encode("0")[0]
    assert entext.encode("9")[0] == digit0 + 9
    short = lambda r: ".short " + ", ".join(f"{x:#x}" for x in r + [0] * (-len(r) % 2))
    return f"""
    b kill_roll
    b kills_load
    b kills_save
    b card_show
    b card_free
    b card_key
    b card_list
    b gold_look

gold_look:                  @ r0 the save, r1 a special card: owned, or its card owned and
    push {{r4, r5, lr}}     @ {GOLD_KILLS} of that enemy defeated
    mov r4, r0
    mov r5, r1
    bl {CARD_COUNT:#x}
    cmp r0, #0
    popne {{r4, r5, pc}}
    sub r5, r5, #{drops.CARDS}
    mov r0, r4
    mov r1, r5
    bl {CARD_COUNT:#x}
    cmp r0, #0
    popeq {{r4, r5, pc}}
    ldr r0, =slots
    ldrb r0, [r0, r5]
    cmp r0, #254
    movhs r0, #0
    pophs {{r4, r5, pc}}
    ldr r1, =kills
    add r1, r1, r0, lsl #1
    ldrh r1, [r1]
    mov r0, #0
    cmp r1, #{GOLD_KILLS}
    movhs r0, #1
    pop {{r4, r5, pc}}

kill_roll:                  @ r0 the enemy, r1 where the drop goes: count it, and from the
    push {{r4, r5, r6, r7, r8, lr}}     @ {KILLS_FOR_CARD}th on, an unowned card always drops
    mov r4, r0
    mov r5, r1
    add r6, r4, #0x400
    add r6, r6, #0xA8       @ its drop table: 8 of (tag, item, weight, 0)
    mov r7, #8
find_card:
    ldrsh r0, [r6]
    cmp r0, #0
    beq next_entry
    ldrh r0, [r6, #2]
    sub r8, r0, #{drops.CARD0}
    cmp r8, #{drops.CARDS}
    blo found_card
next_entry:
    add r6, r6, #8
    subs r7, r7, #1
    bne find_card
    b roll
found_card:
    ldr r0, =slots
    ldrb r0, [r0, r8]
    cmp r0, #254
    bhs roll
    ldr r1, =kills
    add r1, r1, r0, lsl #1
    ldrh r0, [r1]
    ldr r2, =0xFFFE
    cmp r0, r2
    addlo r0, r0, #1
    strhlo r0, [r1]
    cmp r0, #{KILLS_FOR_CARD}
    blo roll
    ldr r0, ={DROP_SAVE:#x}
    ldr r0, [r0]
    bl {FIND_TASK:#x}
    mov r1, r8
    bl {CARD_COUNT:#x}
    cmp r0, #0
    bne roll
    mov r0, r4              @ the roll's own reasons for no drop at all
    bl {NO_DROP:#x}
    cmp r0, #0
    bne roll
    mov r0, #9
    bl {NO_DROP_9:#x}
    cmp r0, #0
    bne roll
    ldmia r6, {{r0, r1}}
    stmia r5, {{r0, r1}}
    mov r0, #1
    pop {{r4, r5, r6, r7, r8, pc}}
roll:
    mov r0, r4
    mov r1, r5
    pop {{r4, r5, r6, r7, r8, lr}}
    b {DROP_ROLL:#x}

kills_load:                 @ the save file screen's result: -1 a new game, 0 and up a loaded file
    push {{r4, lr}}
    bl {LOAD_RESULT:#x}
    mov r4, r0
    cmn r4, #1
    beq kills_clear
    cmp r4, #0
    blt kills_loaded
    ldr r0, ={BACKUP_READ:#x}
    bl backup_io
    cmp r0, #0
    beq kills_loaded
    ldr r1, =kills          @ never written: 0xFFFF
    mov r2, #0
    ldr r3, =0xFFFF
unset:
    ldrh r0, [r1, r2]
    cmp r0, r3
    moveq r0, #0
    strheq r0, [r1, r2]
    add r2, r2, #2
    cmp r2, #{KILL_SIZE}
    blt unset
    b kills_ok
kills_clear:
    ldr r1, =kills
    mov r0, #0
    mov r2, #0
clear:
    str r0, [r1, r2]
    add r2, r2, #4
    cmp r2, #{KILL_SIZE}
    blt clear
kills_ok:
    ldr r1, =vars
    mov r0, #1
    str r0, [r1, #{LOADED}]
kills_loaded:
    mov r0, r4
    pop {{r4, pc}}

kills_save:                 @ a save went through: the counts too, if they came from this file
    push {{lr}}
    ldr r1, =vars
    ldr r0, [r1, #{LOADED}]
    cmp r0, #0
    beq kills_kept
    ldr r0, ={BACKUP_WRITE:#x}
    bl backup_io
kills_kept:
    pop {{lr}}
    mvn r8, #0              @ the instruction this call replaced
    bx lr

backup_io:                  @ r0 BACKUP_READ or BACKUP_WRITE; 1 if done
    push {{r4, r5, r6, lr}}
    mov r5, r0
    mov r6, #0
    bl {LOCK_ID:#x}
    mov r4, r0
    cmn r0, #3
    beq io_end
    bl {CARD_LOCK:#x}
    ldr r0, ={KILL_SAVE_AT:#x}
    ldr r1, =kills
    mov r2, #{KILL_SIZE}
    blx r5
    mov r0, r4
    bl {CARD_UNLOCK:#x}
    mov r0, r4
    bl {LOCK_RELEASE:#x}
    mov r6, #1
io_end:
    mov r0, r6
    pop {{r4, r5, r6, pc}}

card_list:                  @ the card list: a page opened from it starts on the notes
    ldr r1, =vars
    mov r0, #0
    str r0, [r1, #{VIEW}]
    bx lr

view_of:                    @ r0 a card: the view it shows (people met have only their notes)
    ldr r1, =slots
    ldrb r1, [r1, r0]
    ldr r0, =vars
    ldr r0, [r0, #{VIEW}]
    cmp r1, #255
    moveq r0, #0
    bx lr

card_show:                  @ r0 the book, r1 the card: its notes, Item Info or Detailed Info, then our lines
    push {{r4, r5, r6, lr}}
    mov r4, r0
    mov r5, r1
    mov r0, r1
    bl view_of
    mov r6, r0
    mov r2, #{drops.FIRST_ID}
    mla r5, r0, r2, r5      @ message 112 * view + card
    cmp r6, #0
    blne {TOWER_OPEN:#x}
    cmpne r0, #0
    addne r5, r5, #{cardinfo.TOWER_SHIFT}    @ Item and Detailed Info as they are once the Tower is open
    mov r1, r5
    mov r0, r4
    bl {CARD_TEXT:#x}
    bl extras
    pop {{r4, r5, r6, pc}}

card_key:                   @ r4 the book, on a card page: X steps notes, Item Info, Detailed Info
    push {{r0, r1, r2, r3, r4, r12, lr}}
    ldr r0, ={PAD:#x}
    ldrh r0, [r0, #2]
    tst r0, #0x400
    beq key_end
    add r1, r4, #0x1000
    ldr r1, [r1, #0xAEC]
    ldr r0, =slots
    ldrb r0, [r0, r1]
    cmp r0, #255
    beq key_end             @ people met: their notes only
    ldr r1, =vars
    ldr r0, [r1, #{VIEW}]
    add r0, r0, #1
    cmp r0, #3
    movhs r0, #0
    str r0, [r1, #{VIEW}]
    ldr r0, ={SOUND:#x}
    mov r1, #0
    mov r2, #103
    bl {PLAY_SE:#x}
    add r1, r4, #0x1000
    ldr r1, [r1, #0xAEC]
    mov r0, r4
    bl card_show
key_end:
    pop {{r0, r1, r2, r3, r4, r12, pc}}

card_free:                  @ the bag pages' text clear: ours goes with it
    push {{r0, lr}}
    mov r0, #0
    mov r1, #0
    bl put_line
    mov r0, #1
    mov r1, #0
    bl put_line
    pop {{r0, lr}}
    push {{r4, lr}}         @ the instruction this jump replaced
    b {CARD_FREE + 4:#x}

extras:                     @ r4 the book: the X hint, and on the notes the defeated count
    push {{r5, r6, r7, lr}}
    add r6, r4, #0x1000
    ldr r6, [r6, #0xAEC]
    mov r0, r6
    bl view_of
    mov r5, r0
    ldr r1, =hints
    ldr r1, [r1, r5, lsl #2]
    ldr r0, =slots
    ldrb r7, [r0, r6]
    cmp r7, #255
    moveq r1, #0            @ people met: no hint
    mov r0, #0
    mov r2, #{CARD_LINE_Y}
    mov r3, #{CARD_HINT_X}
    bl put_line_at
    cmp r5, #0
    bne extras_end
    cmp r7, #254            @ bosses keep no count
    bhs extras_end
    ldr r0, ={SAVE_TASK:#x}
    bl {SAVE_OF:#x}
    mov r1, r6
    bl {CARD_COUNT:#x}
    cmp r0, #0
    beq extras_end
    ldr r0, =kills
    add r0, r0, r7, lsl #1
    ldrh r0, [r0]
    ldr r1, ={CARD_STRS:#x}  @ "Defeated: " then the digits
    ldr r2, =defeated
    mov r3, #{len(defeated)}
copy:
    ldrh r12, [r2], #2
    strh r12, [r1], #2
    subs r3, r3, #1
    bne copy
    mov r5, sp              @ digits backwards onto the stack, then forwards
    mov r3, #0
digits:
    mov r2, #0              @ r0 / 10 by subtraction: r0 is at most 65534
div:
    cmp r0, #10
    subhs r0, r0, #10
    addhs r2, r2, #1
    bhs div
    add r0, r0, #{digit0}
    strh r0, [sp, #-2]!
    add r3, r3, #1
    movs r0, r2
    bne digits
forward:
    ldrh r0, [sp], #2
    strh r0, [r1], #2
    subs r3, r3, #1
    bne forward
    ldr r0, =0xFFFD
    strh r0, [r1]
    mov sp, r5
    mov r0, #1
    ldr r1, ={CARD_STRS:#x}
    mov r2, #{CARD_LINE_Y}
    mov r3, #{CARD_COUNT_X}
    bl put_line_at
extras_end:
    pop {{r5, r6, r7, pc}}

put_line:                   @ r0 our line 0 or 1, r1 tokens (0 clears), r2 top y, r3 centre x
put_line_at:
    push {{r4, r5, r6, r7, r8, lr}}
    mov r8, r3
    sub sp, sp, #16
    mov r5, r0
    mov r6, r1
    mov r7, r2
    ldr r3, =vars
    add r3, r3, #{TXT}
    ldr r0, [r3, r5, lsl #2]
    subs r0, r0, #1
    bmi line_fresh
    mov r2, #0
    str r2, [r3, r5, lsl #2]
    add r3, r3, #8          @ the buffer we gave it: if the slot holds another now, it isn't ours
    ldr r2, [r3, r5, lsl #2]
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
    ldr r3, =vars
    add r3, r3, #{TXT}
    add r2, r4, #1
    str r2, [r3, r5, lsl #2]
    add r3, r3, #8
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
vars:
.word 0, 0, 0, 0, 0, 0      @ view, loaded, 2 text slots + 1, their buffers
hint0:
{short(hint[0])}
hint2:
{short(hint[1])}
hints:
.word hint0, {CARD_STRS + 32:#x}, hint2
defeated:
{short(defeated)}
slots:
.byte {", ".join(str(x) for x in slots)}
kills:
.space {KILL_SIZE}
"""


def card_strs_src():
    """The card book's "Defeated: n" line (32 bytes: n is at most 65534), then its Detailed Info hint."""
    hint = entext.encode("Ⓧ: Detailed Info") + [0xFFFD]
    hint += [0] * (len(hint) % 2)
    return f"""
.space 32
.short {", ".join(f"{x:#x}" for x in hint)}
"""


def tower_open_src():
    """r0 nonzero once the Tower of Illusion is open: script 2578 sets its world map spot
    after Fallow, and the world map shows the spot by that bit."""
    return f"""
    ldr r0, ={SCRIPT_SHORTS:#x}
    ldr r0, [r0]
    cmp r0, #0
    ldrhne r0, [r0, #{MAP_SPOTS * 2}]
    and r0, r0, #{TOWER_SPOT:#x}
    bx lr
.ltorg
"""
