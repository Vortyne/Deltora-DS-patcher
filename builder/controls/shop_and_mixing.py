"""Tom's Shop, Jasmine's mixing room and the smith.

Part of the controls namespace (see __init__.py): names from every part are shared."""

# Jasmine's mixing room, overlay 2: a chain of small unused commands and block ends
MIX_CODE, MIX_ROOM = 0x022129AC, 40         # CheckEffect3D
MIX_KEYS, MIX_KEYS_ROOM = 0x022122A4, 40    # IsBossBgmMode
MIX_KEY2, MIX_KEY2_ROOM = 0x02212730, 24    # the end of the ICONS block
MIX_TABLE, MIX_TABLE_ROOM = 0x02211B9C, 24  # GetMobWXpos, unused
MIX_KEEP = 0x02214700           # a mix result's jingle data, kept playing after A, freed later
MIX_SOUND, MIX_SOUND_ROOM = 0x022143A0, 0xA0      # the end of the options block's space
MIX_GRID, MIX_GRID_ROOM = 0x02211324, 40    # DepauseStrm
MIX_STEP, MIX_STEP_ROOM = 0x0221288C, 36    # SetMapPosType
MIX_TAP, MIX_TAP_ROOM = 0x022117D0, 36      # SetMobTouch
MIX_USE, MIX_USE_ROOM = 0x022113D0, 36      # SoundStopWithSaved
MIX_ON, MIX_ON_ROOM = 0x022113B4, 16        # the end of the SLOW block
MIX_OFF, MIX_OFF_ROOM = 0x02211798, 20          # the end of the PLACE code, before its tables
MIX_POT = MIX_KEY2 + 12
MIX_PROMPTS, MIX_PROMPTS_ROOM = 0x02212AD4, 28  # the end of the MAP_DRAW block
MIX_START, MIX_START_ROOM = 0x022116B8, 24  # the end of the SHOP_EXIT block
MIX_PROMPTS_OFF, MIX_RESET, MIX_ENTER = 0x021F5664, 0x021F5A74, 0x021F2B40
SHOP_CODE, SHOP_ROOM = 0x02210D18, 184      # AttachMobEventTalk, unused
SHOP_STEP, SHOP_STEP_ROOM = 0x022122CC, 84  # MobSetInvincible, unused
SHOP_BUY, SHOP_BUY_ROOM = 0x02211908, 68    # SetMobCondition, unused
SHOP_YN, SHOP_YN_ROOM = 0x02210CBC, 92      # MessageIWait, unused
SHOP_DATA, SHOP_DATA_ROOM = 0x022112FC, 40  # the end of the SHOP_TAP block
SHOP_EXIT2 = SHOP_DATA + 8
SHOP_EXIT, SHOP_EXIT_ROOM = 0x02211698, 56  # IsMobDisp, unused
SHOP_DOOR, SHOP_DOOR_ROOM = 0x02212268, 60  # SetBossBgmMode, unused
SHOP_DOOR2, SHOP_DOOR2_ROOM = 0x022117F4, 56     # AddMoney, unused
SHOP_DOOR3, SHOP_DOOR3_ROOM = 0x02211660, 56     # IsMobVisible, unused
SHOP_YN2, SHOP_YN2_ROOM = 0x02212844, 72    # LaserWideSpeedSub, unused
SHOP_YN3, SHOP_YN3_ROOM = 0x02211618, 72    # AddMobHpMax, unused
SHOP_TAP, SHOP_TAP_ROOM = 0x022112D4, 80    # PlayStrmFade, unused
MIX_BACK, MIX_BACK_ROOM = 0x02212AF0, 160     # the mixing room's return to its items
MIX_FRAME_SITE, MIX_FRAME = 0x02046710, 0x021F2C40  # sb_CallCompound's frame
MIX_END_SITE, MIX_END = 0x02046738, 0x021F2858
# Smith forging: A is a tap. The mixing room's variable holds this tag on that page.
SMITH_TAG = 0x02000000
MAT_CODE, MAT_ROOM = 0x0221194C, 304          # SetMobTagScale, unused
MAT_PULSE = MAT_CODE + 4
MAT_SHOW = 0x021FD504            # puts the selection ring on a material
SMITH_SITE, SMITH_FRAME = 0x020465A4, 0x021FAAF4    # sb_CallSmith's frame
MAT_NUM, MAT_NUM_ROOM = 0x02216360, 0x400    # the 24th kilobyte: each material's count under its icon on the smith's page
# its counts shown and 8 digit sprites (tens, ones per slot), at the end of its room: kept out of the
# assembly, as keystone miscounts branches after a .space
MAT_DATA = MAT_NUM + MAT_NUM_ROOM - 0x80
MAT_SHOWN, MAT_SLOTS, MAT_BUFS, MAT_TOKS = (MAT_DATA + i * 16 for i in range(4))   # per slot: count, text slot + 1, buffer; then 4 x 8 bytes of text
MAT_NUM_X, MAT_NUM_Y = 230, 32   # a count's centre x and top y: the text box's top right, on the name's line; 40 more each row
MAT_FREE, MAT_FREE_ROOM = 0x02215800, 0x80    # frees one slot's digit sprites, for MAT_NUM; 80 bytes after it are free
SMITH_ON, SMITH_ON_ROOM = 0x022113C4, 12            # the end of the MIX_ON block
SMITH_ON2, SMITH_ON2_ROOM = 0x022111C0, 20         # the end of the MENU block
SMITH_TAP, SMITH_TAP_ROOM = 0x022125A8, 20          # the end of the INPUT block
SMITH_TAP2, SMITH_TAP2_ROOM = 0x0221225C, 12        # the end of the MAP_SPAWN block
SHOP_PTR = 0x021E7FD4       # Tom's shop, overlay 2, null when closed
SHOP_ITEM_POS = 0x021F772C
SHOP_ALIVE = 0x021F7E10     # the shop's own update, called each frame
SHOP_ALIVE_SITE = 0x020672C0
SHOP_CLEAR_TEXT = 0x021F7C20
SHOP_SOUND_AT = 124
SHOP_ITEMS_AT = 100         # shop_items, within shop_src


