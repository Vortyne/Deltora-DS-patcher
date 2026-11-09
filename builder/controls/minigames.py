"""The quiz, the Belt of Deltora puzzle, the Grand Farm's crops and the Disposal Pit.

Part of the controls namespace (see __init__.py): names from every part are shared."""

QUIZ_CODE, QUIZ_ROOM = 0x02215D40, 0x220   # Mokeet's picture quiz: the D-pad picks, A answers
QUIZ_TRG, QUIZ_X, QUIZ_Y = 0x5154, 0x5155, 0x5156   # GetTpTouch's arguments in the quiz (script 2381)
CROP_MARK = 0x5157              # GetTpTouch's argument in the farmer's PickCrop (script 2338)
BELT_MARK = 0x5158              # GetTpTouch's argument in the Belt of Deltora puzzle (script 2386), for GetTouchTrg(0)
BELT_CODE, BELT_ROOM = 0x02216230, 0x130    # the belt puzzle: the D-pad picks a gem, A sets it
BELT_MORE, BELT_MORE_ROOM = 0x02216A60, 0x300   # its helpers (the 26th kilobyte)
BELT_DATA = 0x02215AC0          # +0 the chosen gem, +4 the arrow's id, +8 gems taken (bits), +16 the gems' x, y
BELT_GEMS = ((141, 111), (113, 50), (162, 73), (208, 105), (96, 120), (157, 145), (61, 81))   # SpawnObj's places
BELT_ARROW_GAP = 18             # the arrow's tip this far above a gem's middle, clear of its top
BELT_NONE = -1                  # no gem chosen (no hint of the order): the D-pad then picks the leftmost gem left
BELT_NEAR = 16                  # a touch this close on both axes takes a gem (IsMobTouchSize(16, 16))
CROP_CODE, CROP_ROOM = 0x022160F0, 0x140   # the Grand Farm's crop menu; BELT_CODE follows
CROP_MSG = 18                   # bank 2190: the menu with crop 0, 1 or 2 highlighted (18 + crop)
CROP_BOX_Y = 0xA0               # the talk box's text, as the smith's notices: the box itself is the bottom screen's
QUIZ_ARROW_GAP = 2              # pixels between the arrow and a picture's top edge
HOLE_X, HOLE_HELD = 0x4858, 0x4848   # GetTpTouch's arguments in the Disposal Pit: touch x, touch held


