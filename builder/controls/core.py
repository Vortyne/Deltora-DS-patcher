"""The code block, its install into the ARM9, shared hooks and the script helpers.

Part of the controls namespace (see __init__.py): names from every part are shared."""

RAM = 0x02000000
STEER_CODE, STEER_ROOM = 0x02212748, 252   # LaserWindowSub, unused
STRIP_FIND, STRIP_FIND_END = 0x0204CB30, 0x0204CBDC   # FUN_0204cb30: a free run of text strips (16, 2 KB each)
STRIP_MASK, PANIC = 0x0204CBDC, 0x020082DC            # the strips' in-use mask for the text's screen; the game's halt
PROMPT_RESET, PROMPT_RESET_ROOM = 0x02212CA8, 24
EDGE_LEFT, EDGE_RIGHT, EDGE_TOP, EDGE_BOTTOM = 6, 249, 8, 188    # past where the screen would scroll
CAMEL_SPOT = 34, 92            # where the camp's arrow sits on the Muddlet
REACH, REACH_ROOM = 0x02210DD0, 0xA0         # the old shared block's free space
MOB_DISTANCE = 0x02087874   # GetMobDistance's measure: Lief's feet to their point, 4.12 fixed
GEAR_BONUS = 0x02090970         # (unused, slot, item): a gear slot's health bonus, as FUN_02090ABC adds it
ON_FLOOR_A, ON_FLOOR_B, HAS_GEAR = 0x020870E8, 0x02087100, 0x0209141C
SOUP_SITE, SOUP_END_SITE = 0x020A0FA4, 0x020A3354  # its timer (7) started; that timer run out
INFO_FN = 0x02033824            # (message, bank, x, y): a message window; its handle at the screen's +0x64
MSG_CLOSE = 0x0203379C          # a message window closed (push {r4, lr} first)
SCRIPT_BYTES = 0x020C92B4       # the scripts' saved globals: their byte array (byte 0: the game cleared, set by the ending)
MEM_SAVE_AT = 0x1F30            # between the options and the kill counts, untouched by the game
HEAP_ALLOC_SITE, EXP_ALLOC = 0x020352F8, 0x0205008C    # in FUN_020352d8 (HEAP_ALLOC), every heap's allocation
POOL1, POOL2 = 0x020D413C, 0x020D4164    # the main heap; the second, which our code block shrinks
MESSAGE_CLOSE = 0x0203379C      # a message window's handle: closed, if it still is open
TOUCH_TRIG = 0x02037758         # the touch's new-press flag (+3 of TOUCH_STATE)
TOUCH_PICK, CAN_TARGET = 0x02096CD4, 0x02087800
SOUP_SWITCH_SITE = 0x02090544   # SET_COSTUME: the hero coming in gets their saved biorhythm
SET_TIMER, SET_BIO = 0x020A32E4, 0x02094938
SCRIPT_LONGS = 0x020C92CC      # the scripts' saved globals: their 64-bit array (IsFlagChk's groups)
SCRIPT_SHORTS = 0x020C92BC     # the scripts' saved globals: their short array
SWING, SWING_ROOM = 0x022151C0, 0x120          # Y with no enemy in reach: a swing the way he faces
COMBO_AT = 0x436 * 4        # player: which hit of the combo comes next
HERO_NAMES = "Lief", "Barda", "Jasmine"
TOP_TEXT = 2                # Text_Create's mode for the top screen (the game's own text all uses 0, the bottom)
NO_DROP, NO_DROP_9 = 0x0208B5E8, 0x0202A50C            # the roll's own checks for no drop at all
DROP_SAVE, FIND_TASK = 0x0207CC38, 0x020A5440          # how the roll finds the save data
BAG_SHOWN = 0x020A30F0           # player+0xF18 bit 1: the field shows the bag icon
BAG_DRAW, BAG_DRAW_SITE = 0x0208BAA8, 0x020A30D4    # the icon's sprite drawn, at the end of its update
BAG_TAP_SITE = 0x020A2FBC        # the icon's own tap check
VOICE_STOP = 0x0208B30C
SET_COSTUME = 0x020903BC
LEAVE_QUIET, LEAVE_QUIET_ROOM = 0x02212F30, 24
LEAVE_SOUND_SITE = 0x0206C128  # the closing page starting the walk-away sound
ZOOM = 0x02065CAC              # the bag's zoom-in: from, to, amount
MESSAGE_WINDOW, MESSAGE_DONE = 0x020338C0, 0x02033788
MESSAGE_BANK, MESSAGE_BANK_NOW = 0x02033730, 0x02033758
MUSIC_PLAYERS = 0x021E63B8, 0x021E63DC   # NNS player 13 and 14 volume bytes: every music sequence
STREAM_SLOTS = 0x021E73EC      # four stream slots, 0x174 apart; +0x158 their volume
STREAM_VOLUME_SITE = 0x0205E874   # a stream starting: str r1, [r4, #0x158] with r1 0x7F
SET_RESULT = 0x02028F98
TOUCH_HELD = 0x02037748         # the touch held flag, as GetTpTouch(0) reads it
TOUCH_STATE = 0x020D4410        # the touch state: +0x12 the x while held
SPRITE_INIT, SPRITE_MAKE, SPRITE_SCALE, SPRITE_POS = 0x02033C84, 0x02033D3C, 0x020341F8, 0x02034164
SPRITE_FLAG, SPRITE_ANIM, SPRITE_GETPOS, SPRITE_DEPTH = 0x02034370, 0x02034508, 0x02034194, 0x020662B0
SPRITE_DRAW, SPRITE_FREE, SPRITE_MADE, SPRITE_SHOW = 0x0203403C, 0x02033FC8, 0x02033CFC, 0x0203466C
TOUCH, TOUCH_TRIG = 0x020D42A8, 0x02036A70
MESSAGE_FREE = 0x0203379C
COSTUME_SITE = 0x02046A20      # the script command GetCostume reading the player
PLAYER_DATA = 0x021D4A44
GET_PARTY, IN_PARTY = 0x0203A9E0, 0x02090860
BACK_INFO_ENTRY = 0x020BAA5C    # GetBackDataInfo, called only by the title script
SB_BACK_INFO = 0x02048C94
BACK_INFO = 0x020B8A70
MESSAGE_ENTRY = 0x020BA85C      # MessageC in the command table
MESSAGE_CODE, MESSAGE_ROOM = 0x022121D4, 148    # IsGlobalFlag and friends, unused
SB_MESSAGE = 0x0203E324
SET_SEQ = 0x0204ACE8     # sprite, sequence, speed, mode, start
RANGE_BUTTON, RANGE_FIRE = 0x0203ED4C, 0x0203EF10   # RangeButtonEvent: A already counts, but the touch point check after it stopped that
PROMPT_DATA = 0x021DDF34    # holds the Yes and No sprites at +0xC and +0x18
PROMPT_RESULT = 0x020C20A4
PROMPT_SPRITES = 0x0204C86C
SPRITE_SEQ = 0x0204ACE8
SOUND = 0x020D4458
PLAY_SE = 0x0203897C
TOUCH_ENTRY = 0x020BA3BC    # GetTpTouch in the command table
EFFECT_ENTRY = 0x020BA78C   # SetEffect in the command table
SET_EFFECT = 0x0203F8F8
SPAWN_SITE = 0x0203F8D4     # sb_SpawnObj, with the new object in r1
SPAWN_DONE = 0x0203F794
SCRIPT_ARG = 0x02028D34
CAMEL_EFFECT = 5408         # only loaded when the camel is in the scene
HOOKS_CODE, HOOKS_ROOM = 0x02211BE4, 292    # GetMobWYpos, LoadExitData and friends, unused
DIRECT_ENTRY, LOOP_ENTRY = 0x020BA36C, 0x020BA35C   # MobMotionDirect and its Loop form
SB_DIRECT, SB_LOOP = 0x02042B3C, 0x02042D20
SET_MOTION = 0x0203C674
START_MOTION = 0x0208D058
MOTION_LOOP = 0x0208D070
MOTION_BUSY = 0x0208D188
FIND_MOB = 0x020A5578
TP_TOUCH = 0x020429CC
BAG_X, BAG_Y = 240, 176     # bottom-right bag icon
SHARED_BASE = 0x022155C0      # moved after the cursor block; 0x02210DD0 (256 bytes) is free
INPUT_CODE, INPUT_ROOM = 0x02212320, 636    # WipeOpen/Close Main/Sub, PlayerDeadProc, unused; CARD_COL follows
INPUT_CODE_ON, INPUT_CODE_OFF = INPUT_CODE + 4, INPUT_CODE + 8
CODE = 0x02210760           # 20 KB after the largest overlay, cut from the game's memory
CODE_AREA = 0x7C00           # 31 KB: the completion percentage took the last kilobyte
ARENA_LOW = 0x02007478      # where the game keeps that start address
LIMIT = 0x02000000
ON, OFF = INPUT_CODE_ON, INPUT_CODE_OFF
PAD = 0x020D4284             # game's held buttons, including X and Y
PRESSED = 0x02037500
READ = 0x02037560
TP_ENABLED = 0x020D42A8
WORLD = 0x021E9E3C          # holds the party; +0x28 is the stage
HITLIST = 0x021E8F4C
GET_PLAYER = 0x020A5440
LIST_RESET = 0x020A492C
LIST_NEXT = 0x020A4ACC
OBJ_TYPE = 0x0208D0A8
CAN_ACT = 0x02093BC4
STAGE = WORLD + 0x28 + 0x6000
WALK_SPEED = 0x2400         # 2.25 px per frame, 4.12 fixed point
SET_MOVE = 0x02093228
DO_MOVE = 0x02093774
IS_PEAK = 0x020942D8
SPECIAL_SITE = 0x02097024    # the attack start, asking if the biorhythm is at its peak
STAGE_OWNER = 0x021E9E3C
ITEM_POS = 0x0208BB34          # object, sprite, out: where a bar sprite is
COPY = 0x02008D20               # source, destination, bytes
ITEM_COUNT = 0x02091298        # (save, -1, item) -> how many owned
SPR_INIT, SPR_FREE, SPR_DRAW = 0x02033D3C, 0x02033FC8, 0x0203403C    # a 0x44-byte sprite object: load, free, draw
SPR_FRAME, SPR_PRIO, SPR_POS = 0x02034508, 0x020343A8, 0x02034164
DIGITS = (0x15D4, 0x15D3, 0x15D5, 0x148A)     # the bag's count digits (frames 0-9), as FUN_02066588 loads them
OBJ_FREE = 0x02033FC8
SB_TOUCH_SIZE = 0x020428C0
TOUCH_SIZE_ENTRY = 0x020BA3AC   # IsMobTouchSize in the command table
SET_RESULT = 0x02028F98
SPAWN_OBJECT = 0x0203BF30
GET_STAGE = 0x0202CC30
TILE_AT = 0x02082748
MENU = 0x021E7FD0            # bag menu; null until first opened, state 13 when closed