def shop_src():
    return f"""
    ldr r0, [r9, #{MAP}]
    subs r0, r0, #1
    strpl r0, [r9, #{MAP}]
    bicpl r7, r7, #1        @ on the world map A picks a spot, not a tap
    ldr r4, ={SHOP_PTR:#x}
    ldr r4, [r4]
    cmp r4, #0
    bxeq lr
    ldr r0, [r4, #0x80]     @ Tom is talking: A goes to the message
    cmp r0, #0
    bxne lr
    ldr r0, [r4, #0x64]
    ldr r1, [r4, #0x70]
    cmp r0, #3
    cmpeq r1, #1
    beq shop_list
    cmp r0, #4
    cmpeq r1, #3
    bxne lr
    b {SHOP_BUY:#x}

shop_list:
    mov r5, #0xF0
    mov r6, #0xB0
    tst r7, #2              @ B only moves to the exit, so nobody leaves by accident
    orrne r7, r7, #0x80
    b {SHOP_EXIT:#x}
shop_items:
    ldr r6, [r4, #0x4B8]
    tst r7, #1              @ a second tap on the selected item opens it
    beq {SHOP_STEP:#x}
    cmp r6, #0
    bge {SHOP_TAP:#x}
    b {SHOP_STEP:#x}
shop_sound:
    ldr r0, ={SOUND:#x}
    mov r1, #0
    mov r2, #0x67
    bl {PLAY_SE:#x}
    b {OFF:#x}
shop_move:                  @ Down onto the exit; Up back to the first item
    and r0, r7, #0x80
    cmp r0, r1
    beq {OFF:#x}
    str r0, [r3]
    cmp r0, #0
    bne shop_sound
    orr r7, r7, #0x10
    b shop_items

.ltorg
"""