def quiz_src():
    """Mokeet's picture quiz, script 2381's NazoMain: each frame it asks GetTouchTrg(0) for a new
    touch, then GetTpTouch(1) and (2) for where, and the picture whose box holds it is the answer.
    patch_quiz makes those three calls GetTpTouch with our marks. Left and right move the camp's
    green arrow between the pictures; A answers with the centre of the chosen one, so the script
    judges it as a touch there. A real touch still answers as before."""
    return f"""
quiz_ask:                   @ from script_ask: r0 the argument, r4 the script, {{r4, lr}} pushed
    ldr r1, ={QUIZ_TRG:#x}
    subs r1, r0, r1
    beq quiz_trg
    cmp r1, #1
    cmpne r1, #2
    beq quiz_xy
    cmp r1, #3
    bge {BELT_CODE:#x}      @ the Grand Farm's crop menu, the belt puzzle, or the plain read
    mov r0, r4
    pop {{r4, lr}}
    b {TP_TOUCH:#x}
quiz_result:                @ r1 the answer
    mov r0, r4
    bl {SET_RESULT:#x}
    mov r0, #1
    pop {{r4, pc}}
quiz_trg:                   @ 1 for a new touch or A
    push {{r5, r6, r7}}
    adr r5, state
    ldr r0, ={PAD:#x}
    ldrh r6, [r0, #2]       @ buttons newly pressed
    bl {TOUCH_TRIG:#x}
    mov r7, #1
    cmp r0, #0
    movne r0, #0            @ a real touch: its own place
    bne trg_answer
    tst r6, #1
    movne r0, #1            @ A: the chosen picture's centre
    bne trg_answer
    mov r7, #0
    ldr r1, [r5]
    mov r0, r1
    tst r6, #0x10
    addne r0, r0, #1
    tst r6, #0x20
    subne r0, r0, #1
    cmp r0, #0
    movlt r0, #0
    cmp r0, #2
    movgt r0, #2
    str r0, [r5]
    cmp r0, r1
    beq trg_show
    ldr r0, ={SOUND:#x}
    mov r1, #0
    mov r2, #0x67
    bl {PLAY_SE:#x}
trg_show:
    bl get_arrow
    cmp r0, #0
    beq trg_out
    ldr r3, [r5]
    adr r2, places
    add r2, r2, r3, lsl #2
    ldrb r1, [r2]
    lsl r1, r1, #12
    str r1, [r0, #0x220]
    ldrb r1, [r2, #2]       @ the picture's top edge
    sub r1, r1, #{QUIZ_ARROW_GAP}
    lsl r1, r1, #12
    str r1, [r0, #0x224]
    b trg_out
trg_answer:
    str r0, [r5, #8]
    cmp r0, #0              @ a real touch: the next question's arrow starts in the middle
    moveq r1, #1
    streq r1, [r5]
    ldr r1, [r5, #4]        @ the arrow, if there is one, goes off screen
    cmp r1, #0
    beq trg_out
    ldr r0, ={WORLD:#x}
    bl {FIND_MOB:#x}
    cmp r0, #0
    movne r1, #{300 << 12:#x}
    strne r1, [r0, #0x224]
trg_out:
    mov r1, r7
    pop {{r5, r6, r7}}
    b quiz_result
quiz_xy:                    @ r1 1 for x, 2 for y
    adr r2, state
    ldr r3, [r2, #8]
    cmp r3, #0
    bne pad_xy
    push {{r1}}             @ as GetTpTouch: -1 with no touch held
    bl {TOUCH_HELD:#x}
    pop {{r1}}
    cmp r0, #0
    mvneq r1, #0
    beq quiz_result
    ldr r2, ={TOUCH_STATE:#x}
    cmp r1, #1
    ldrheq r1, [r2, #0x12]
    ldrhne r1, [r2, #6]
    b quiz_result
pad_xy:
    ldr r3, [r2]
    cmp r1, #2              @ y, the last read: the next question's arrow starts in the middle
    moveq r12, #1
    streq r12, [r2]
    adr r2, places
    add r2, r2, r3, lsl #2
    cmp r1, #1
    ldrbeq r1, [r2]
    ldrbne r1, [r2, #1]
    b quiz_result
get_arrow:                  @ r5 state: the arrow, made if it is gone; 0 if it can't be
    push {{r3, lr}}
    ldr r1, [r5, #4]
    cmp r1, #0
    beq new_arrow
    ldr r0, ={WORLD:#x}
    bl {FIND_MOB:#x}
    cmp r0, #0
    popne {{r3, pc}}
new_arrow:
    sub sp, sp, #8
    mov r3, #0
    str r3, [sp]
    str r3, [sp, #4]
    mov r2, #0
    mov r1, #31
    ldr r0, ={EVENTS:#x}
    bl {SPAWN_OBJECT:#x}
    add sp, sp, #8
    str r0, [r5, #4]
    mov r1, r0
    ldr r0, ={WORLD:#x}
    bl {FIND_MOB:#x}
    pop {{r3, pc}}
    .ltorg
state:
    .word 1, 0, 0           @ the chosen picture (0 to 2), the arrow's id, answered by A
places:                     @ each picture's centre x, y, and top edge, inside its touch box
    .byte 55, 83, 53, 0
    .byte 127, 55, 21, 0
    .byte 199, 83, 53, 0
"""