def _walktab():
    rows = []
    for y in (-1, 0, 1):
        for x in (-1, 0, 1):
            if x == 0 and y == 0:
                rows.append(".short 0, 0, 0")
                continue
            a = math.atan2(y, x)
            rows.append(f".short {(int(a / (2 * math.pi) * 65536) - 0x4000) & 0xFFFF}, "
                        f"{int(math.cos(a) * WALK_SPEED)}, {int(math.sin(a) * WALK_SPEED)}")
    return chr(10).join(rows)


WALKTAB = _walktab() + chr(10) + ".short 0"

# vars, relative to r9
ACTIVE, VX, VY, MODE, CNT, FX, FY, PREV, CAMX, CAMY, CTRL, PLAYER, TAP, MOVE_X, MOVE_Y, CAMP, CAMP_SEL, LIVE, TAP2, WAIT, CAMP_KIND, CAMEL, HERO, POINTER, AX, AY, PEND, ARM, HOLD_ID, HOLD_OBJ, HOLD_MOTION, SIGN, SE_REQ, POSE_REQ, SEL_MOB, RETRY, RETRY_MOB, RETRY_N, GLIDE, GLIDE_X, GLIDE_Y, PROMPT_ON, PROMPT_SEL, PROMPT_SHOWN, TITLE, TITLE_SEL, TITLE_N, SAVE_SEL, ANY_KEY, MAP, SHOP_SEL, SHOP_SHOWN, MIX = range(0, 212, 4)
VARS_SIZE = 212
SRC = f"""
vt_pressed:
    push {{r4, r5, r6, r7, r8, r9, r10, r11, lr}}
    sub sp, sp, #16
    ldr r9, =vars
    bl {INPUT_CODE:#x}
    add sp, sp, #16
    str r0, [r9, #{ACTIVE}]
    cmp r0, #0
    popne {{r4, r5, r6, r7, r8, r9, r10, r11, pc}}
    pop {{r4, r5, r6, r7, r8, r9, r10, r11, lr}}
    push {{r3, lr}}
    b {PRESSED + 4:#x}

vt_read:
    ldr r2, =vars
    ldr r3, [r2, #{ACTIVE}]
    cmp r3, #0
    beq read_real
    ldr r3, [r2, #{VX}]
    strh r3, [r0]
    ldr r3, [r2, #{VY}]
    strh r3, [r1]
    mov r0, #1
    bx lr
read_real:
    push {{r3, r4, r5, lr}}
    b {READ + 4:#x}

walk:
    push {{r0, r1, r2, r3, r4, lr}}
    ldr r4, =vars
    ldr r1, [r4, #{CAMP}]
    cmp r1, #0
    bne walk_done
    ldr r1, [r4, #{CTRL}]
    cmp r1, #1
    bne walk_done
    ldr r1, [r4, #{PLAYER}]
    cmp r1, r0
    bne walk_done
    ldr r1, [r4, #{MODE}]
    cmp r1, #0
    bne walk_done
    ldr r1, [r0, #0x714]    @ no walking or turning until a basic attack ends
    sub r1, r1, #9
    cmp r1, #5
    bls walk_done
    cmp r1, #0x14
    beq walk_done
    ldr r1, ={PAD:#x}
    ldrh r1, [r1]
    mov r2, #4
    tst r1, #0x20
    subne r2, r2, #1
    tst r1, #0x10
    addne r2, r2, #1
    tst r1, #0x40
    subne r2, r2, #3
    tst r1, #0x80
    addne r2, r2, #3
    cmp r2, #4
    beq walk_done
    add r2, r2, r2, lsl #1
    adr r3, walktab
    add r3, r3, r2, lsl #1
    ldrh r1, [r3]
    ldrsh r2, [r3, #2]
    ldrsh r3, [r3, #4]
    str r2, [r4, #{MOVE_X}]
    str r3, [r4, #{MOVE_Y}]
    add r4, r0, #0x2d8
    strh r1, [r4]
    mov r4, #0x8000
    ldr r12, ={PAD:#x}
    ldrh r12, [r12]
    tst r12, #2             @ B doubles the speed and limits the collision step uses
    lslne r2, r2, #1
    lslne r3, r3, #1
    lslne r4, r4, #1
    sub sp, sp, #8
    str r4, [sp]
    bl {STEER_CODE:#x}
    add sp, sp, #8
walk_done:
    pop {{r0, r1, r2, r3, r4, lr}}
    b {DO_MOVE:#x}

gate:
    push {{r4, r5, lr}}
    ldr r5, =vars
    mov r4, #0
    str r4, [r5, #{CTRL}]
    ldr r4, [r0]
    cmp r4, #0
    beq gate_done
    ldr r12, ={MENU:#x}
    ldr r12, [r12]
    cmp r12, #0
    ldrne r12, [r12, #4]
    cmpne r12, #13
    bne gate_keep
    ldr r0, ={WORLD:#x}
    bl {GET_PLAYER:#x}
    movs r4, r0
    beq gate_keep
    str r4, [r5, #{PLAYER}]
    ldr r12, [r4]
    ldr r12, [r12, #0xa0]
    blx r12
    cmp r0, #0
    bne gate_keep
    mov r0, r4
    bl {CAN_ACT:#x}
    cmp r0, #0
    moveq r0, #2
    streq r0, [r5, #{CTRL}]
    beq gate_keep
    ldr r12, [r4]
    ldr r12, [r12, #0x1f0]
    mov r0, r4
    blx r12
    cmp r0, #0
    moveq r0, #1
    movne r0, #4
    str r0, [r5, #{CTRL}]
gate_keep:
    mov r4, #1
gate_done:
    mov r0, r4
    pop {{r4, r5, pc}}

attack:
    mov r10, #112
    b scan
interact:
    mov r0, #4
    str r0, [r9, #{MODE}]
    mov r10, #0xF00         @ reach itself is checked in REACH (out of reach: 0x1000); room for TALK_LOW's penalties
scan:
    ldr r0, ={HITLIST:#x}
    mov r1, #0
    bl {LIST_RESET:#x}
    mov r11, #0
next:
    ldr r0, ={HITLIST:#x}
    mov r1, #13
    bl {LIST_NEXT:#x}
    movs r7, r0
    beq chosen
    cmp r7, r4
    beq next
    bl {OBJ_TYPE:#x}
    ldr r1, [r9, #{MODE}]   @ 4 while A talks
    cmp r1, #4
    cmpne r0, #4            @ Y attacks enemies (type 4) only
    bne next
    cmp r0, #2              @ A skips the party and enemies; type 3 is NPCs, which A talks to
    cmpne r0, r1
    beq next
    ldr r12, [r7]
    ldr r12, [r12, #0x6c]
    mov r0, r7
    add r1, sp, #4
    blx r12
    ldr r0, [sp, #4]
    ldr r1, [r9, #{CAMX}]
    rsb r0, r1, r0, asr #12
    ldr r2, [sp, #8]
    ldr r1, [r9, #{CAMY}]
    rsb r2, r1, r2, asr #12
    subs r1, r0, r5
    rsblt r1, r1, #0
    subs r3, r2, r6
    rsblt r3, r3, #0
    bl {REACH:#x}           @ r1 + r3, or A's ranking score
    cmp r1, r10
    bge next
    mov r10, r1
    mov r11, #1
    str r0, [r9, #{VX}]
    str r2, [r9, #{VY}]
    b next
chosen:
    cmp r11, #0
    beq {SWING:#x}          @ nobody in reach: Y still swings, A does nothing
    ldr r5, [r9, #{VX}]
    ldr r6, [r9, #{VY}]
    b {ON:#x}

prompt:                     @ Yes/No: runs in the text update while the prompt waits
    push {{r4, r5, r6, lr}}
    sub sp, sp, #8
    ldr r4, ={PROMPT_DATA:#x}
    ldr r5, =vars
    ldr r0, [r4, #0xC]
    cmp r0, #0
    bleq {PROMPT_RESET:#x}
    streq r0, [r5, #{PROMPT_SEL}]
    mvneq r0, #0
    streq r0, [r5, #{PROMPT_SHOWN}]
    bl {PROMPT_SPRITES:#x}
    mov r0, #1
    str r0, [r5, #{PROMPT_ON}]
    ldr r0, ={PAD:#x}
    ldrh r6, [r0, #2]
    tst r6, #0x32
    beq prompt_keys
    ldr r1, [r5, #{PROMPT_SEL}]
    tst r6, #0x30
    eorne r1, r1, #1
    tst r6, #2              @ B moves to No; only A chooses
    movne r1, #0
    str r1, [r5, #{PROMPT_SEL}]
    ldr r0, ={SOUND:#x}
    mov r1, #0
    mov r2, #103
    bl {PLAY_SE:#x}
prompt_keys:
    tst r6, #1
    beq prompt_show
    ldr r1, [r5, #{PROMPT_SEL}]
    ldr r0, ={PROMPT_RESULT:#x}
    strb r1, [r0]
    mov r0, #1
    strb r0, [r9, #8]
    cmp r1, #0
    mov r2, #100
    moveq r2, #0x65
    ldr r0, ={SOUND:#x}
    mov r1, #0
    bl {PLAY_SE:#x}
    b prompt_end
prompt_show:
    ldr r1, [r5, #{PROMPT_SEL}]
    ldr r0, [r5, #{PROMPT_SHOWN}]
    cmp r0, r1
    beq prompt_end
    str r1, [r5, #{PROMPT_SHOWN}]
    mov r3, #0
    str r3, [sp]
    cmp r1, #0              @ only the selected card animates
    movne r1, #2
    movne r2, #0x1000
    moveq r2, #0
    ldr r0, [r4, #0xC]
    bl {SPRITE_SEQ:#x}
    ldr r1, [r5, #{PROMPT_SEL}]
    cmp r1, #0
    moveq r1, #3
    moveq r2, #0x1000
    movne r1, #1
    movne r2, #0
    mov r3, #0
    str r3, [sp]
    ldr r0, [r4, #0x18]
    bl {SPRITE_SEQ:#x}
prompt_end:
    add sp, sp, #8
    pop {{r4, r5, r6, pc}}

.ltorg
walktab:
""" + WALKTAB + """
vars:
"""