def shop_step_src():
    return f"""
    ands r2, r7, #0x30
    beq {OFF:#x}
    cmp r2, #0x10
    moveq r2, #1
    mvnne r2, #0
    ldrsh r3, [r4, #0x60]
    mov r1, r3
next_item:
    add r6, r6, r2
    cmp r6, #0
    sublt r6, r3, #1
    cmp r6, r3
    movge r6, #0
    add r0, r4, r6, lsl #1
    ldrsh r0, [r0, #0x38]
    cmp r0, #0
    bge {SHOP_TAP:#x}
    subs r1, r1, #1
    bgt next_item
    b {OFF:#x}
"""


def shop_tap_src():
    return f"""
    sub sp, sp, #8
    mov r0, r4
    mov r1, r6
    add r2, sp, #4
    mov r3, sp
    bl {SHOP_ITEM_POS:#x}
    ldr r5, [sp, #4]
    ldr r6, [sp]
    add sp, sp, #8
    b {ON:#x}
"""


def shop_buy_src():
    return f"""
    tst r7, #0x30           @ the Buy screen: its cards flip in shop_yn_src
    beq bux_keys
    ldr r0, ={SOUND:#x}
    mov r1, #0
    mov r2, #0x67
    bl {PLAY_SE:#x}
bux_keys:
    mov r5, #0xE8           @ No, and the door if there is nothing to buy
    mov r6, #0xB0
    tst r7, #2
    bne {ON:#x}
    tst r7, #1
    beq {OFF:#x}
    ldr r0, [r9, #{SHOP_SEL}]
    cmp r0, #0
    movne r5, #0xA8
    b {ON:#x}

.ltorg
"""


def shop_yn_src(var):
    return f"""
    b yn_tick
    b yn_end

yn_tick:                    @ in the shop's own update, which moves these sprites itself
    push {{r4, r5, r6, lr}}
    mov r4, r0
    ldr r5, ={var:#x}
    ldr r0, [r4, #0x64]
    cmp r0, #4
    bne {SHOP_DOOR:#x}
    ldr r0, [r4, #0x70]
    cmp r0, #3
    bne yn_end
    ldr r0, [r4, #0x3AC]
    cmp r0, #0
    bne {SHOP_YN2:#x}
    b yn_end
yn_end:
    mov r0, r4
    pop {{r4, r5, r6, lr}}
    b {SHOP_ALIVE:#x}

.ltorg
"""


def shop_yn2_src():
    return f"""
    ldr r0, ={PAD:#x}
    ldrh r0, [r0, #2]
    tst r0, #0x30
    ldr r6, [r5, #{SHOP_SEL}]
    eorne r6, r6, #1
    strne r6, [r5, #{SHOP_SEL}]
    ldr r0, [r5, #{SHOP_SHOWN}]
    cmp r0, r6
    beq {SHOP_YN + 4:#x}
    b {SHOP_YN3:#x}

.ltorg
"""


def shop_yn3_src():
    return f"""
    str r6, [r5, #{SHOP_SHOWN}]
    sub sp, sp, #8
    mov r3, #0
    str r3, [sp]
    ldr r0, [r4, #0x3AC]
    lsl r1, r6, #1          @ Yes: 2 selected, 0 plain and still
    lsl r2, r6, #12
    bl {SPRITE_SEQ:#x}
    mov r3, #0
    ldr r0, [r4, #0x3F0]
    rsb r1, r6, #3          @ No: 3 selected, 1 plain and still
    sub r1, r1, r6
    eor r2, r6, #1
    lsl r2, r2, #12
    bl {SPRITE_SEQ:#x}
    add sp, sp, #8
    b {SHOP_YN + 4:#x}
"""


def shop_exit_src():
    return f"""
    ldr r3, ={SHOP_DATA:#x}     @ r5, r6 are the exit's tap point
    ldr r1, [r3]
    ands r0, r7, #0xC0
    bne {SHOP_CODE + SHOP_SOUND_AT + 20:#x}
    cmp r1, #0
    beq {SHOP_CODE + SHOP_ITEMS_AT:#x}
    b {SHOP_EXIT2:#x}

.ltorg
"""