def belt_src():
    """The Belt of Deltora puzzle, script 2386: each frame its loop asks GetTouchTrg(0) for a new
    touch, then each gem not yet set asks IsMobTouchSize(gem, 16, 16), which compares the touch
    with the gem's place on screen. patch_belt makes that GetTouchTrg ask BELT_MARK. The D-pad moves
    the camp's green arrow to the nearest gem still there in that direction; A puts a touch on the
    chosen gem (the touch state's held, new, x and y, as the stylus would), so the script sets it
    exactly as if tapped. Gems taken by A or the stylus are noted the way the game tests them, and
    the arrow passes over them; when the chosen one goes, it moves to the nearest left."""
    return f"""
belt_ask:                   @ from quiz_ask: r1 the mark - QUIZ_TRG (3 or more), r4 the script, {{r4, lr}} pushed
    cmp r1, #3
    beq {CROP_CODE:#x}
    cmp r1, #4
    beq belt
    mov r0, r4
    pop {{r4, lr}}
    b {TP_TOUCH:#x}
belt:
    push {{r5, r6, r7, r8}}
    ldr r5, ={BELT_DATA:#x}
    ldr r0, ={TOUCH_STATE:#x}
    ldrb r7, [r0, #3]       @ a new touch: the answer, as GetTouchTrg
    cmp r7, #0
    beq belt_keys
    ldrh r1, [r0, #0x12]
    ldrh r2, [r0, #6]
    bl {BELT_MORE + 12:#x}  @ the camera: to the world, where the gems are kept
    add r1, r1, r0
    add r2, r2, r3
    b belt_hit
belt_keys:
    ldr r0, ={PAD:#x}
    ldrh r6, [r0, #2]       @ buttons newly pressed
    tst r6, #1
    beq belt_move
    ldr r0, [r5]
    cmp r0, #0
    blt belt_after          @ A with nothing chosen: nothing
    bl {BELT_MORE + 8:#x}   @ A: a touch on the chosen gem
    push {{r1, r2}}
    bl {BELT_MORE + 12:#x}
    sub r1, r1, r0
    sub r2, r2, r3
    ldr r0, ={TOUCH_STATE:#x}
    mov r7, #1
    strb r7, [r0, #2]
    strb r7, [r0, #3]
    strh r1, [r0, #0x12]
    strh r2, [r0, #6]
    pop {{r1, r2}}
belt_hit:
    bl {BELT_MORE:#x}
    mvn r0, #0              @ a gem set (or a touch): nothing chosen again
    str r0, [r5]
    b belt_after
belt_move:
    ands r6, r6, #0xF0
    blne {BELT_MORE + 4:#x}
belt_after:
    ldr r0, [r5, #8]
    cmp r0, #0x7F
    bne belt_left
    bl {BELT_MORE + 20:#x}  @ all seven set: the next try starts fresh
    b belt_out
belt_left:
    ldr r0, [r5]
    cmp r0, #0
    blt belt_hide           @ nothing chosen: no arrow
    bl {BELT_MORE + 16:#x}
    movs r8, r0
    beq belt_out
    ldr r0, [r5]
    bl {BELT_MORE + 8:#x}
    lsl r1, r1, #12
    str r1, [r8, #0x220]
    sub r2, r2, #{BELT_ARROW_GAP}
    lsl r2, r2, #12
    str r2, [r8, #0x224]
    b belt_out
belt_hide:
    bl {BELT_MORE + 24:#x}
belt_out:
    mov r1, r7
    pop {{r5, r6, r7, r8}}
    mov r0, r4
    bl {SET_RESULT:#x}
    mov r0, #1
    pop {{r4, pc}}
.ltorg
"""