def build():
    code = entext.asm(SRC, CODE)
    check_branches(code, CODE)
    data = bytearray(VARS_SIZE)
    data[FX] = 1            # dash direction before the first move
    code += bytes(data)
    assert len(code) <= LIMIT - 0x01FFFB00, len(code)
    assert len(code) % 4 == 0, len(code)
    return code


# Bag menu D-pad control. These blocks replace MobMove2, MobMoveR2, MobReTurn and
# IsMobTouch, script commands that no script or code calls.
SHARED_CODE, SHARED_ROOM = SHARED_BASE, 0x130
NEXT_ITEM, NEXT_ITEM_ROOM = 0x02210ED0, 56     # the end of the SHARED block
LIST_SYNC, LIST_SYNC_ROOM = 0x022152E0, 0x60     # the card list's D-pad cursor follows the game's slot
PLACE_CODE, PLACE_ROOM = 0x022116D0, 256    # IsMobTouch, also unused
PLACE_TABLES = PLACE_CODE + 220
GRID, WHO, BOOK = (PLACE_TABLES + i * 12 for i in range(3))
MENU_CODE, MENU_ROOM = 0x02211050, 368
ICON_SEQ, ICON_SEQ_ROOM = 0x02210C74, 72       # the end of MessageI
ICON_SETUP = (0x02065E7C, 0x02065EA4, 0x02065ECC, 0x02065EF4, 0x02065F18,
              0x02066084, 0x020660A4, 0x020660C4, 0x020660E4, 0x02066104)
MENU_PAGE = 0x02062014      # the bag's top page
AIM_SITE = 0x020889DC       # wall slides pick a direction from the touch point
TO_WORLD = 0x02081FA4
FLAG = 0x0202A50C
IN_FIELD = 0x02093B04
EVENTS = 0x021D4A44
EVENT_ON = 0x0209288C
OPEN_BAG = 0x02067148
HIDE_ICON = 0x020A1DA0
PLAY_VOICE = 0x0208B230
ITEM_HELD = 0x020A2B84
# Gellick's poison pools (mob update type 10, FUN_020742e8) set their hit area each frame from
# their sprite scale s: 3s/256 pixels square, 96x96 at full size (scale 2), while the drawn pool
# is about 64x28 there. Now s/128 wide (64) and 7s/2048 tall (28), the pool as drawn.
POOL_SIZE = (
    (0x020743FC, "asr r0, r0, #7"), (0x02074400, "mov r0, r0"), (0x02074404, "mov r0, r0"),
    (0x02074420, "rsb r0, r0, r0, lsl #3"), (0x02074424, "asr r0, r0, #11"), (0x02074428, "mov r0, r0"),
)
# At camp, every cursor move had the scene load the hero's costume and top screen portrait
# (FUN_0203d390, then 6 frames' wait). DEFER holds both until the cursor has rested
# CAMP_TAP_DELAY idle frames; a new move's SetCostume restarts the count.
COSTUME_CMD_SITE = 0x02046A74       # sb_SetCostume: bl SET_COSTUME
SUBSCREEN_PORTRAIT_SITE = 0x020483CC    # sb_SetSubScreen: bl FUN_0203d390, which then waits 6 frames
PORTRAIT_LOAD, PORTRAIT_FREE = 0x0203D390, 0x020328C4
HERO_BLOCKS, HERO_BLOCK, HERO_BIO = 0x021D4A44 + 0x1750 + 0x2C4, 0xB0, 0x74   # each hero's saved state; +0x74 is
                               # SET_COSTUME's copy of the object's +0x1054, which BIO_OF reads