def shop_exit2_src():
    return f"""
    tst r7, #1
    bne {ON:#x}
    tst r7, #0x30
    beq {OFF:#x}
    mov r0, #0
    str r0, [r3]
    b {SHOP_CODE + SHOP_ITEMS_AT:#x}
"""


def shop_door_src():
    return f"""
    mov r0, #1              @ not on the Buy screen: reset its choice
    str r0, [r5, #{SHOP_SEL}]
    mvn r0, #0
    str r0, [r5, #{SHOP_SHOWN}]
    ldr r6, ={SHOP_DATA:#x}
    ldr r0, [r4, #0x64]
    cmp r0, #3
    mvnne r0, #0
    strne r0, [r6, #4]
    movne r0, #0
    strne r0, [r6]
    bne {SHOP_YN + 4:#x}
    b {SHOP_DOOR2:#x}

.ltorg
"""


def shop_door2_src():
    return f"""
    ldr r1, [r6]            @ the exit only animates while selected
    ldr r0, [r6, #4]
    cmp r0, r1
    beq {SHOP_YN + 4:#x}
    str r1, [r6, #4]
    ldr r0, [r4, #0x434]
    cmp r0, #0
    beq {SHOP_YN + 4:#x}
    sub sp, sp, #8
    mov r3, #0
    str r3, [sp]
    lsl r2, r1, #5          @ Down stored 0x80: speed 0x1000, otherwise 0
    mov r1, #0
    b {SHOP_DOOR3:#x}
"""


def shop_door3_src():
    return f"""
    cmp r2, #0              @ sequence 0 rests bare, sequence 1 pulses
    movne r1, #1
    bl {SPRITE_SEQ:#x}
    add sp, sp, #8
    ldr r0, [r6, #4]
    cmp r0, #0
    beq {SHOP_YN + 4:#x}
    mov r0, r4              @ on the exit: no item stays selected
    bl {SHOP_CLEAR_TEXT:#x}
    add r0, r4, #0xBC
    bl {OBJ_FREE:#x}
    mvn r0, #0
    str r0, [r4, #0x4B8]
    b {SHOP_YN + 4:#x}
"""