def belt_more_src():
    """belt_src's helpers; r5 is BELT_DATA throughout. +0 hit: r1, r2 a touch in the world, the
    gem it takes noted. +4 step: r6 the direction keys (0: the nearest), the chosen gem moves.
    +8 gem: r0 a gem, r1, r2 its place. +12 camera: r0 its x, r3 its y. +16 the arrow (0 if none)."""
    return f"""
    b hit
    b step
    b gem
    b cam
    b arrow
    b reset
    b hide
reset:                      @ +20: no gems taken, nothing chosen; then as hide
    mvn r0, #0
    str r0, [r5]
    mov r0, #0
    str r0, [r5, #8]
hide:                       @ +24: the arrow off screen, if there is one (none is made for it)
    push {{lr}}
    ldr r1, [r5, #4]
    cmp r1, #0
    popeq {{pc}}
    ldr r0, ={WORLD:#x}
    bl {FIND_MOB:#x}
    cmp r0, #0
    movne r1, #{300 << 12:#x}
    strne r1, [r0, #0x224]
    pop {{pc}}
first:                      @ the leftmost gem left: r0 it, or -1
    push {{r4, r7, lr}}
    mvn r7, #0
    mov r3, #0x1000
    mov r4, #0
first_next:
    ldr r0, [r5, #8]
    mov r12, #1
    tst r0, r12, lsl r4
    bne first_skip
    mov r0, r4
    bl gem
    cmp r1, r3
    movlt r3, r1
    movlt r7, r4
first_skip:
    add r4, r4, #1
    cmp r4, #7
    blt first_next
    mov r0, r7
    pop {{r4, r7, pc}}
hit:
    push {{r4, lr}}
    mov r4, #0
hit_next:
    ldr r3, [r5, #8]
    mov r12, #1
    tst r3, r12, lsl r4
    bne hit_skip
    add r12, r5, #16
    add r12, r12, r4, lsl #1
    ldrb r0, [r12]
    subs r0, r1, r0
    rsblt r0, r0, #0
    cmp r0, #{BELT_NEAR}
    bge hit_skip
    ldrb r0, [r12, #1]
    subs r0, r2, r0
    rsblt r0, r0, #0
    cmp r0, #{BELT_NEAR}
    bge hit_skip
    mov r12, #1
    orr r3, r3, r12, lsl r4
    str r3, [r5, #8]
    pop {{r4, pc}}
hit_skip:
    add r4, r4, #1
    cmp r4, #7
    blt hit_next
    pop {{r4, pc}}
gem:
    add r12, r5, #16
    add r12, r12, r0, lsl #1
    ldrb r1, [r12]
    ldrb r2, [r12, #1]
    bx lr
cam:                        @ as FUN_02081f6c: the stage's scroll and shake
    ldr r12, ={STAGE:#x}
    ldr r0, [r12, #0x278]
    ldr r3, [r12, #0x2a0]
    add r0, r0, r3
    ldr r3, [r12, #0x27c]
    ldr r12, [r12, #0x2a4]
    add r3, r3, r12
    bx lr
step:                       @ the score: the distance that way, plus twice the distance across
    push {{r4, r7, r8, lr}}
    sub sp, sp, #8
    ldr r0, [r5]
    cmp r0, #0
    bge step_from
    bl first                @ nothing chosen yet: any direction picks the leftmost gem
    mov r6, #0x10
    str r0, [sp, #4]
    b step_found
step_from:
    bl gem
    mov r7, r1
    mov r8, r2
    mov r0, #0x10000
    str r0, [sp]
    mvn r0, #0
    str r0, [sp, #4]
    mov r4, #0
step_next:
    ldr r0, [r5]
    cmp r4, r0
    beq step_skip
    ldr r3, [r5, #8]
    mov r12, #1
    tst r3, r12, lsl r4
    bne step_skip
    mov r0, r4
    bl gem
    sub r1, r1, r7
    sub r2, r2, r8
    tst r6, #0x10
    beq step_l
    cmp r1, #0
    ble step_skip
    mov r0, r1
    mov r3, r2
    b step_score
step_l:
    tst r6, #0x20
    beq step_u
    cmp r1, #0
    bge step_skip
    rsb r0, r1, #0
    mov r3, r2
    b step_score
step_u:
    tst r6, #0x40
    beq step_d
    cmp r2, #0
    bge step_skip
    rsb r0, r2, #0
    mov r3, r1
    b step_score
step_d:
    tst r6, #0x80
    beq step_any
    cmp r2, #0
    ble step_skip
    mov r0, r2
    mov r3, r1
step_score:
    cmp r3, #0
    rsblt r3, r3, #0
    add r0, r0, r3, lsl #1
    b step_cmp
step_any:
    cmp r1, #0
    rsblt r1, r1, #0
    cmp r2, #0
    rsblt r2, r2, #0
    add r0, r1, r2
step_cmp:
    ldr r1, [sp]
    cmp r0, r1
    strlt r0, [sp]
    strlt r4, [sp, #4]
step_skip:
    add r4, r4, #1
    cmp r4, #7
    blt step_next
step_found:
    ldr r0, [sp, #4]
    cmp r0, #0
    blt step_done
    str r0, [r5]
    cmp r6, #0
    beq step_done
    ldr r0, ={SOUND:#x}
    mov r1, #0
    mov r2, #0x67           @ the menus' cursor sound
    bl {PLAY_SE:#x}
step_done:
    add sp, sp, #8
    pop {{r4, r7, r8, pc}}
arrow:                      @ the camp's green arrow, made if it is gone
    push {{r3, lr}}
    ldr r1, [r5, #4]
    cmp r1, #0
    beq arrow_new
    ldr r0, ={WORLD:#x}
    bl {FIND_MOB:#x}
    cmp r0, #0
    popne {{r3, pc}}
arrow_new:
    sub sp, sp, #8
    mov r3, #0
    str r3, [sp]
    str r3, [sp, #4]
    mov r2, #0
    mov r1, #31
    ldr r0, ={EVENTS:#x}
    bl {SPAWN_OBJECT:#x}
    add sp, sp, #8
    str r0, [r5, #4]
    mov r1, r0
    ldr r0, ={WORLD:#x}
    bl {FIND_MOB:#x}
    pop {{r3, pc}}
.ltorg
"""


