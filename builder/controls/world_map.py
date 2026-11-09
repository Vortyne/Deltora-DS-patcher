"""The world map: D-pad travel, chests remaining and completion.

Part of the controls namespace (see __init__.py): names from every part are shared."""

CHEST_CODE, CHEST_ROOM = 0x02217B60, 0x200  # the world map: a spot's chests not yet opened (the 30th kilobyte)
COMP_CODE, COMP_ROOM = 0x02217DA0, 0x5C0   # the completion percentage: from live memory or a file's save (to the 31st kilobyte's end)
MAP_SPOTS, TOWER_SPOT = 1, 0x2000      # short 1: the world map's open spots; the Tower is spot 14
# world map, script 2609: all unused script commands
MAP_TOUCH, MAP_TOUCH_ROOM = 0x02211B30, 108     # SetMobDecScl
MAP_TICK, MAP_TICK_ROOM = 0x02212A10, 120       # TilePosition
MAP_DRAW, MAP_DRAW_ROOM = 0x02212A88, 104       # TileAngle
MAP_SEARCH, MAP_SEARCH_ROOM = 0x022125BC, 252   # LaserWindow
MAP_ENDS, MAP_ENDS_ROOM = 0x02211D98, 88        # SetMapObjScript; a mob vtable uses the veneer after it
MAP_STATE, MAP_STATE_ROOM = 0x02210C60, 20      # MessageI, unused
MAP_ARROW, MAP_ARROW_ROOM = 0x02211D1C, 124     # GetStageNo
MAP_NEAR, MAP_NEAR_ROOM = 0x02212968, 68        # the end of the TITLE block
MAP_SPAWN, MAP_SPAWN_ROOM = 0x0221221C, 64      # the end of the MESSAGE block
MAP_ID, MAP_ID_ROOM = 0x02211D08, 20            # the end of the HOOKS block
MAP_SEEN, MAP_ACTIVE, MAP_SEL, MAP_CHOSEN, MAP_POINTER = range(0, 20, 4)
MAP_ARROW_TALL, MAP_ARROW_LOW = 26, 12     # pixels above the spot
MAP_MARK = 17               # width the patched map script asks for


def map_touch_src():
    return f"""
touch:                      @ IsMobTouchSize; the map asks once per open spot, each frame
    push {{r4, r5, r6, lr}}
    mov r4, r0
    mov r1, #1
    bl {SCRIPT_ARG:#x}
    cmp r0, #{MAP_MARK}
    bne {MAP_ENDS + 8:#x}
    mov r0, r4
    mov r1, #0
    bl {SCRIPT_ARG:#x}
    mov r5, r0
    ldr r3, ={MAP_STATE:#x}
    mov r6, #1
    and r0, r5, #31         @ object ids climb with each scene: the masks hold them modulo 32
    lsl r6, r6, r0
    ldr r0, [r3, #{MAP_SEEN}]
    tst r0, r6
    beq touch_new
    str r0, [r3, #{MAP_ACTIVE}]
    bl {MAP_TICK:#x}
    ldr r3, ={MAP_STATE:#x}
    mov r0, #0
touch_new:
    orr r0, r0, r6
    str r0, [r3, #{MAP_SEEN}]
    b {MAP_ENDS + 4:#x}

.ltorg
"""


def map_tick_src(var):
    return f"""
tick:                       @ the map's D-pad; r4 and r5 belong to the caller
    push {{r4, r5, r6, lr}}
    sub r2, r5, #12         @ the spots lie within 32 ids of here
    ldr r0, ={var + MAP:#x}
    mov r1, #3
    str r1, [r0]
    ldr r4, ={MAP_STATE:#x}
    ldr r0, ={PAD:#x}
    ldrh r6, [r0, #2]
    ldr r5, [r4, #{MAP_SEL}]
    ldr r0, [r4, #{MAP_ACTIVE}]
    and r1, r5, #31
    lsr r0, r0, r1
    cmp r5, #0
    tstne r0, #1
    bne tick_have
    mov r5, #0              @ nothing chosen yet: the spot nearest the player
    mov r1, #4
    b tick_find
tick_have:
    ands r0, r6, #0xF0
    beq tick_show
    clz r0, r0              @ right, left, up, down become 0 to 3
    rsb r1, r0, #27
tick_find:
    bl {MAP_SEARCH:#x}
    b tick_draw
tick_show:
    mov r0, #0
tick_draw:
    mov r1, r6
    b {MAP_DRAW:#x}

.ltorg
"""