def mix_src(var):
    rows = ((2, 0xF4, 0xB4), (0x200, 0x30, 0x10), (0x100, 0x58, 0x10), (8, 0xBC, 0x94), (0x400, 0xF0, 0x10))
    table = chr(10).join(f".word {key << 16 | y << 8 | x:#x}" for key, x, y in rows) + chr(10) + ".word 0"
    return (
        (MIX_CODE, MIX_ROOM, f"""
    ldr r0, [r9, #{MIX}]    @ the mixing room's item page, or on to the shop
    cmp r0, #0
    beq {SHOP_CODE:#x}
    ldr r1, [r0, #0xC]
    ldr r2, [r0, #0x18]
    cmp r1, #3
    cmpeq r2, #3
    beq {MIX_KEYS:#x}
    b {SMITH_TAP:#x}
"""),
        (SMITH_TAP, SMITH_TAP_ROOM, f"""
    cmp r0, #{SMITH_TAG:#x}
    bne {MAT_CODE + 8:#x}
    tst r7, #1
    b {SMITH_TAP2:#x}
"""),
        (SMITH_TAP2, SMITH_TAP2_ROOM, f"""
    beq {OFF:#x}
    mov r5, #128
    b {ON:#x}
"""),
        (SMITH_ON2, SMITH_ON2_ROOM, f"""
    b {MAT_CODE:#x}
"""),
        (MIX_KEYS, MIX_KEYS_ROOM, f"""
    ldr r3, ={MIX_TABLE:#x}
more_keys:
    ldr r0, [r3], #4
    cmp r0, #0
    beq {MIX_GRID:#x}
    tst r7, r0, lsr #16
    beq more_keys
    and r5, r0, #0xFF
    b {MIX_KEY2:#x}

.ltorg
"""),
        (MIX_KEY2, MIX_KEY2_ROOM, f"""
    lsr r6, r0, #8
    and r6, r6, #0xFF
    b {ON:#x}
    mov r5, #0xB8           @ the pot
    mov r6, #0x5A
    b {ON:#x}
"""),
        (MIX_TABLE, MIX_TABLE_ROOM, table),
        (MIX_GRID, MIX_GRID_ROOM, f"""
    ldr r4, [r9, #{MIX}]
    ldr r1, [r4, #0x4C]
    ands r0, r7, #0xF0
    bne {MIX_STEP:#x}
    cmp r1, #0
    bge {MIX_USE:#x}
    b {OFF:#x}
"""),
        (MIX_STEP, MIX_STEP_ROOM, f"""
    clz r0, r0              @ right, left, up, down
    rsb r0, r0, #27
    adr r2, steps
    ldrsb r0, [r2, r0]
    add r1, r1, r0
    and r1, r1, #15
    b {MIX_TAP:#x}
steps:
.byte 1, 0xFF, 0xFC, 4
"""),
        (MIX_TAP, MIX_TAP_ROOM, f"""
    and r5, r1, #3          @ the centre of grid cell r1
    add r5, r5, r5, lsl #1
    lsl r5, r5, #3
    add r5, r5, #0x1C
    lsr r6, r1, #2
    lsl r6, r6, #5
    add r6, r6, #0x30
    b {ON:#x}
"""),
        (MIX_USE, MIX_USE_ROOM, f"""
    tst r7, #0x800          @ Y opens the selected item's page
    bne {MIX_TAP:#x}
    tst r7, #1
    beq {OFF:#x}
    ldr r2, [r4, #0x38]     @ A puts it in the pot, or opens a recipe
    cmp r2, #0
    beq {MIX_POT:#x}
    b {MIX_TAP:#x}
"""),
        (MIX_PROMPTS, MIX_PROMPTS_ROOM, f"""
    push {{r4, lr}}         @ the bowl's sprite: place it, then its prompts' sequence
    mov r4, r0
    bl 0x02034164
    mov r0, r4
    mov r1, #1
    pop {{r4, lr}}
    b 0x02034508
"""),
        (MIX_START, MIX_START_ROOM, f"""
    push {{r0, lr}}
    bl {MIX_PROMPTS_OFF:#x}
    bl {MIX_SOUND + 4:#x}    @ the last result's jingle data goes before this mix loads its own
    pop {{r0, lr}}
    b {MIX_RESET:#x}
"""),
        (MIX_ON, MIX_ON_ROOM, f"""
    ldr r1, ={var + MIX:#x}
    str r0, [r1]
    b {MIX_FRAME:#x}

.ltorg
"""),
        (SMITH_ON, SMITH_ON_ROOM, f"""
    ldr r2, [pc, #-12]      @ the address just above, in the MIX_ON block
    ldr r1, [r0, #0x10]
    b {SMITH_ON2:#x}
"""),
        (MIX_OFF, MIX_OFF_ROOM, f"""
    ldr r1, ={var + MIX:#x}
    mov r2, #0
    str r2, [r1]
    b {MIX_END:#x}

.ltorg
"""),
    )