def belt_data_src():
    gems = ", ".join(f"{x}, {y}" for x, y in BELT_GEMS)
    return f"""
.word {BELT_NONE}, 0, 0, 0
.byte {gems}
.align 2
"""


def crop_src():
    """The Grand Farm: the farmer used to sow a crop picked at random as the farm was entered
    (global byte 6: 0 wheat, 1 pumpkins, 2 hibiscus). patch_crop has his PickCrop ask our mark each
    frame after he agrees to sow; this answers -1 while the menu is up and the crop once A picks it.
    The menu is the talk box, as the options' info boxes open one: the question, then the three
    crops on one line (bank 2190, 18 + the chosen crop, highlighted), since the box holds two lines.
    Left or Up and Right or Down swap in the one for the crop before or after."""
    return f"""
crop:                       @ from quiz_ask: r4 the script, {{r4, lr}} pushed
    push {{r5, r6, r7}}
    adr r5, crop_state
    mvn r7, #0              @ -1: not chosen yet
    ldr r0, [r5, #8]
    cmp r0, #0
    bne crop_keys
    mov r0, #1              @ first call: the menu goes up, on the first crop
    str r0, [r5, #8]
    mov r0, #0
    str r0, [r5, #4]
    bl crop_show
    b crop_out
crop_keys:
    ldr r0, ={PAD:#x}
    ldrh r6, [r0, #2]
    ldr r1, [r5, #4]
    tst r6, #1
    bne crop_chosen
    tst r6, #0x60           @ Up or Left
    beq crop_down
    subs r1, r1, #1
    movmi r1, #2
    b crop_moved
crop_down:
    tst r6, #0x90           @ Down or Right
    beq crop_out
    add r1, r1, #1
    cmp r1, #3
    movge r1, #0
crop_moved:
    str r1, [r5, #4]
    bl crop_show
    ldr r0, ={SOUND:#x}
    mov r1, #0
    mov r2, #0x67
    bl {PLAY_SE:#x}
    b crop_out
crop_chosen:
    ldr r7, [r5, #4]
    mov r0, #0
    str r0, [r5, #8]
    ldr r0, [r5]
    cmp r0, #0
    blne {MESSAGE_CLOSE:#x}
    mov r0, #0
    str r0, [r5]
    ldr r0, ={SOUND:#x}
    mov r1, #0
    mov r2, #100
    bl {PLAY_SE:#x}
crop_out:
    mov r1, r7
    pop {{r5, r6, r7}}
    mov r0, r4
    bl {SET_RESULT:#x}
    mov r0, #1
    pop {{r4, pc}}
crop_show:                  @ r5 the state: the box for the chosen crop, in place of the last
    push {{lr}}
    ldr r0, [r5]
    cmp r0, #0
    blne {MESSAGE_CLOSE:#x}
    sub sp, sp, #16
    mov r0, #0
    str r0, [sp]
    mov r0, #1
    str r0, [sp, #4]
    mov r0, #{CROP_BOX_Y}
    str r0, [sp, #8]
    mov r0, #{TALK_FLAGS}
    str r0, [sp, #12]
    ldr r0, [r5, #4]
    add r0, r0, #{CROP_MSG}
    mov r1, #0
    mvn r2, #0
    mov r3, #0
    bl {MESSAGE_WINDOW:#x}
    add sp, sp, #16
    str r0, [r5]
    pop {{pc}}
.ltorg
crop_state:
    .word 0, 0, 0           @ the box's handle, the chosen crop, the menu up
"""