def map_draw_src():
    return f"""
show:                       @ r0 the new spot or 0, r1 the buttons, r4 state, r5 old spot
    mov r6, r1
    cmp r0, #0
    beq show_it
    str r0, [r4, #{MAP_SEL}]
    cmp r5, #0
    beq show_it
    ldr r0, ={SOUND:#x}
    mov r1, #0
    mov r2, #0x67
    bl {PLAY_SE:#x}
show_it:
    ldr r0, ={WORLD:#x}
    ldr r1, [r4, #{MAP_SEL}]
    bl {FIND_MOB:#x}
    cmp r0, #0
    popeq {{r4, r5, r6, pc}}
    bl {MAP_ARROW:#x}
    b {MAP_ENDS:#x}

.ltorg
"""


def map_state_src():
    return f"""
    b choose
    b answer
    b real

choose:                     @ r4 state, r6 the buttons
    tst r6, #1
    popeq {{r4, r5, r6, pc}}
    ldr r0, [r4, #{MAP_SEL}]
    str r0, [r4, #{MAP_CHOSEN}]
    bl {MAP_ARROW + 4:#x}
    pop {{r4, r5, r6, pc}}

answer:                     @ r3 state, r4 script, r5 this spot; A or a real touch
    ldr r0, [r3, #{MAP_CHOSEN}]
    cmp r0, r5
    bne real
    mov r0, #0
    str r0, [r3, #{MAP_CHOSEN}]
    mov r0, r4
    mov r1, #1
    bl {SET_RESULT:#x}
    mov r0, #1
    pop {{r4, r5, r6, pc}}

real:
    mov r0, r4
    pop {{r4, r5, r6, lr}}
    b {SB_TOUCH_SIZE:#x}
"""


def map_arrow_src():
    return f"""
    b arrow
    b hide_arrow

arrow:                      @ r0 the spot, r4 state: the camp's green arrow, over that spot
    push {{r6, r7, r8, lr}}
    mov r7, r0
    bl get_arrow
    ldr r1, [r7, #0x220]
    str r1, [r0, #0x220]
    ldr r2, [r7, #0x2E8]
    cmp r2, #2              @ the campfire and shop are tall, and so is the player on a spot
    cmpne r2, #4
    blne {MAP_NEAR:#x}
    ldr r1, [r7, #0x224]
    subeq r1, r1, #{MAP_ARROW_TALL << 12:#x}
    subne r1, r1, #{MAP_ARROW_LOW << 12:#x}
    str r1, [r0, #0x224]
    pop {{r6, r7, r8, pc}}

hide_arrow:
    push {{r3, lr}}
    bl get_arrow
    mov r1, #{300 << 12:#x}
    str r1, [r0, #0x224]
    pop {{r3, pc}}

get_arrow:
    push {{r3, lr}}
    ldr r1, [r4, #{MAP_POINTER}]
    cmp r1, #0
    beq {MAP_SPAWN:#x}
    ldr r0, ={WORLD:#x}
    bl {FIND_MOB:#x}
    cmp r0, #0
    popne {{r3, pc}}
    b {MAP_SPAWN:#x}

.ltorg
"""


def map_near_src():
    return f"""
near:                       @ r7 the spot; Z set if the player is on it; keeps r0
    push {{r0, lr}}
    ldr r0, ={WORLD:#x}
    bl {GET_PLAYER:#x}
    ldr r1, [r0, #0x220]
    ldr r2, [r7, #0x220]
    sub r1, r1, r2
    add r1, r1, #0x8000     @ within 8 pixels on each axis
    lsrs r1, r1, #16
    bne near_end
    ldr r1, [r0, #0x224]
    ldr r2, [r7, #0x224]
    sub r1, r1, r2
    add r1, r1, #0x8000
    lsrs r1, r1, #16
near_end:
    pop {{r0, pc}}

.ltorg
"""


def map_spawn_src():
    return f"""
    sub sp, sp, #8
    mov r3, #0
    str r3, [sp]
    str r3, [sp, #4]
    mov r2, #0
    mov r1, #31
    ldr r0, ={EVENTS:#x}
    bl {SPAWN_OBJECT:#x}
    add sp, sp, #8
    str r0, [r4, #{MAP_POINTER}]
    mov r1, r0
    ldr r0, ={WORLD:#x}
    bl {FIND_MOB:#x}
    pop {{r3, pc}}

.ltorg
"""