MENU_SITE = 0x02061D18
MENU_ROW = (                # icons in a line: where each is placed, then its touch zone
    (0x02065E64, "mov r0, #0x24000"), (0x02065E8C, "mov r0, #0x80000"),
    (0x02065E94, "mov r0, #0x60000"), (0x02065EB4, "mov r0, #0xAE000"),
    (0x02065EBC, "mov r0, #0x60000"), (0x02065EDC, "mov r0, #0xDC000"),
    (0x02065EFC, "add r1, r4, #0x1000"), (0x02065F00, "mov r0, #0x52000"),
    (0x02065F04, "str r0, [r1, #0x234]"), (0x02065F08, "mov r0, #0x60000"),
    (0x02065F0C, "str r0, [r1, #0x238]"),
    (0x0206608C, "mov r1, #0x24000"), (0x020660AC, "mov r1, #0x80000"), (0x02066108, "mov r1, #0x52000"),
    (0x020660B0, "mov r2, #0x60000"), (0x020660CC, "mov r1, #0xAE000"),
    (0x020660D0, "mov r2, #0x60000"), (0x020660EC, "mov r1, #0xDC000"),
    (0x02066110, "mov r2, #0x60000"),
    (0x020664C8, "add r1, r6, r6, lsr #2"),     # the board, a quarter wider
    (0x02066174, "mov r1, #0x1400"), (0x02066178, "mov r2, #0x1000"),
    (0x02066188, "mov r2, #0"), (0x0206618C, "mov r1, #0x80000"),   # its cell is centred on x 0
    (0x02065F78, "add r4, r4, #0x80000"), (0x02065F7C, "str r4, [r0, #0x308]"),
    (0x02062094, "cmp r0, #0x14"), (0x0206209C, "cmp r0, #0x34"),
    (0x020620E0, "cmp r0, #0x70"), (0x020620E8, "cmp r0, #0x90"),
    (0x020621C0, "cmp r0, #0x42"), (0x020621C8, "cmp r0, #0x62"),
    (0x020620F4, "cmp r0, #0x50"), (0x020620FC, "cmp r0, #0x70"),
    (0x0206212C, "cmp r0, #0x9E"), (0x02062134, "cmp r0, #0xBE"),
    (0x02062140, "cmp r0, #0x50"), (0x02062148, "cmp r0, #0x70"),
    (0x02063C14, "mov r2, #0x67"),      # the card book: moving to an entry, the menus' cursor sound
    (0x02062178, "cmp r0, #0xCC"), (0x02062180, "cmp r0, #0xEC"),
    (0x020621D4, "cmp r0, #0x50"), (0x020621DC, "cmp r0, #0x70"),
)
DISPATCH = 0x02061C9C       # runs the current bag page
DC_FLUSH, LOAD_OBJ = 0x020070B0, 0x02004B7C     # DC_FlushRange; GX_LoadOBJ(src, offset, size)
BOOK_TAB = 0x1AC4


def shared_src():
    return f"""
    b shout
    b kill
    b draw

shout:
    push {{r4, lr}}
    mov r4, r0
    bl {MIC_READ:#x}
    ldr r1, ={PAD:#x}
    ldrh r1, [r1]
    tst r1, #0x100
    movne r1, #0x40
    addne r0, r4, #0x1200
    strne r1, [r0, #{MIC_LEVEL - 0x1200:#x}]
    pop {{r4, pc}}

kill:
    push {{lr}}
    ldr r1, =slot
    ldr r0, [r1]
    subs r0, r0, #1
    popmi {{pc}}
    mov r2, #0
    str r2, [r1]
    ldr r1, ={TEXT_BUFS:#x}  @ the bag may have cleared all text: the slot could be another's now
    ldr r2, [r1]
    ldr r1, ={TEXT_SLOTS:#x}
    ldr r1, [r1, r0, lsl #5]
    cmp r1, r2
    popne {{pc}}
    bl {TEXT_FREE:#x}
    pop {{pc}}

draw:                       @ r0 centre x, r1 top y; does nothing if already shown
    push {{r4, r5, r6, lr}}
    sub sp, sp, #16
    mov r5, r0
    mov r6, r1
    ldr r0, =slot
    ldr r0, [r0]
    cmp r0, #0
    bne {ARROW_REDRAW if ARROW_REFRESH else 'draw_end'}
    bl {FREE_SLOT:#x}
    cmn r0, #1
    beq draw_end
    mov r4, r0
    mov r0, #0x80
    bl {ALLOC:#x}
    bl {ARROW_SLOT:#x}
    ldr r1, =slot
    add r2, r4, #1
    str r2, [r1]
    ldr r1, ={TEXT_BUFS:#x}
    str r0, [r1]
    cmp r0, #0
    beq draw_end
    mov r1, #0xC
    str r1, [sp]
    mov r1, #1
    str r1, [sp, #4]
    mov r1, #0
    str r1, [sp, #8]
    adr r1, arrow
    str r1, [sp, #12]
    mov r1, r5
    mov r2, r6
    mov r3, #0
    bl {TEXT_CREATE:#x}
draw_end:
    add sp, sp, #16
    pop {{r4, r5, r6, pc}}

.ltorg
arrow:
.short {ARROW_TOKEN:#x}, 0xFFFD
slot:
.word 0
"""

# page table fields
COLS, ROWS, X0, Y0, DX, DY, GAP, AUTO, COL, ROW, RISE = range(11)


def hooks_src(var):
    return f"""
    b camp_on
    b camp_off
    b live
    b spawned
    b effect

camp_on:                    @ r4 is the camp type here
    ldr r12, ={var:#x}
    mov r1, #1
    str r1, [r12, #{CAMP}]
    mov r1, #0
    str r1, [r12, #{TAP2}]
    str r1, [r12, #{CAMEL}]
    str r1, [r12, #{POINTER}]
    str r1, [r12, #{SIGN}]
    str r1, [r12, #{SE_REQ}]
    str r1, [r12, #{POSE_REQ}]
    str r1, [r12, #{SEL_MOB}]
    str r1, [r12, #{RETRY}]
    str r4, [r12, #{CAMP_KIND}]
    ldr r1, [r12, #{PLAYER}]
    ldr r1, [r1, #0x81C]
    cmp r1, #2
    movhi r1, #0
    str r1, [r12, #{CAMP_SEL}]
    str r1, [r12, #{HERO}]
    b {CAMP_MOVE + 4:#x}    @ notes a Lief-only camp, then CAMP_KEEP

camp_off:
    push {{r0, lr}}
    ldr r12, ={var:#x}
    mov r1, #0
    str r1, [r12, #{CAMP}]
    str r1, [r12, #{HOLD_OBJ}]
    bl {DEFER + 8:#x}       @ held portrait files, the menu arrow and the X prompt
    pop {{r0, lr}}
    b {CAMP_KEEP + 4:#x}

live:
    push {{r0, lr}}
    ldr r12, ={var:#x}
    str r12, [r12, #{LIVE}]
    bl {POSE_CODE:#x}
    pop {{r0, lr}}
    b {OPT_CODE + 24:#x}     @ the options can answer the title script; otherwise the touch read

spawned:                    @ the scene's last spawn is its green arrow
    ldr r12, ={var:#x}
    ldr r3, [r12, #{CAMP}]
    cmp r3, #0
    ldrne r3, [r12, #{POINTER}]
    strne r3, [r12, #{SIGN}]    @ the spawn before it is the Save sign
    strne r1, [r12, #{POINTER}]
    ldr r12, ={MAP_STATE:#x}    @ a new scene: the world map's old arrow is gone
    mov r3, #0
    str r3, [r12, #{MAP_SEL}]
    str r3, [r12, #{MAP_CHOSEN}]
    str r3, [r12, #{MAP_POINTER}]
    b {TITLE_GLOW:#x}

effect:
    push {{r0, lr}}
    ldr r12, ={var:#x}
    ldr r1, [r12, #{CAMP}]
    cmp r1, #0
    beq effect_end
    mov r1, #1
    bl {SCRIPT_ARG:#x}
    ldr r1, ={CAMEL_EFFECT:#x}
    cmp r0, r1
    ldreq r12, ={var:#x}
    moveq r1, #1
    streq r1, [r12, #{CAMEL}]
effect_end:
    pop {{r0, lr}}
    b {SET_EFFECT:#x}

.ltorg
"""