def patch_quiz(script):
    """Mokeet's picture quiz, script 2381: NazoMain's GetTouchTrg(0) and GetTpTouch(1), (2) become
    GetTpTouch with the quiz marks, so quiz_src can answer them from the D-pad and A."""
    b = bytearray(script)
    funcs, imports = scr.recs(b)
    nazo = scr.rec(b, funcs[1])
    assert nazo["name"] == "NazoMain"
    names = [scr.rec(b, o)["name"] if o else None for o in imports]
    trg, tp = names.index("GetTouchTrg"), names.index("GetTpTouch")
    for at, arg, call, mark in ((28, 0, trg, QUIZ_TRG), (38, 1, tp, QUIZ_X), (46, 2, tp, QUIZ_Y)):
        assert struct.unpack_from("<4H", b, nazo["code"] + at * 2) == (0x4000, arg, 0x2102, call), at
        struct.pack_into("<4H", b, nazo["code"] + at * 2, 0x4001, mark, 0x2102, tp)
    return bytes(b)


def patch_crop(script):
    """The farmer, script 2338: after he agrees to sow ("Then I'll start sowing.") his FlagOn(13, 1)
    becomes PickCrop(13, 1), which asks GetTpTouch(CROP_MARK) each frame until crop_src's menu gives
    a crop, sets the crop (global byte 6, which the farm picked at random on the way in), and then
    does that FlagOn."""
    b = bytearray(script)
    funcs, imports = scr.recs(b)
    touch = scr.rec(b, funcs[3])
    assert touch["name"] == "Mob_Touch"
    names = [scr.rec(b, o)["name"] for o in imports]
    flag_on = names.index("FlagOn")
    at = touch["code"] + 255 * 2
    assert struct.unpack_from("<7H", b, at) == (0x4000, 13, 0x4000, 1, 0x2102, flag_on, 0xA000)
    ix = script_add(b, imports=(("GetTpTouch", 1), ("WaitVsync", 1), ("FlagOn", 2)))
    crop = (0x6008, 6)                                      # global byte 6
    code = (*crop, 0x4001, CROP_MARK, 0x2102, ix["GetTpTouch"], 0x14, 0xA000,      # 0: crop = the menu
            *crop, 0x4000, 0, 0x0C,                         # 8: crop >= 0
            0x101, 0x4001, 6, 0x103,                        # 13: no: to 20
            0x4001, 11, 0x103,                              # 17: yes: to 28
            0x4000, 1, 0x2102, ix["WaitVsync"], 0xA000,     # 20: a frame
            0x4001, -25 & 0xFFFF, 0x103,                    # 25: again, from 0
            0x4000, 13, 0x4000, 1, 0x2102, ix["FlagOn"], 0xA000,   # 28: as he did
            0x4000, 0, 0x108)
    ix.update(script_add(b, funcs=(("PickCrop", 2, code),)))
    struct.pack_into("<7H", b, at, 0x4000, 13, 0x4000, 1, 0x2002, ix["PickCrop"], 0xA000)
    return bytes(b)


def patch_belt(script):
    """The Belt of Deltora puzzle, script 2386: its loop's GetTouchTrg(0) becomes
    GetTpTouch(BELT_MARK), answered by belt_src (a new touch, or A on the chosen gem)."""
    b = bytearray(script)
    funcs, imports = scr.recs(b)
    main = scr.rec(b, funcs[0])
    assert main["name"] == "StartScript"
    names = [scr.rec(b, o)["name"] for o in imports]
    at = main["code"] + 388 * 2
    assert struct.unpack_from("<4H", b, at) == (0x4000, 0, 0x2102, names.index("GetTouchTrg"))
    tp = names.index("GetTpTouch") if "GetTpTouch" in names else script_add(b, imports=(("GetTpTouch", 1),))["GetTpTouch"]
    struct.pack_into("<4H", b, at, 0x4001, BELT_MARK, 0x2102, tp)
    return bytes(b)


def patch_hole(script):
    """Disposal Pit, script 2380: its steering reads GetTpTouch(1) for the touch x and GetTpTouch(0)
    for held, every frame. Their arguments become marks, so the D-pad can answer as the stylus."""
    b = bytearray(script)
    funcs, imports = scr.recs(b)
    main = scr.rec(b, funcs[0])
    assert main["name"] == "StartScript"
    assert b[imports[0x16] + 0x20:imports[0x16] + 0x2A] == b"GetTpTouch"
    for at, arg, mark in ((411, 1, HOLE_X), (417, 0, HOLE_HELD)):
        assert struct.unpack_from("<4H", b, main["code"] + at * 2) == (0x4000, arg, 0x2102, 0x16), at
        struct.pack_into("<2H", b, main["code"] + at * 2, 0x4001, mark)
    return bytes(b)