def map_id_src():
    return """
    ldr r5, [sp]            @ r9 is a spot's id modulo 32, [sp] the lowest id it can be
    sub r0, r9, r5
    and r0, r0, #31
    add r5, r5, r0
    bx lr
"""


def map_search_src():
    return f"""
search:                     @ r1 right, left, up, down or 4 for nearest; from spot r5, or the player
    push {{r4, r5, r6, r7, r8, r9, r10, r11, lr}}
    sub sp, sp, #4
    str r2, [sp]
    mov r8, r1
    ldr r0, ={WORLD:#x}
    cmp r5, #0
    bne from_spot
    bl {GET_PLAYER:#x}
    b from_here
from_spot:
    mov r1, r5
    bl {FIND_MOB:#x}
from_here:
    ldr r6, [r0, #0x220]
    ldr r7, [r0, #0x224]
    mov r9, #0
    mov r10, #0
    mvn r11, #0x80000000
each:
    ldr r0, [r4, #{MAP_ACTIVE}]
    lsr r0, r0, r9
    tst r0, #1
    beq skip
    bl {MAP_ID:#x}
    ldr r0, ={WORLD:#x}
    mov r1, r5
    bl {FIND_MOB:#x}
    cmp r0, #0
    beq skip
    ldr r1, [r0, #0x220]
    sub r1, r1, r6
    ldr r2, [r0, #0x224]
    sub r2, r2, r7
    cmp r8, #1
    rsbeq r1, r1, #0
    cmp r8, #2
    rsbeq r2, r2, #0
    cmpne r8, #3
    bne no_swap
    mov r3, r1
    mov r1, r2
    mov r2, r3
no_swap:
    cmp r8, #4
    beq scored
    cmp r1, #0
    ble skip
scored:
    cmp r1, #0
    rsblt r1, r1, #0
    cmp r2, #0
    rsblt r2, r2, #0
    add r0, r1, r2, lsl #1
    cmp r1, r2, lsr #1      @ mostly sideways of the press: only if nothing else is that way
    addlo r0, r0, #0x400000
    cmp r0, r11
    bge skip
    mov r11, r0
    mov r10, r5
skip:
    add r9, r9, #1
    cmp r9, #32
    blt each
    mov r0, r10
    add sp, sp, #4
    pop {{r4, r5, r6, r7, r8, r9, r10, r11, pc}}

.ltorg
"""


CHEST_SCRIPTS = (2235, 2236, 2368, 2369, 2371)    # chests, locked chests, pots: SetDropItemScr of their contents


CHEST_MARK = 0x4300             # GetTpTouch(CHEST_MARK + spot) on the world map: that spot's chests left, or -1
CHEST_FLAGS = 0x021D4C34        # the scripts' global flags (0x021D4A44 + 0x1F0): a chest sets the bit its spawn record names
CHEST_KINDS = (2235, 2236)      # chests and locked chests (pots and the rest aren't counted)
CHEST_MANSION = 10              # Mokeet's Mansion's spot: chapter 1's stages 5 and 6
CHEST_MSG = 336                 # bank 2197: "Chests Remaining: n"
CHEST_Y = 172                   # the top screen's last line
CHEST_VAR = (0x600A, 17)        # global int 17, which no script uses: the message's handle


def chest_spots():
    """{map spot: sorted chest flags}: spots 1-8 are chapters 1-7 and the final chapter (stage table
    chapters 1-8), spot 10 Mokeet's Mansion. Chests are spawn records of kind 3 with a chest's
    script; word 10 (+0x14) is the global flag the chest sets when opened."""
    spots = {}
    for (c, s), scripts in sorted(cardinfo.stage_areas().items()):
        if not 1 <= c <= 8:
            continue
        spot = CHEST_MANSION if (c, s) in ((1, 5), (1, 6)) else c
        for sc in scripts:
            for name, ints in cardinfo.script_ops(sc) or ():
                if name != "push" or ints not in cardinfo.SPAWN_FILES:
                    continue
                d = open(f"work/lf2/{ints:05d}.bin", "rb").read()
                for k in {v for v in struct.unpack_from("<64h", d, 0) if v >= 0}:
                    p = 0x80 + k * 0x1C
                    while p + 0x1C <= len(d) and struct.unpack_from("<H", d, p)[0] != 0xFFFF:
                        w = struct.unpack_from("<14H", d, p)
                        if w[0] == 3 and w[12] in CHEST_KINDS:
                            spots.setdefault(spot, set()).add(w[10])
                        p += 0x1C
    return {k: sorted(v) for k, v in spots.items()}