def mat_src():
    return f"""
    b mat_on
    b mat_pulse
    b mat

mat_on:                     @ the smith's frame: r0 the object, r1 its page
    cmp r1, #5              @ the forging page
    moveq r1, #{SMITH_TAG:#x}
    beq mat_store
    cmp r1, #3              @ the page choosing a material
    movne r1, #0
    bne mat_store
    ldr r1, =mat_obj
    str r0, [r1]
    ldr r1, =mat_tag
    ldr r1, [r1]
mat_store:
    str r1, [r2]
    b {MAT_NUM:#x}          @ the counts, then the smith's frame

mat_pulse:                  @ only the chosen material's icon pulses
    ldr r1, [r4, #0x33C]
    cmp r1, r5
    ldreq r1, [r4, #0x348]
    movne r1, #0x1000
    bx lr

mat:                        @ taps through the page's own checks
    ldr r1, =mat_tag
    ldr r1, [r1]
    cmp r0, r1
    bne {SHOP_CODE:#x}
    ldr r4, =mat_obj
    ldr r4, [r4]
    ldr r1, [r4, #0x1C]
    cmp r1, #2
    bne {OFF:#x}
    ldr r3, [r4, #0x4C]
    ldr r2, [r4, #0x33C]
    mov r1, #1
    cmp r2, #0              @ nothing chosen yet: the first material
    blt mat_next
    mov r6, #8
    tst r7, #1              @ A: the circle
    movne r5, #0xD8
    bne {ON:#x}
    tst r7, #2              @ B: the arrow
    movne r5, #0xF8
    bne {ON:#x}
    tst r7, #0x40
    mvnne r1, #0
    bne mat_next
    tst r7, #0x80
    beq {OFF:#x}
mat_next:
    mov r0, #4
mat_look:
    add r2, r2, r1
    and r2, r2, #3
    mov r5, #1
    tst r3, r5, lsl r2
    bne mat_found
    subs r0, r0, #1
    bne mat_look
    b {OFF:#x}
mat_found:
    ldr r0, [r4, #0x33C]
    cmp r0, r2              @ a second tap would confirm it
    beq {OFF:#x}
    cmp r0, #0
    bge mat_tap
    str r2, [r4, #0x33C]    @ the first choice is quiet: no tap
    mov r0, r4
    mov r1, r2
    bl {MAT_SHOW:#x}
    b {OFF:#x}
mat_tap:
    mov r5, #0x20
    add r6, r2, r2, lsl #2
    lsl r6, r6, #3
    add r6, r6, #0x38
    b {ON:#x}

.ltorg
mat_tag:
.word {SMITH_TAG + 4:#x}
mat_obj:
.word 0
"""


def mat_num_src():
    """The smith's material page (page 3, r0 its object): at the top right of each material's
    text box, how many are owned ("x02"), as text (the game's own text, so no sprite graphics are
    loaded). A slot shows only while its name does (+0x350 + slot * 4); the material is item
    0x20 + slot. Any other page clears them. Then the smith's frame."""
    digit0 = entext.encode("0")[0]
    ex = entext.encode("x")[0]
    return f"""
    push {{r0, r1, r2, r3, r4, r5, r6, r7, r8, lr}}
    mov r4, r0
    ldr r5, ={MAT_SHOWN:#x}
    ldr r0, [r4, #0x10]
    cmp r0, #3
    bne num_clear
    ldr r0, ={SAVE_TASK:#x}
    bl {SAVE_OF:#x}
    mov r8, r0
    mov r6, #0
num_slot:
    add r0, r4, #0x350
    ldr r0, [r0, r6, lsl #2]
    cmp r0, #0
    moveq r7, #0
    beq num_have
    mov r0, r8
    mvn r1, #0
    add r2, r6, #0x20
    bl {ITEM_COUNT:#x}
    cmp r0, #99
    movgt r0, #99
    mov r7, r0
num_have:
    ldr r0, [r5, r6, lsl #2]
    cmp r0, r7
    beq num_next
    str r7, [r5, r6, lsl #2]
    mov r0, r6
    bl {MAT_FREE:#x}
    cmp r7, #0
    beq num_next
    mov r0, r6
    mov r1, r7
    bl make
num_next:
    add r6, r6, #1
    cmp r6, #4
    blt num_slot
    b num_end
num_clear:
    mov r6, #0
clear:
    mov r0, #0
    str r0, [r5, r6, lsl #2]
    mov r0, r6
    bl {MAT_FREE:#x}
    add r6, r6, #1
    cmp r6, #4
    blt clear
num_end:
    pop {{r0, r1, r2, r3, r4, r5, r6, r7, r8, lr}}
    b {SMITH_FRAME:#x}

make:                       @ r0 a slot, r1 its count (1-99): its text
    push {{r4, r5, r6, r7, lr}}
    sub sp, sp, #20
    mov r6, r0
    ldr r5, ={MAT_TOKS:#x}
    add r5, r5, r6, lsl #3
    mov r7, r5
    mov r2, #0
tens:
    cmp r1, #10
    subhs r1, r1, #10
    addhs r2, r2, #1
    bhs tens
    mov r3, #{ex}           @ "x" and two digits: the game holds at most 99
    strh r3, [r7], #2
    add r2, r2, #{digit0}
    strh r2, [r7], #2
    add r1, r1, #{digit0}
    strh r1, [r7], #2
    ldr r1, =0xFFFD
    strh r1, [r7]
    bl {FREE_SLOT:#x}
    cmn r0, #1
    beq made
    mov r4, r0
    mov r0, #0x80
    bl {ALLOC:#x}
    bl {ARROW_SLOT:#x}
    ldr r3, ={MAT_SLOTS:#x}
    add r2, r4, #1
    str r2, [r3, r6, lsl #2]
    ldr r3, ={MAT_BUFS:#x}
    str r0, [r3, r6, lsl #2]
    cmp r0, #0
    beq made
    mov r1, #0xC
    str r1, [sp]
    mov r1, #1
    str r1, [sp, #4]
    mov r1, #0
    str r1, [sp, #8]
    str r5, [sp, #12]
    mov r2, #40
    mul r2, r6, r2
    add r2, r2, #{MAT_NUM_Y}
    mov r1, #{MAT_NUM_X}
    mov r3, #0
    bl {TEXT_CREATE:#x}
made:
    add sp, sp, #20
    pop {{r4, r5, r6, r7, pc}}

.ltorg
"""