def message_src(var):
    return f"""
message:                    @ the title's first message: its screen takes any button
    push {{r4, lr}}
    mov r4, r0
    mov r1, #1
    bl {SCRIPT_ARG:#x}
    cmp r0, #120
    bne message_on
    mov r0, r4
    mov r1, #0
    bl {SCRIPT_ARG:#x}
    cmp r0, #0
    bne message_on
    ldr r12, ={var:#x}
    mov r0, #1
    str r0, [r12, #{ANY_KEY}]
message_on:
    mov r0, r4
    pop {{r4, lr}}
    b {SB_MESSAGE:#x}

.ltorg
"""


def check_branches(blob, addr):
    """Keystone turns a conditional call to a forward label into a branch to itself."""
    for i in range(0, len(blob) - 3, 4):
        word = struct.unpack_from("<I", blob, i)[0]
        assert word & 0x0FFFFFFF not in (0x0AFFFFFE, 0x0BFFFFFE) or word >> 28 == 15, hex(addr + i)


def script_add(b, imports=(), strings=(), funcs=()):
    """Append import, string and function records to a script, with new tables after them.
    imports: (name, argument count); funcs: (name, argument count, code words).
    Returns the new indexes. Records and tables are found through absolute offsets, so the old
    tables are just left unused."""
    F, I = scr.recs(b)
    ns, st = struct.unpack_from("<II", b, 0x14)
    S = [struct.unpack_from("<I", b, st + 4 * i)[0] for i in range(ns)]
    names = [scr.rec(b, o)["name"] for o in I]

    def put(data):
        b.extend(bytes(-len(b) % 16))
        b.extend(data)
        return len(b) - len(data)

    def types(n):
        t = struct.pack(f"<{n + 1}H", *[2] * n, 0xFFFF)
        return t + bytes(-len(t) % 16)

    out = {}
    for name, n in imports:
        if name not in names:
            I.append(put(struct.pack("<IHHIIIIII", 0x20, 2, n, 0x30, 0, 0, 1, 0, 0) + name.encode().ljust(16, b"\0") + types(n)))
            names.append(name)
        out[name] = names.index(name)
    for s in strings:
        S.append(put(s.encode().ljust(16, b"\0")))
        out[s] = len(S) - 1
    for name, n, code in funcs:
        t = types(n)
        F.append(put(struct.pack("<IHHIIIIII", 0x20, 2, n, 0x30, 0x30 + len(t), len(code), 1, 0, 0) + name.encode().ljust(16, b"\0") + t + struct.pack(f"<{len(code)}H", *code)))
        out[name] = len(F) - 1
    b.extend(bytes(-len(b) % 4))
    tables = []
    for t in (F, I, S):
        tables.append(len(b))
        b.extend(struct.pack(f"<{len(t)}I", *t))
    struct.pack_into("<HHIIII", b, 8, len(F), len(I), tables[0], tables[1], len(S), tables[2])
    return out


def imm(v):
    return (0x4000, v) if 0 <= v < 128 else (0x4001, v & 0xFFFF)