def chest_src():
    """script_ask's next stop: GetTpTouch(CHEST_MARK + spot) answers the spot's chests not opened,
    or -1 where the map shouldn't say: a chapter before it's cleared (the next spot is open: short 1
    has bit spot), the final chapter before the ending (global byte 0), and every spot that isn't a
    chapter or the mansion. Other arguments go on to the quiz's marks. r0 the argument, r4 the
    script; script_ask pushed r4 and lr."""
    spots = chest_spots()
    flags, index = [], []
    for spot in range(17):
        index.append(len(flags))
        flags += spots.get(spot, [])
    assert len(flags) < 256 and max(flags) < 0x800
    return f"""
chest_ask:
    ldr r1, ={CHEST_MARK:#x}
    sub r1, r0, r1
    cmp r1, #16
    bhs {COMP_CODE:#x}      @ the completion mark, the quiz's marks, or the plain touch read
    mvn r12, #0             @ -1: nothing to show
    cmp r1, #{CHEST_MANSION}
    beq chest_count
    cmp r1, #8
    bhi chest_done
    beq chest_final
    cmp r1, #0
    beq chest_done
    ldr r0, ={SCRIPT_SHORTS:#x}
    ldr r0, [r0]
    ldrh r0, [r0, #{MAP_SPOTS * 2}]
    mov r2, #1
    tst r0, r2, lsl r1      @ chapter n is cleared once spot n + 1 is open (bit n)
    beq chest_done
    b chest_count
chest_final:
    ldr r0, ={SCRIPT_BYTES:#x}
    ldr r0, [r0]
    ldrb r0, [r0]           @ the game cleared
    cmp r0, #0
    beq chest_done
chest_count:
    adr r0, chest_index
    add r0, r0, r1
    ldrb r2, [r0]
    ldrb r3, [r0, #1]
    adr r0, chest_flags
    add r2, r0, r2, lsl #1
    add r3, r0, r3, lsl #1
    mov r12, #0
    ldr r1, ={CHEST_FLAGS:#x}
chest_next:
    cmp r2, r3
    bhs chest_done
    ldrh r0, [r2], #2
    ldrb lr, [r1, r0, lsr #3]
    and r0, r0, #7
    lsr lr, lr, r0
    tst lr, #1
    addeq r12, r12, #1
    b chest_next
chest_done:
    mov r1, r12
    mov r0, r4
    bl {SET_RESULT:#x}
    mov r0, #1
    pop {{r4, pc}}

.ltorg
chest_index:
.byte {", ".join(str(i) for i in index)}
.align 1
chest_flags:
.short {", ".join(str(f) for f in flags)}
.align 2
"""


COMP_MARK = 0x4320              # GetTpTouch(COMP_MARK): the completion percentage once the game is cleared, else -1
COMP_MSG = 337                  # bank 2197: "Completion: n%"
COMP_Y = 176                    # the touch screen's last line, right-aligned (the world map)
COMP_FLAGS = 0x84100            # the touch screen, right-aligned, no panel, no wait
COMP_VAR = (0x600A, 12)         # global int 12, which no script uses: the world map's message handle
PLAYER_OF, PLAYER_LIST = 0x020A5440, 0x021E9E3C     # the player object, as the bag commands find it
SAVE_FLAGS, SAVE_ITEMS = 0x5C, 0x15C8                # a file's save: the chest flags; the item words (cards follow)
SAVE_BYTES, SAVE_SHORTS, SAVE_LONGS = 0x1B4C, 0x1B8C, 0x1D0C   # its script globals
ITEMS_OF = 0x83C                # the player's item words (112, top bit: had before), then 224 card counts
TOWER_CARD, MANSION_GROUP, MANSION_BIT = 99, 10, 7   # the Blue Dragon (floor 99); the mansion's last event done
# (name, weight %, what counts): chapters 1-7 by the next map spot open, the final one by the ending
COMP_PARTS = (("chapters", 50, 8), ("bag items", 5, 32), ("gear", 5, 32), ("recipes", 5, 16),
              ("key items", 5, 16), ("chests", 5, None), ("cards", 15, 112))