FARM_SIGN_X, FARM_SIGN_Y = 152, 640    # on the grass between the house and the bushes, clear of the screen edge
FARM_SIGN_MSG = 17                     # bank 2190, added


def patch_farm(script):
    """Grand Farm, script 2605: a sown field grows a stage (and its monsters come) once an hour has
    passed since leaving, instead of a day; three days away ruins it (was two). A signpost by the
    entrance path says so: StartScript's HatakeInit call goes through FarmSign, which puts it up, and
    a new AreaOut puts it back on its screen before running the old one (now AreaOutBase)."""
    b = bytearray(script)
    funcs, imports = scr.recs(b)
    init = scr.rec(b, funcs[1])
    assert init["name"] == "HatakeInit"
    at = init["code"] + 174 * 2            # elapsed > 60 * 60 * 24: the next stage
    assert struct.unpack_from("<16H", b, at) == (0x600A, 0x28, 0x4000, 60, 0x4000, 60, 5, 0x4000, 24, 5, 0xB, 0x101, 0x4001, 127, 0x103, 0x6008)
    struct.pack_into("<H", b, at + 8 * 2, 1)
    at = init["code"] + 132 * 2            # elapsed > 60 * 60 * 24 * 2: ruined, now 3 days
    assert struct.unpack_from("<14H", b, at) == (0x600A, 0x28, 0x4000, 60, 0x4000, 60, 5, 0x4000, 24, 5, 0x4000, 2, 5, 0xB)
    struct.pack_into("<H", b, at + 11 * 2, 3)

    main = scr.rec(b, funcs[0])
    assert main["name"] == "StartScript"
    call = main["code"] + 47 * 2
    assert struct.unpack_from("<5H", b, call) == (0x4000, 0, 0x2002, 1, 0xA000)
    ix = script_add(b, imports=(("SpawnObj", 7), ("MessageWait", 2), ("RangeButtonEvent", 7),
                                ("PlaySe", 2), ("KeyOff", 1), ("KeyOn", 1)), strings=("TouchKanban",))
    zone = (0x4005, ix["TouchKanban"], *imm(0), *imm(0), *imm(FARM_SIGN_X), *imm(FARM_SIGN_Y - 14),
            *imm(48), *imm(64), 0x2102, ix["RangeButtonEvent"], 0xA000)
    spawn = (*imm(0), *imm(0), *imm(SIGN_OBJ), *imm(0), *imm(FARM_SIGN_X), *imm(FARM_SIGN_Y), *imm(0),
             0x2102, ix["SpawnObj"], 0xA000)
    sign = spawn + zone + (0x4000, 0, 0x2002, 1, 0xA000, 0x4000, 0, 0x108)
    # objects go when their 256x192 screen does; the stage's AreaOut(screen) puts them back
    screen = FARM_SIGN_Y // 192 * 8 + FARM_SIGN_X // 256
    old = next(i for i, o in enumerate(funcs) if scr.rec(b, o)["name"] == "AreaOut")
    b[funcs[old] + 0x20:funcs[old] + 0x30] = b"AreaOutBase".ljust(16, b"\0")
    area = (0x601A, 0, *imm(screen), 0xD, 0x101, 0x4001, 3 + len(spawn), 0x103) + spawn + (
            0x601A, 0, 0x601A, 1, 0x2002, old, 0xA000, 0x4000, 0, 0x108)
    touch = (0x4000, 0, *imm(103), 0x2102, ix["PlaySe"], 0xA000,
             0x4000, 0, 0x2102, ix["KeyOff"], 0xA000,
             *imm(FARM_SIGN_MSG), 0x4000, 1, 0x4000, 1, 0x20, 0x2102, ix["MessageWait"], 0xA000) + zone + (
             0x4000, 0, 0x2102, ix["KeyOn"], 0xA000, 0x4000, 0, 0x108)
    ix.update(script_add(b, funcs=(("FarmSign", 1, sign), ("TouchKanban", 2, touch), ("AreaOut", 2, area))))
    struct.pack_into("<H", b, call + 6, ix["FarmSign"])
    return bytes(b)