def install(arm9, extra=()):
    """Return a longer ARM9 with the hooks and a third autoload block."""
    b = bytearray(arm9)
    code = build()
    p = b.find(bytes.fromhex("21 06 c0 de de c0 06 21"))
    lst, lst_end, src = struct.unpack_from("<III", b, p - 0x1C)
    table = bytes(b[lst - RAM:lst_end - RAM])
    new = lst - RAM
    assert new == len(b) - len(table)
    end = new + CODE_AREA
    tail = table + struct.pack("<III", CODE, CODE_AREA, 0)
    out = b[:new] + code.ljust(CODE_AREA, bytes(1)) + tail
    assert struct.unpack_from("<I", out, ARENA_LOW - RAM)[0] == CODE
    struct.pack_into("<I", out, ARENA_LOW - RAM, CODE + CODE_AREA)
    home = lambda a: a - CODE + new if CODE <= a < CODE + CODE_AREA else a - RAM
    struct.pack_into("<II", out, p - 0x1C, RAM + end, RAM + end + len(tail))
    read = code.index(entext.asm("ldr r3, [r2, #0]", 0)) - 4
    out[PRESSED - RAM:PRESSED - RAM + 4] = entext.asm(f"b {CODE:#x}", PRESSED)
    out[READ - RAM:READ - RAM + 4] = entext.asm(f"b {CODE + read:#x}", READ)
    walk = code.index(entext.asm("push {r0, r1, r2, r3, r4, lr}", 0))
    out[WALK_SITE - RAM:WALK_SITE - RAM + 4] = entext.asm(f"bl {CODE + walk:#x}", WALK_SITE)
    gate = code.index(entext.asm("push {r4, r5, lr}", 0))
    out[GATE_SITE - RAM:GATE_SITE - RAM + 4] = entext.asm(f"bl {CODE + gate:#x}", GATE_SITE)
    out[MIC_SITE - RAM:MIC_SITE - RAM + 4] = entext.asm(f"bl {SHOUT:#x}", MIC_SITE)
    out[CAP_SITE - RAM:CAP_SITE - RAM + 4] = entext.asm(f"bl {CAP:#x}", CAP_SITE)
    var = CODE + len(code) - VARS_SIZE
    card_slots, n_slots = cardinfo.slots(drops.enemies())
    cards = cards_src(card_slots, n_slots)
    kills = CARDS_CODE + len(entext.asm(cards, CARDS_CODE)) - kill_size(n_slots)     # the block ends with them
    seen = kills + 2 * n_slots
    attack = CODE + code.index(entext.asm("mov r10, #112", 0))
    camp = CAMP_CODE
    assert code.count(entext.asm("push {r4, r5, r6, lr}", 0)) == 1
    prompt = CODE + code.index(entext.asm("push {r4, r5, r6, lr}", 0))
    for site in PROMPT_SITES:
        out[site - RAM:site - RAM + 4] = entext.asm(f"bl {prompt:#x}", site)
    out[CAMP_ON_SITE - RAM:CAMP_ON_SITE - RAM + 4] = entext.asm(f"bl {HOOKS_CODE:#x}", CAMP_ON_SITE)
    out[CAMP_OFF_SITE - RAM:CAMP_OFF_SITE - RAM + 4] = entext.asm(f"bl {HOOKS_CODE + 4:#x}", CAMP_OFF_SITE)
    struct.pack_into("<I", out, TOUCH_ENTRY - RAM, HOOKS_CODE + 8)
    struct.pack_into("<I", out, TOUCH_SIZE_ENTRY - RAM, MAP_TOUCH)
    out[SPAWN_SITE - RAM:SPAWN_SITE - RAM + 4] = entext.asm(f"bl {HOOKS_CODE + 12:#x}", SPAWN_SITE)
    struct.pack_into("<I", out, EFFECT_ENTRY - RAM, HOOKS_CODE + 16)
    struct.pack_into("<I", out, BACK_INFO_ENTRY - RAM, TITLE_CODE + 4)
    struct.pack_into("<I", out, MESSAGE_ENTRY - RAM, MESSAGE_CODE)
    out[SAVE_SITE - RAM:SAVE_SITE - RAM + 4] = entext.asm(f"bl {SAVE_CODE:#x}", SAVE_SITE)
    out[RANGE_BUTTON - RAM:RANGE_BUTTON - RAM + 4] = entext.asm(f"b {RANGE_FIRE:#x}", RANGE_BUTTON)
    out[TEXT_OAM_SITE - RAM:TEXT_OAM_SITE - RAM + 4] = entext.asm(f"bl {ARROW_ONLY:#x}", TEXT_OAM_SITE)
    # Text strips take sprite VRAM from the top down. Their area (bottom screen 0x8000 + strip * 0x800,
    # top 0x18000 + ...) is not reserved in the sprite allocator (FUN_0204f634), which fills from 0
    # up: once VRAM is fragmented, a big sprite such as the Start menu's board (12 KB) spills past
    # 0x8000 into strip 0, and the two overwrite each other (a chunk of the board missing, or the
    # menu arrow garbled after battles). From strip 15 down, they meet only when VRAM is truly full.
    # Exactly n free strips are asked for (the old search wanted one more than it marked).
    s = STRIP_FIND - RAM
    assert out[s:s + 8] == entext.asm("push {r4, r5, r6, r7, r8, sb, sl, lr}\nmov r7, r1", STRIP_FIND)
    strip = entext.asm(f"""
    push {{r4, lr}}
    mov r4, r1              @ the strips wanted
    bl {STRIP_MASK:#x}      @ r0 the text: its screen's mask
    ldr r0, [r0]
    cmp r4, #1
    movlt r4, #1
    mov r2, #1
    lsl r2, r2, r4
    sub r2, r2, #1          @ n bits
    rsb r1, r4, #16         @ the highest start first
strip_try:
    cmp r1, #0
    blt strip_none
    tst r0, r2, lsl r1
    moveq r0, r1
    popeq {{r4, pc}}
    sub r1, r1, #1
    b strip_try
strip_none:
    bl {PANIC:#x}
    mvn r0, #0
    pop {{r4, pc}}
""", STRIP_FIND)
    assert len(strip) <= STRIP_FIND_END - STRIP_FIND, len(strip)
    out[s:s + len(strip)] = strip
    out[DELETE_SITE - RAM:DELETE_SITE - RAM + 4] = entext.asm(f"bl {DELETE_ASK:#x}", DELETE_SITE)
    out[SAVE_HERO_SITE - RAM:SAVE_HERO_SITE - RAM + 4] = entext.asm(f"bl {CAMP_KEEP + 8:#x}", SAVE_HERO_SITE)
    out[COSTUME_SITE - RAM:COSTUME_SITE - RAM + 4] = entext.asm(f"bl {CAMP_KEEP + 12:#x}", COSTUME_SITE)
    out[LEAVE_SOUND_SITE - RAM:LEAVE_SOUND_SITE - RAM + 4] = entext.asm(f"bl {LEAVE_QUIET:#x}", LEAVE_SOUND_SITE)
    for site in GOLD_VIEW_SITES:
        assert out[site - RAM:site - RAM + 4] == entext.asm(f"bl {CARD_COUNT:#x}", site), hex(site)
        out[site - RAM:site - RAM + 4] = entext.asm(f"bl {CARDS_CODE + 28:#x}", site)
    assert out[GOLD_DROP_SITE - RAM:GOLD_DROP_SITE - RAM + 8] == entext.asm("cmp r6, #0\nbne #0x28", 0)
    out[GOLD_DROP_SITE - RAM:GOLD_DROP_SITE - RAM + 4] = entext.asm(f"b {GOLD_DROP_SITE + 0x28:#x}", GOLD_DROP_SITE)
    at = SAVE_SHOWN_AT - RAM            # mov r8, #0 / 3 frame calls / add, cmp #90, blo: now until a press
    assert out[at:at + 4] == entext.asm("mov r8, #0", 0) and out[at + 24:at + 28] == entext.asm("cmp r8, #0x5a", 0)
    out[at:at + 4] = entext.asm(f"bl {MEM_LOG + 4:#x}", SAVE_SHOWN_AT)   # the memory log, then CARDS_CODE + 8
    out[HEAP_ALLOC_SITE - RAM:HEAP_ALLOC_SITE - RAM + 4] = entext.asm(f"bl {MEM_LOG:#x}", HEAP_ALLOC_SITE)    # writes the kill counts, then mvn r8, #0
    for site, was, entry in ((KILL_ROLL_SITE, DROP_ROLL, 0), (LOAD_RESULT_SITE, LOAD_RESULT, 4), (CARD_TEXT_SITE, CARD_TEXT, 12)):
        assert out[site - RAM:site - RAM + 4] == entext.asm(f"bl {was:#x}", site), hex(site)
        out[site - RAM:site - RAM + 4] = entext.asm(f"bl {CARDS_CODE + entry:#x}", site)
    out[LOAD_RESULT_SITE - RAM:LOAD_RESULT_SITE - RAM + 4] = entext.asm(f"bl {PT_CODE:#x}", LOAD_RESULT_SITE)   # play time, then the kill counts
    for site in INFO_SHOW_SITES:        # the title's file screen: a file's box, and its play time
        assert out[site - RAM:site - RAM + 4] == entext.asm(f"bl {INFO_FN:#x}", site), hex(site)
        out[site - RAM:site - RAM + 4] = entext.asm(f"bl {PT_CODE + 8:#x}", site)
    out[INFO_SHOW_SITES[2] - RAM:INFO_SHOW_SITES[2] - RAM + 4] = entext.asm(f"bl {TOWER_NAME_CODE:#x}", INFO_SHOW_SITES[2])   # camp + 0xF
    assert out[LOC_SITE - RAM:LOC_SITE - RAM + 4] == entext.asm(f"bl {UNKNOWN_SHOW:#x}", LOC_SITE)   # the "??????" text
    out[LOC_SITE - RAM:LOC_SITE - RAM + 4] = entext.asm(f"bl {LOC_CODE:#x}", LOC_SITE)
    assert out[MSG_CLOSE - RAM:MSG_CLOSE - RAM + 4] == entext.asm("push {r4, lr}", 0)
    out[MSG_CLOSE - RAM:MSG_CLOSE - RAM + 4] = entext.asm(f"b {PT_CODE + 12:#x}", MSG_CLOSE)
    assert out[CARD_FREE - RAM:CARD_FREE - RAM + 4] == entext.asm("push {r4, lr}", 0)
    out[CARD_FREE - RAM:CARD_FREE - RAM + 4] = entext.asm(f"b {CARDS_CODE + 16:#x}", CARD_FREE)
    for site, was, to in ((HEX_SITE, f"bl {HEX_TARGET:#x}", f"bl {HEX_CODE:#x}"),
                          (HEART_CUR_SITE, f"bl {HP_OF:#x}", f"bl {CAMP_HEARTS:#x}"),
                          (HEART_MAX_SITE, "blx r8", f"bl {CAMP_HEARTS + 4:#x}"),
                          (SPIKE_A_SITE, f"bl {ON_FLOOR_A:#x}", f"bl {SPIKE_ATTACK:#x}"),
                          (SPIKE_B_SITE, f"bl {ON_FLOOR_B:#x}", f"bl {SPIKE_ATTACK + 4:#x}"),
                          (SOUP_SITE, f"bl {SET_TIMER:#x}", f"bl {BIO_KEEP + 4:#x}"),
                          (SOUP_SWITCH_SITE, f"bl {SET_BIO:#x}", f"bl {BIO_KEEP + 8:#x}"),
                          (PICK_SITE, f"bl {TOUCH_PICK:#x}", f"bl {PICK_CODE:#x}"),
                          (SCROLL_EDGE_SITE, "ldr r3, [r0, #0x278]", f"bl {SCROLL_EDGE:#x}"),
                          *SCROLL_RIGHT_SITES,
                          (SOUP_END_SITE, f"bl {SET_BIO:#x}", f"bl {BIO_KEEP:#x}"),
                          (CARD_SET_SITE, "strb r7, [r0, #0x9fc]", f"bl {CARD_ADDED:#x}"),
                          (CARD_ADD_SITE, "strb r4, [r2, r1]", f"bl {CARD_ADDED + 8:#x}")):
        assert out[site - RAM:site - RAM + 4] == entext.asm(was, site), hex(site)
        out[site - RAM:site - RAM + 4] = entext.asm(to, site)
    out[at + 20:at + 32] = entext.asm(f"bl {SAVE_WAIT:#x}\ncmp r0, #0\nbeq {SAVE_SHOWN_AT + 4:#x}", SAVE_SHOWN_AT + 20)
    for site, was, to in ((FS_MAKE_SITE, "bl #0x2034b00", f"bl {FS_CODE:#x}"),     # Final Slash's red circle
                          (FX_TIMER_SITE, "sub r1, r1, #1", f"bl {FS_CODE + 4:#x}"),
                          (FX_COUNT_SITE, "add r0, r0, #1", f"bl {FS_CODE + 8:#x}"),
                          (FS_TICK_SITE, "add r4, r0, #1", f"bl {FS_CODE + 12:#x}"), *FS_SLIDES):
        assert out[site - RAM:site - RAM + 4] == entext.asm(was, site), hex(site)
        out[site - RAM:site - RAM + 4] = entext.asm(to, site)
    w = SAVE_WRITE_AT - RAM             # the save thread: the write waits for the hearts to settle
    assert out[w - 8:w] == entext.asm("cmp r8, #0x3c\nadd r8, r8, #1", SAVE_WRITE_AT - 8)
    assert out[w:w + 4] == entext.asm(f"bls {SAVE_WRITE_SKIP:#x}", SAVE_WRITE_AT)
    out[w:w + 4] = entext.asm(f"bl {SAVE_HOLD:#x}", SAVE_WRITE_AT)
    assert out[SAVE_TAIL_AT - RAM:SAVE_TAIL_AT - RAM + 4] == entext.asm("ldr r4, [pc, #0x30]", 0)
    out[SAVE_TAIL_AT - RAM:SAVE_TAIL_AT - RAM + 4] = entext.asm(f"b {SAVE_TAIL_AT + 0x24:#x}", SAVE_TAIL_AT)   # to mov r0, #1
    out[ALERT_SITE - RAM:ALERT_SITE - RAM + 16] = entext.asm(f"bl {ALERT_CODE:#x}", ALERT_SITE) + entext.asm("mov r0, r0", 0) * 3
    out[HUD_TAP_SITE - RAM:HUD_TAP_SITE - RAM + 4] = entext.asm(f"bl {HUD_GUARD:#x}", HUD_TAP_SITE)
    out[HUD_TAP_SITE + 4 - RAM:HUD_TAP_SITE + 8 - RAM] = entext.asm(f"bl {HUD_GUARD + 12:#x}", HUD_TAP_SITE + 4)
    out[BAG_DRAW_SITE - RAM:BAG_DRAW_SITE - RAM + 4] = entext.asm(f"bl {HUD_GUARD + 4:#x}", BAG_DRAW_SITE)
    out[BAG_TAP_SITE - RAM:BAG_TAP_SITE - RAM + 4] = entext.asm(f"bl {HUD_GUARD + 8:#x}", BAG_TAP_SITE)
    for site, entry in ((OPT_DRAW_SITE, 4), (OPT_FREE_SITE, 8), (STREAM_VOLUME_SITE, 32)) + tuple((s, 28) for s in BIO_CUE_SITES):
        out[site - RAM:site - RAM + 4] = entext.asm(f"bl {OPT_CODE + entry:#x}", site)
    struct.pack_into("<I", out, DIRECT_ENTRY - RAM, ANIM_CODE)
    struct.pack_into("<I", out, LOOP_ENTRY - RAM, ANIM_CODE + 4)
    spans = []
    for addr, room, src in tuple(extra) + mix_src(var) + ((INPUT_CODE, INPUT_ROOM, input_src(attack, camp)),
                            (CAMP_CODE, CAMP_ROOM, camp_src()),
                            (CAMP2_CODE, CAMP2_ROOM, camp2_src()),
                            (ANIM_CODE, ANIM_ROOM, anim_src(CODE + len(code) - VARS_SIZE)),
                            (POSE_CODE, POSE_ROOM, pose_src(CODE + len(code) - VARS_SIZE)),
                            (TITLE_CODE, TITLE_ROOM, title_src(CODE + len(code) - VARS_SIZE)),
                            (MESSAGE_CODE, MESSAGE_ROOM, message_src(CODE + len(code) - VARS_SIZE)),
                            (SAVE_CODE, SAVE_ROOM, save_src(CODE + len(code) - VARS_SIZE)),
                            (HOOKS_CODE, HOOKS_ROOM, hooks_src(CODE + len(code) - VARS_SIZE)),
                            (ACTIONS_CODE, ACTIONS_ROOM, actions_src()),
                            (SHARED_CODE, SHARED_ROOM, shared_src()),
                            (TEXT_BUFS, 28, ".word 0, 0, 0, 0, 0, 0, 0"),
                            (CURSOR_CODE, CURSOR_ROOM, cursor_src()),
                            (PLACE_CODE, PLACE_ROOM, place_src(var + TAP)),
                            (STEER_CODE, STEER_ROOM, steer_src()),
                            (SHOP_CODE, SHOP_ROOM, shop_src()),
                            (SHOP_STEP, SHOP_STEP_ROOM, shop_step_src()),
                            (SHOP_BUY, SHOP_BUY_ROOM, shop_buy_src()),
                            (SHOP_YN, SHOP_YN_ROOM, shop_yn_src(var)),
                            (SHOP_YN2, SHOP_YN2_ROOM, shop_yn2_src()),
                            (SHOP_YN3, SHOP_YN3_ROOM, shop_yn3_src()),
                            (SHOP_DATA, 8, ".word 0, 0xFFFFFFFF"),
                            (SHOP_EXIT2, SHOP_DATA_ROOM - 8, shop_exit2_src()),
                            (SHOP_EXIT, SHOP_EXIT_ROOM, shop_exit_src()),
                            (SHOP_DOOR, SHOP_DOOR_ROOM, shop_door_src()),
                            (SHOP_DOOR2, SHOP_DOOR2_ROOM, shop_door2_src()),
                            (SHOP_DOOR3, SHOP_DOOR3_ROOM, shop_door3_src()),
                            (SHOP_TAP, SHOP_TAP_ROOM, shop_tap_src()),
                            (MAP_TOUCH, MAP_TOUCH_ROOM, map_touch_src()),
                            (MAP_TICK, MAP_TICK_ROOM, map_tick_src(var)),
                            (MAP_DRAW, MAP_DRAW_ROOM, map_draw_src()),
                            (MAP_SEARCH, MAP_SEARCH_ROOM, map_search_src()),
                            (MAP_ARROW, MAP_ARROW_ROOM, map_arrow_src()),
                            (MAP_SPAWN, MAP_SPAWN_ROOM, map_spawn_src()),
                            (MAP_NEAR, MAP_NEAR_ROOM, map_near_src()),
                            (MAP_ENDS, MAP_ENDS_ROOM, map_state_src()),
                            (MAP_STATE, MAP_STATE_ROOM, ".word 0, 0, 0, 0, 0"),
                            (MAP_ID, MAP_ID_ROOM, map_id_src()),
                            (SLOW_CODE, SLOW_ROOM, slow_src()),
                            (ICONS_CODE, ICONS_ROOM, icons_src()),
                            (ICON_SEQ, ICON_SEQ_ROOM, icon_seq_src()),
                            (KEY_COLS, KEY_COLS_ROOM, key_cols_src()),
                            (KEY_COLS2, 16, f"""
    cmp r7, #7
    moveq r7, #3
    movne r7, #0
    b {KEY_COLS3:#x}
"""),
                            (KEY_COLS3, 16, f"""
    strb r7, [r5, #{COL}]
    bx lr
"""),
                            (LIST_SYNC, LIST_SYNC_ROOM, list_sync_src()),
                            (MAT_NUM, MAT_DATA - MAT_NUM, mat_num_src()),    # its data follows
                            (MAT_FREE, MAT_FREE_ROOM, mat_free_src()),
                            (CARD_COL, 12, f"""
    mov r12, #1             @ the card page's cursor always rests in the middle
    strb r12, [r5, #{COL}]
    bx lr
"""),
                            (CARD, 12, ".byte 9, 1, 8, 0x1C, 0x74, 0, 0, 1, 1, 0, 0, 0"),
                            (WHO_COL, WHO_COL_ROOM, who_col_src()),
                            (ARROW_SLOT, ARROW_SLOT_ROOM, arrow_slot_src()),
                            (CAP_EDGE, CAP_EDGE_ROOM, cap_edge_src(var)),
                            (PROMPT_RESET, PROMPT_RESET_ROOM, prompt_reset_src()),
                            (DELETE_ASK, DELETE_ASK_ROOM, delete_ask_src(var)),
                            (CAMP_DATA, 8, ".word 0, 0"),
                            (CAMP_PICK, CAMP_PICK_ROOM, camp_pick_src()),
                            (CAMP_KEEP, CAMP_KEEP_ROOM, camp_keep_src(var)),
                            (ALERT_DATA, 8, ".word 0, 0"),
                            (ALERT_CODE, ALERT_ROOM, alert_src()),
                            (MIX_KEEP, 8, ".word 0, 0"),
                            (CAMP_RIM, CAMP_RIM_ROOM, camp_rim_src()),
                            (REACH, REACH_ROOM, reach_src()),
                            (REACH_MORE, REACH_MORE_ROOM, reach_more_src()),
                            (COMP_CODE, COMP_ROOM, comp_src()),
                            (DEFER, DEFER_ROOM, defer_src(var)),
                            (DEFER_TICK, DEFER_TICK_ROOM, defer_tick_src()),
                            (SHOWN_CODE, SHOWN_ROOM, shown_src()),
                            (CAMP_X, CAMP_X_ROOM, camp_x_src(var)),
                            (SWING, SWING_ROOM, swing_src()),
                            (TALK_LIMITS, 328, '.byte ' + ', '.join(map(str, talk.table()))),
                            (MIX_SOUND, MIX_SOUND_ROOM, mix_sound_src()),
                            (SAVE_WAIT, SAVE_WAIT_ROOM, save_wait_src()),
                            (TOWER_OPEN, TOWER_OPEN_ROOM, tower_open_src()),
                            (HEX_CODE, HEX_ROOM, hex_src(seen)),
                            (CARD_ADDED, CARD_ADDED_ROOM, card_added_src(seen)),
                            (CAMP_MOVE, CAMP_MOVE_ROOM, camp_move_src()),
                            (CAMP_LEAVE, CAMP_LEAVE_ROOM, camp_leave_src()),
                            (CAMP_HEARTS, CAMP_HEARTS_ROOM, camp_hearts_src(var)),
                            (SAVE_GAUGE, 4, ".word 0"),
                            (SAVE_HOLD, SAVE_HOLD_ROOM, save_hold_src()),
                            (BELT_DATA, 0x40, belt_data_src()),
                            (BELT_CODE, BELT_ROOM, belt_src()),
                            (BELT_MORE, BELT_MORE_ROOM, belt_more_src()),
                            (FS_CODE, FS_ROOM, fs_src()),
                            (PT_CODE, PT_ROOM, pt_src()),
                            (LOC_CODE, LOC_ROOM, loc_src(card_places())),
                            (TOWER_NAME_CODE, TOWER_NAME_ROOM, tower_name_src()),
                            (CHEST_CODE, CHEST_ROOM, chest_src()),
                            (ARROW_REDRAW, ARROW_REDRAW_ROOM, arrow_redraw_src()),
                            (SPIKE_ATTACK, SPIKE_ATTACK_ROOM, spike_attack_src()),
                            (BIO_KEEP, BIO_KEEP_ROOM, bio_keep_src()),
                            (QUIZ_CODE, QUIZ_ROOM, quiz_src()),
                            (PICK_CODE, PICK_ROOM, pick_src(var)),
                            (SCROLL_EDGE, SCROLL_EDGE_ROOM, scroll_edge_src()),
                            (CROP_CODE, CROP_ROOM, crop_src()),
                            (MEM_LOG, MEM_LOG_ROOM, mem_log_src()),
                            (CARDS_CODE, CARDS_ROOM, cards),
                            (CARD_STRS, CARD_STRS_ROOM, card_strs_src()),
                            (HUD_GUARD, HUD_GUARD_ROOM, hud_guard_src(var)),
                            (CAMP_BACK, CAMP_BACK_ROOM, camp_back_src()),
                            (SAVE_BACK, SAVE_BACK_ROOM, save_back_src()),
                            (LEAVE_QUIET, LEAVE_QUIET_ROOM, leave_quiet_src()),
                            (TITLE_DATA, 12, ".word 0, 0, -1"),
                            (TITLE_GLOW, TITLE_GLOW_ROOM, title_glow_src(var)),
                            (OPT_DATA, 16, ".word 0, 0, 0, 0"),
                            (OPT_CODE, OPT_ROOM, opt_src(var)),
                            (ARROW_ONLY, ARROW_ONLY_ROOM, arrow_only_src()),
                            (MAT_CODE, MAT_ROOM, mat_src()),
                            (ITEM_SLIDE, ITEM_SLIDE_ROOM, item_slide_src()),
                            (ITEM_SLIDE2, ITEM_SLIDE2_ROOM, item_slide2_src()),
                            (ITEM_SLIDE3, ITEM_SLIDE3_ROOM, item_slide3_src()),
                            (NEXT_ITEM, NEXT_ITEM_ROOM, next_item_src()),
                            (ICONS2_CODE, ICONS2_ROOM, icon_still_src()),
                            (MENU_CODE, MENU_ROOM, nav_src(var))):
        blob = entext.asm(src, addr)
        check_branches(blob, addr)
        if addr == PLACE_CODE:
            assert len(blob) <= MIX_OFF - PLACE_CODE, len(blob)
            out[home(PLACE_TABLES):home(PLACE_TABLES) + len(PLACE_DATA)] = PLACE_DATA
        assert len(blob) <= room and len(blob) % 4 == 0, (hex(addr), len(blob))
        assert addr != SHOP_CODE or blob[SHOP_ITEMS_AT:SHOP_ITEMS_AT + 4] == entext.asm("ldr r6, [r4, #0x4B8]", 0)
        assert len(blob) <= room
        out[home(addr):home(addr) + len(blob)] = blob
        spans.append((addr, len(blob)))
        print("block", hex(addr), len(blob), "of", room, "bytes")
    spans.sort()                    # blocks share rooms: what each one writes must stop short of the next
    for (a, n), (b, _) in zip(spans, spans[1:]):
        assert a + n <= b, f"block {a:#x} ({n} bytes) runs into block {b:#x}"
    out[MENU_SITE - RAM:MENU_SITE - RAM + 4] = entext.asm(f"bl {MENU_CODE:#x}", MENU_SITE)
    out[AIM_SITE - RAM:AIM_SITE - RAM + 4] = entext.asm(f"bl {MENU_CODE + 4:#x}", AIM_SITE)
    out[SPECIAL_SITE - RAM:SPECIAL_SITE - RAM + 4] = entext.asm(f"bl {ICONS_CODE + 8:#x}", SPECIAL_SITE)
    out[MIX_FRAME_SITE - RAM:MIX_FRAME_SITE - RAM + 4] = entext.asm(f"bl {MIX_ON:#x}", MIX_FRAME_SITE)
    out[MIX_END_SITE - RAM:MIX_END_SITE - RAM + 4] = entext.asm(f"bl {MIX_OFF:#x}", MIX_END_SITE)
    out[SMITH_SITE - RAM:SMITH_SITE - RAM + 4] = entext.asm(f"bl {SMITH_ON:#x}", SMITH_SITE)
    out[SHOP_ALIVE_SITE - RAM:SHOP_ALIVE_SITE - RAM + 4] = entext.asm(f"bl {SHOP_YN:#x}", SHOP_ALIVE_SITE)
    for site in ICON_SETUP:
        out[site - RAM:site - RAM + 4] = entext.asm(f"bl {ICONS2_CODE:#x}", site)
    out[COSTUME_CMD_SITE - RAM:COSTUME_CMD_SITE - RAM + 4] = entext.asm(f"bl {DEFER:#x}", COSTUME_CMD_SITE)
    out[SUBSCREEN_PORTRAIT_SITE - RAM:SUBSCREEN_PORTRAIT_SITE - RAM + 4] = entext.asm(f"bl {DEFER + 12:#x}", SUBSCREEN_PORTRAIT_SITE)
    for site, line in MENU_ROW + (SWING_ANY,) + POOL_SIZE:     # ATTACK_SPEED is off while the original pace is tested
        out[site - RAM:site - RAM + 4] = entext.asm(line, site)
    out[DISPATCH - RAM:DISPATCH - RAM + 4] = entext.asm(f"b {CURSOR_CODE:#x}", DISPATCH)
    print("controls code", len(code), "bytes, read hook at", hex(CODE + read))
    return bytes(out)