def comp_src():
    """The completion percentage. comp_calc(r0 a view: chest flags, item words, script bytes,
    shorts and longs) adds each part's share: its weight times found / all, in 1/65536ths (all
    found gives the weight exactly), then the Tower (the Blue Dragon card) and Mokeet's Mansion
    (group 10 bit 7), 5 each; the total rounds down. Items count when their word is nonzero (the
    bag keeps a used-up item's top bit); a card when it or its special version was ever held.
    comp_ask answers GetTpTouch(COMP_MARK) from live memory, -1 before the game is cleared; other
    arguments go on to the quiz's marks. comp_save(r0 a file's save) is for the file screen."""
    flags = sorted({f for v in chest_spots().values() for f in v})
    parts = {name: (w, d) for name, w, d in COMP_PARTS}
    parts["chests"] = (5, len(flags))
    per = {k: (w << 16) // d for k, (w, d) in parts.items()}
    assert sum(w for w, d in parts.values()) + 10 == 100
    def add(name, n_reg):
        w, d = parts[name]
        return f"""    mov r0, #{d}
    ldr r2, ={per[name]:#x}
    ldr r3, ={w << 16:#x}
    bl comp_add"""
    return f"""
    b comp_ask              @ +0: script_ask's chain (CHEST_CODE)
    b comp_save             @ +4: the file box's percentage (file_show)
    b file_strip            @ +8
    b file_free             @ +12
file_strip:                 @ r0 tokens, r1 the top y, r2 its record (slot + 1, buffer): right-aligned
    push {{r4, r5, r6, r7, lr}}
    sub sp, sp, #0x48
    mov r5, r0
    mov r6, r1
    mov r7, r2
    mov r0, #0
    str r0, [sp, #0x38]     @ the measure's right mode: 255 - the width
    str r0, [sp, #0x40]
    mov r0, sp
    mov r1, r5
    mov r2, #40
    bl {entext.MEASURE:#x}
    rsb r0, r0, #0xFF       @ the width
    ldr r1, ={FILE_RIGHT:#x}
    sub r6, r6, #0          @ (keep r6 the y)
    sub r4, r1, r0, lsr #1  @ the centre x
    str r4, [sp, #0x44]
    bl {FREE_SLOT:#x}
    cmn r0, #1
    beq file_strip_end
    mov r4, r0
    mov r0, #0x80
    bl {ALLOC:#x}
    bl {ARROW_SLOT:#x}      @ r4 the slot, r0 the buffer
    add r1, r4, #1
    str r1, [r7]
    str r0, [r7, #4]
    cmp r0, #0
    beq file_strip_end
    mov r1, #0xC
    str r1, [sp]
    mov r1, #1
    str r1, [sp, #4]
    mov r1, #0
    str r1, [sp, #8]
    str r5, [sp, #12]
    ldr r1, [sp, #0x44]
    mov r2, r6
    mov r3, #0
    bl {TEXT_CREATE:#x}
file_strip_end:
    add sp, sp, #0x48
    pop {{r4, r5, r6, r7, pc}}

file_free:                  @ r0 pt_data: both lines, if their slots still hold our buffers; no box after
    push {{r4, lr}}
    mov r4, r0
    mov r0, #0
    str r0, [r4, #12]
    add r0, r4, #16
    bl file_free_one
    add r0, r4, #28
    bl file_free_one
    pop {{r4, pc}}
file_free_one:              @ r0 a record
    ldr r1, [r0]
    mov r2, #0
    str r2, [r0]
    subs r1, r1, #1
    bxmi lr
    ldr r2, ={TEXT_SLOTS:#x}
    ldr r2, [r2, r1, lsl #5]
    ldr r3, [r0, #4]
    cmp r2, r3
    bxne lr
    mov r0, r1
    b {TEXT_FREE:#x}


comp_ask:                   @ script_ask's chain: r0 the argument, r4 the script, {{{{r4, lr}}}} pushed
    ldr r1, ={COMP_MARK:#x}
    cmp r0, r1
    bne {QUIZ_CODE:#x}
    mvn r1, #0
    ldr r0, ={SCRIPT_BYTES:#x}
    ldr r0, [r0]
    ldrb r0, [r0]
    cmp r0, #0
    beq comp_answer         @ not cleared yet
    ldr r0, ={PLAYER_LIST:#x}
    bl {PLAYER_OF:#x}
    cmp r0, #0
    mvneq r1, #0
    beq comp_answer
    sub sp, sp, #20
    add r0, r0, #{ITEMS_OF & ~0xFF:#x}
    add r0, r0, #{ITEMS_OF & 0xFF:#x}
    ldr r1, ={CHEST_FLAGS:#x}
    str r1, [sp]            @ the chest flags
    str r0, [sp, #4]        @ the item words
    ldr r0, ={SCRIPT_BYTES:#x}
    ldr r0, [r0]
    str r0, [sp, #8]
    ldr r0, ={SCRIPT_SHORTS:#x}
    ldr r0, [r0]
    str r0, [sp, #12]
    ldr r0, ={SCRIPT_LONGS:#x}
    ldr r0, [r0]
    str r0, [sp, #16]
    mov r0, sp
    bl comp_calc
    add sp, sp, #20
    mov r1, r0
comp_answer:
    mov r0, r4
    bl {SET_RESULT:#x}
    mov r0, #1
    pop {{r4, pc}}

comp_save:                  @ r0 a file's save image: its percentage
    push {{lr}}
    sub sp, sp, #20
    add r1, r0, #{SAVE_FLAGS & ~0xFF:#x}
    add r1, r1, #{SAVE_FLAGS & 0xFF:#x}
    str r1, [sp]
    add r1, r0, #{SAVE_ITEMS & ~0xFF:#x}
    add r1, r1, #{SAVE_ITEMS & 0xFF:#x}
    str r1, [sp, #4]
    add r1, r0, #{SAVE_BYTES & ~0xFF:#x}
    add r1, r1, #{SAVE_BYTES & 0xFF:#x}
    str r1, [sp, #8]
    add r1, r0, #{SAVE_SHORTS & ~0xFF:#x}
    add r1, r1, #{SAVE_SHORTS & 0xFF:#x}
    str r1, [sp, #12]
    add r1, r0, #{SAVE_LONGS & ~0xFF:#x}
    add r1, r1, #{SAVE_LONGS & 0xFF:#x}
    str r1, [sp, #16]
    mov r0, sp
    bl comp_calc
    add sp, sp, #20
    pop {{pc}}

comp_calc:                  @ r0 the view; r0 the percentage
    push {{r4, r5, r6, lr}}
    mov r4, r0
    mov r5, #0
    ldr r0, [r4, #12]
    ldrh r0, [r0, #{MAP_SPOTS * 2}]
    mov r1, #0
    mov r2, #1
comp_ch:                    @ chapter n cleared: spot n + 1 open (bit n)
    mov r3, r0, lsr r2
    tst r3, #1
    addne r1, r1, #1
    add r2, r2, #1
    cmp r2, #8
    blt comp_ch
    ldr r0, [r4, #8]
    ldrb r0, [r0]           @ the game cleared: the final chapter
    cmp r0, #0
    addne r1, r1, #1
{add("chapters", "r1")}
    mov r0, #80
    mov r1, #32
    bl comp_words
{add("bag items", "r1")}
    mov r0, #0
    mov r1, #32
    bl comp_words
{add("gear", "r1")}
    mov r0, #48
    mov r1, #16
    bl comp_words
{add("recipes", "r1")}
    mov r0, #64
    mov r1, #16
    bl comp_words
{add("key items", "r1")}
    ldr r6, [r4]            @ chests: their flags' bits
    adr r2, comp_chests
    mov r1, #0
    mov r3, #{len(flags)}
comp_chest:
    ldrh r0, [r2], #2
    ldrb r12, [r6, r0, lsr #3]
    and r0, r0, #7
    mov r12, r12, lsr r0
    tst r12, #1
    addne r1, r1, #1
    subs r3, r3, #1
    bne comp_chest
{add("chests", "r1")}
    ldr r6, [r4, #4]
    add r6, r6, #{112 * 4:#x}   @ the cards: a count each, then each special version's
    mov r1, #0
    mov r3, #0
comp_card:
    ldrb r0, [r6, r3]
    add r12, r6, #112
    ldrb r12, [r12, r3]
    orrs r0, r0, r12
    addne r1, r1, #1
    add r3, r3, #1
    cmp r3, #112
    blt comp_card
{add("cards", "r1")}
    ldrb r0, [r6, #{TOWER_CARD}]
    add r12, r6, #112
    ldrb r12, [r12, #{TOWER_CARD}]
    orrs r0, r0, r12
    addne r5, r5, #{5 << 16:#x}
    ldr r0, [r4, #16]
    ldr r0, [r0, #{MANSION_GROUP * 8}]
    tst r0, #{1 << MANSION_BIT}
    addne r5, r5, #{5 << 16:#x}
    mov r0, r5, lsr #16
    cmp r0, #100
    movhi r0, #100
    pop {{r4, r5, r6, pc}}

comp_words:                 @ r0 the first item, r1 how many: r1 those whose word is nonzero
    ldr r2, [r4, #4]
    add r2, r2, r0, lsl #2
    mov r3, #0
comp_w:
    ldr r12, [r2], #4
    cmp r12, #0
    addne r3, r3, #1
    subs r1, r1, #1
    bne comp_w
    mov r1, r3
    bx lr

comp_add:                   @ r1 found of r0, r2 the share each, r3 the weight (all found): into r5
    cmp r1, r0
    movhs r1, r3
    mullo r1, r2, r1
    add r5, r5, r1
    bx lr

.ltorg
comp_chests:
.short {", ".join(str(f) for f in flags)}
.align 2
"""


def patch_map_chests(b):
    """The world map, after patch_map: once a chapter is cleared, standing on its spot shows
    "Chests Remaining: n" at the bottom right of the top screen. UpScrSet(spot), which draws the
    spot's picture, is now UpScrBase; every call goes to the new UpScrSet, which takes down the old
    count and asks chest_src for the new one. The count goes when a place is entered (MapGo), and
    StartScript forgets the handle first, since global ints outlive the map."""
    funcs, imports = scr.recs(b)
    names = [scr.rec(b, o)["name"] for o in funcs]
    up, go, start = names.index("UpScrSet"), names.index("MapGo"), names.index("StartScript")
    for f, new in ((up, b"UpScrBase"), (start, b"MapBase")):
        b[funcs[f] + 0x20:funcs[f] + 0x30] = new.ljust(16, b"\0")
    ix = script_add(b, imports=(("GetTpTouch", 1), ("MessageIC", 4), ("DeleteMessage", 1)))
    handle = CHEST_VAR
    drop = (*handle, 0x4000, 0, 0x0E, 0x101, 0x4001, 8, 0x103,     # shown: taken down
            *handle, 0x2102, ix["DeleteMessage"], 0xA000, *handle, 0x4000, 0, 0x14, 0xA000)
    assert drop[6] == 0x4001 and 6 + drop[7] == 14
    flags = SOUND_NOW_FLAGS                                         # top screen, right-aligned, no panel, no wait
    show = (*handle, 0x4003, CHEST_MSG, 0x8000, 0, 0, 0x601A, 1, *imm(CHEST_Y),
            0x4003, flags & 0xFFFF, flags >> 16, 0, 0, 0x2102, ix["MessageIC"], 0x14, 0xA000)
    head = (0x109, 2, 1, 0xA000,                                    # 0: local 1
            0x601A, 0, 0x2002, up, 0xA000) + drop + (               # the picture, as before
            0x601A, 1, 0x4001, CHEST_MARK, 0x601A, 0, 0x07, 0x2102, ix["GetTpTouch"], 0x14, 0xA000,
            0x601A, 1, *imm(-1), 0x0E, 0x101, 0x4001)               # chests left (not -1): shown
    at = len(head) - 1
    code = head + (len(show) + 3, 0x103) + show + (0x4000, 0, 0x108)
    assert code[at + code[at + 1]:at + code[at + 1] + 3] == (0x4000, 0, 0x108)
    # the completion percentage (once the game is cleared): the touch screen's bottom right, from the
    # map's start; down while a place is entered, and while the shop or tent has the screen
    cdrop = (*COMP_VAR, 0x4000, 0, 0x0E, 0x101, 0x4001, 8, 0x103,
             *COMP_VAR, 0x2102, ix["DeleteMessage"], 0xA000, *COMP_VAR, 0x4000, 0, 0x14, 0xA000)
    cshow = (*COMP_VAR, 0x4003, COMP_MSG, 0x8000, 0, 0, 0x601A, 1, *imm(COMP_Y),
             0x4003, COMP_FLAGS & 0xFFFF, COMP_FLAGS >> 16, 0, 0, 0x2102, ix["MessageIC"], 0x14, 0xA000)
    chead = (0x109, 2, 1, 0xA000) + cdrop + (
             0x601A, 1, 0x4001, COMP_MARK, 0x2102, ix["GetTpTouch"], 0x14, 0xA000,
             0x601A, 1, *imm(-1), 0x0E, 0x101, 0x4001)
    cat = len(chead) - 1
    comp = chead + (len(cshow) + 3, 0x103) + cshow + (0x4000, 0, 0x108)
    assert comp[cat + comp[cat + 1]:cat + comp[cat + 1] + 3] == (0x4000, 0, 0x108)
    shop, tent, ask = names.index("ShopIn"), names.index("TentIn"), names.index("MapKettei")   # ask: "Go to ...?" (Yes never returns)
    ix.update(script_add(b, funcs=(("CompShow", 1, comp),)))
    mapgo = drop + cdrop + (0x601A, 0, 0x2002, go, 0x108)
    begin = (*handle, 0x4000, 0, 0x14, 0xA000, *COMP_VAR, 0x4000, 0, 0x14, 0xA000,   # forget old handles
             0x4000, 0, 0x2002, ix["CompShow"], 0xA000,
             0x601A, 0, 0x601A, 1, 0x2002, start, 0x108)
    around = lambda f: cdrop + (0x601A, 0, 0x2002, f, 0xA000, 0x4000, 0, 0x2002, ix["CompShow"], 0xA000, 0x4000, 0, 0x108)
    ix.update(script_add(b, funcs=(("UpScrSet", 1, code), ("MapGoChests", 1, mapgo), ("StartScript", 2, begin),
                                   ("ShopComp", 1, around(shop)), ("TentComp", 1, around(tent)),
                                   ("AskComp", 1, around(ask)))))
    funcs, _ = scr.recs(b)
    new = {up: ix["UpScrSet"], go: ix["MapGoChests"], shop: ix["ShopComp"], tent: ix["TentComp"], ask: ix["AskComp"]}
    n = 0
    for f in range(len(funcs)):
        if f in (ix["UpScrSet"], ix["MapGoChests"], ix["StartScript"], ix["ShopComp"], ix["TentComp"], ix["AskComp"]):
            continue
        r = scr.rec(b, funcs[f])
        for a, x in scr.walk(b, r):
            if x[0] == "call" and x[1] == 0x2002 and x[2] in new:
                assert struct.unpack_from("<2H", b, a) == (0x2002, x[2])
                struct.pack_into("<H", b, a + 2, new[x[2]])
                n += 1
    assert n >= 9, n
    return b


def patch_map(script):
    """World map, script 2609: test every open spot each frame, and mark those tests for the hook."""
    b = bytearray(script)
    funcs, _ = scr.recs(b)
    main, chk = scr.rec(b, funcs[0]), scr.rec(b, funcs[3])
    assert (main["name"], chk["name"]) == ("StartScript", "TouchChk")
    at = main["code"] + 2100 * 2                    # the jump past them with no touch
    assert struct.unpack_from("<2H", b, at) == (0x4001, 171)
    struct.pack_into("<H", b, at + 2, 3)            # jumps count from their own push: 3 falls through
    at = chk["code"] + 11 * 2                       # IsMobTouchSize(spot, 16, 16)
    assert struct.unpack_from("<4H", b, at) == (0x4000, 16, 0x4000, 16)
    struct.pack_into("<H", b, at + 2, MAP_MARK)
    return bytes(patch_map_chests(b))


def patch_kin(script):
    """Kin Flight, script 2497: flapping needs no mashing, so its rapid-tap prompt spawns off screen."""
    b = bytearray(script)
    funcs, _ = scr.recs(b)
    fly = scr.rec(b, funcs[1])
    assert fly["name"] == "KinFly"
    at = fly["code"] + 241 * 2                      # SpawnObj(0, 0, 22, 0, 1920, 128, 0)
    assert struct.unpack_from("<4H", b, at) == (0x4001, 1920, 0x4001, 128)
    struct.pack_into("<H", b, at + 6, 2000)
    return bytes(b)