def mat_free_src():
    """r0 a slot of MAT_NUM's: its count's text cleared, if the text slot still holds it."""
    return f"""
    ldr r3, ={MAT_SLOTS:#x}
    ldr r1, [r3, r0, lsl #2]
    subs r1, r1, #1
    bxmi lr
    mov r2, #0
    str r2, [r3, r0, lsl #2]
    ldr r2, ={MAT_BUFS:#x}
    ldr r2, [r2, r0, lsl #2]
    ldr r3, ={TEXT_SLOTS:#x}
    ldr r3, [r3, r1, lsl #5]
    cmp r3, r2
    bxne lr
    mov r0, r1
    b {TEXT_FREE:#x}

.ltorg
"""


def mix_sound_src():
    """The mixing room's result jingle plays on after A, and the room's music fades back in."""
    return f"""
    b mix_keep
    b mix_release
    push {{r0, r1, r2, r3, lr}}     @ leaving the room: free it, then the room's own music fade
    bl mix_release
    pop {{r0, r1, r2, r3, lr}}
    b {SOUND_FADE:#x}

mix_keep:                   @ r4 the room: the result screen would free its jingle's data at once
    push {{r0, lr}}         @ MIX_BACK goes on with r0, the room: the fade's own r0 must not leak out
    ldr r12, ={MIX_KEEP:#x}
    ldr r1, [r4, #0x460]
    ldr r2, [r4, #0x464]
    stm r12, {{r1, r2}}
    mov r1, #0
    str r1, [r4, #0x460]
    str r1, [r4, #0x464]
    ldr r0, ={SOUND:#x}
    ldr r1, [r4, #0x45C]    @ the music, faded out for the result: back to full
    mov r2, #0x7F
    mov r3, #30
    bl {SOUND_FADE:#x}
    pop {{r0, pc}}

mix_release:                @ in the order the result screen frees them
    push {{r4, lr}}
    ldr r4, ={MIX_KEEP:#x}
    ldr r1, [r4]
    cmp r1, #0
    ldrne r0, ={SOUND:#x}
    blne {SOUND_RELEASE:#x}
    ldr r1, [r4, #4]
    cmp r1, #0
    ldrne r0, ={SOUND:#x}
    blne {SOUND_RELEASE:#x}
    mov r1, #0
    str r1, [r4]
    str r1, [r4, #4]
    pop {{r4, pc}}

.ltorg
"""


MIX_SIGN_X, MIX_SIGN_Y = 216, 128     # the floor's right edge (map 65); at 200 the pot and sign could both be reached
MIX_SIGN_ZONE = 40                     # its zone's width: x 196-236, well clear of the pot's (123-171)
MIX_SIGN_MSG = 39                      # bank 2189, added: the four gear recipes no recipe item teaches
