"""The camp: D-pad and buttons, saving anywhere it allows, the Save sign, the party.

Part of the controls namespace (see __init__.py): names from every part are shared."""

CAMP_DATA = 0x02212D70       # the hero at camp start, then 1 + the hero chosen
CAMP_PICK, CAMP_PICK_ROOM = 0x02212D78, 40
CAMP_KEEP, CAMP_KEEP_ROOM = 0x022144A0, 320      # after the options block
CAMP_RIM, CAMP_RIM_ROOM = 0x02214708, 52    # the camp's Save sign back to plain
CAMP_HEARTS, CAMP_HEARTS_ROOM = 0x02215880, 0x140  # at camp, the hearts show the hero under the cursor
SAVE_GAUGE = 0x02215A40         # the hearts gauge's object, kept by CAMP_HEARTS for SAVE_HOLD
SAVE_HOLD, SAVE_HOLD_ROOM = 0x02215A44, 0x78    # the save thread's write waits for the portrait and the hearts; BELT_DATA follows
SAVE_HOLD_MAX = 240             # frames after which the write goes ahead regardless (normally it starts at once)
CAMP_LEAVE, CAMP_LEAVE_ROOM = 0x022159C0, 0x80  # camp closing: the top screen's portrait matches who is played
CAMP_MOVE, CAMP_MOVE_ROOM = 0x02215340, 0xA0    # the camp cursor's next spot, past heroes who aren't there; 0x02215800 (128 bytes) is free
PARTY_GROUP, BARDA_BIT, JASMINE_BIT = 16, 20, 19    # the camp script shows Barda and Jasmine by these
CAMP_PET_DELAY = 45            # frames after moving onto Barda or Jasmine before their pet reacts
CAMP_X, CAMP_X_ROOM = 0x02214E20, 0x3A0        # the camp's X: save, and its prompt under the Save sign
CAMP_NAME_Y = 174           # the camp's "Current character" line: the top screen's bottom edge
CAMP_X_AT = 240, 34                            # the prompt's centre x and top y, under the sign at (240, 18)
CAMP_TAP_DELAY = 15                    # frames after the cursor stops before a hero's portrait and costume load
CAMP_TIPS_Y_WAS, CAMP_TIPS_Y = 60, 44     # the camp's Adventure tips: top y, then one 16-pixel line higher
CAMP_BACK, CAMP_BACK_ROOM = 0x02212E80, 32
CAMP_ON_SITE, CAMP_OFF_SITE = 0x02046614, 0x02046688    # sb_CallCamp's overlay load and unload
CAMP_START, CAMP_END = 0x0206CC7C, 0x0206CC98
CAMP_CODE, CAMP_ROOM = 0x022113F4, 548      # Req_BGMSeq and friends, unused
CAMP2_CODE, CAMP2_ROOM = 0x02211DF0, 356    # MessageY and friends, unused


def camp_pick_src():
    return f"""
    ldr r2, [r9, #{CAMP_SEL}]
    cmp r2, #3
    bhs {CAMP2_CODE + 12:#x}
    bl {SHOWN_CODE:#x}      @ a tap confirms only the hero the scene shows
    cmp r0, r2
    ldreq r12, ={CAMP_DATA:#x}
    addeq r0, r2, #1
    streq r0, [r12, #4]
    b {CAMP2_CODE + 12:#x}

.ltorg
"""


def camp_back_src():
    return f"""
    bl {DEFER + 4:#x}       @ a waiting hero tap, then the X prompt under the Save sign
    tst r7, #2
    movne r5, #{BAG_X}
    movne r6, #{BAG_Y}
    bne {ON:#x}
    tst r7, #1
    bne {CAMP_X + 16:#x}    @ A: the line, then the hero is chosen
    b {CAMP_X:#x}
"""


def camp_x_src(var):
    names = chr(10).join(f"n_{k}:" + chr(10) + ".short " + ", ".join(f"{t:#x}" for t in entext.encode(f"Current character: {n}") + [0xFFFD]) + chr(10) + ".align 2" for k, n in enumerate(HERO_NAMES))
    return f"""
    b x_key
    b x_show
    b x_hide
    b x_leave
    b a_key
    b y_early

y_early:                    @ Y doesn't wait for the scene: a portrait load or a pet's animation keeps playing
    tst r7, #0x800
    beq {CAMP_CODE:#x}
    ldr r0, [r9, #{CAMP_KIND}]
    cmp r0, #2              @ no Save here (type 2), so never a save screen
    beq y_key
    ldr r0, =x_line
    bl line_owned
    cmn r0, #1              @ the prompt is down while the save screen is up: no change then
    beq {OFF:#x}
    b y_key

a_key:                      @ A on a hero: the top screen's line shows them
    ldr r2, [r9, #{CAMP_SEL}]
    cmp r2, #2
    bhi a_pick              @ the Muddlet (5) and the rest: the line stays
    ldr r12, =n_cur
    str r2, [r12]
    bl name_show            @ this frame, before the press reaches the hero and their animation
a_pick:
    b {CAMP_PICK:#x}

x_leave:                    @ the camp closing
    push {{lr}}
    ldr r0, =n_cur
    mvn r1, #0
    str r1, [r0]
    bl {KILL:#x}
    pop {{lr}}
    b x_hide

x_key:                      @ X taps the Save sign, wherever the cursor is
    tst r7, #0x800
    bne y_key
    tst r7, #0x400
    beq {OFF:#x}
    ldr r0, [r9, #{CAMP_KIND}]
    cmp r0, #2              @ camp type 2 has no Save (type 3, the Tower's rest rooms, now does)
    beq {OFF:#x}
    bl x_hide               @ the save screen has no room for it; it comes back after
    mov r2, #3
    b {CAMP2_CODE + 12:#x}

y_key:                      @ Y plays as the hero under the cursor, staying at camp: a save here then stores them
    ldr r2, [r9, #{CAMP_SEL}]
    cmp r2, #2              @ the Muddlet (5) and the rest: nothing
    bhi {OFF:#x}
    ldr r12, ={CAMP_DATA:#x}
    str r2, [r12]           @ who camp started with: what leaving and a save use
    add r0, r2, #1
    str r0, [r12, #4]       @ and chosen, so leaving keeps them
    ldr r12, =n_cur
    str r2, [r12]           @ the costume itself changes as camp closes (keep_end): loading it here
                            @ moves sprite graphics and blanks most of the camp's sprites for a moment
    ldr r0, ={SOUND:#x}
    mov r1, #0
    mov r2, #0x65           @ the Yes sound
    bl {PLAY_SE:#x}
    bl name_show
    b {OFF:#x}

x_show:                     @ each idle camp frame: the prompt, and who is being played on the top screen
    push {{r4, lr}}
    ldr r0, [r9, #{CAMP_KIND}]
    cmp r0, #2              @ no Save here (type 2): no prompt
    beq show_name
    ldr r0, =x_line
    bl line_owned
    cmn r0, #1
    bne show_name
    ldr r0, =x_line
    adr r1, x_text
    bl line_put
show_name:
    bl name_show
    pop {{r4, pc}}

name_show:                  @ the top screen's line: redrawn when its hero changes
    push {{r4, lr}}
    ldr r4, =n_cur          @ the hero A or Y was last pressed on
    ldr r4, [r4]
    cmp r4, #0
    ldrlt r4, ={CAMP_DATA:#x}
    ldrlt r4, [r4]          @ none yet: who camp opened with
    cmp r4, #2
    bhi show_end
    ldr r0, =n_line
    bl line_owned
    cmn r0, #1
    beq show_new_name
    ldr r1, =n_line
    ldr r1, [r1, #8]
    cmp r1, r4              @ showing, and still the right hero
    beq show_end
show_new_name:
    ldr r0, =n_line
    bl line_free
    ldr r0, =n_line
    str r4, [r0, #8]
    adr r1, n_texts
    ldr r1, [r1, r4, lsl #2]
    bl line_put
show_end:
    pop {{r4, pc}}

x_hide:                     @ both lines
    push {{lr}}
    ldr r0, =x_line
    bl line_free
    ldr r0, =n_line
    bl line_free
    pop {{pc}}

line_owned:                 @ r0 a line: its text slot while it still holds our buffer, else -1
    ldr r1, [r0]
    subs r1, r1, #1
    bmi owned_end
    ldr r2, ={TEXT_SLOTS:#x}
    ldr r2, [r2, r1, lsl #5]
    ldr r3, [r0, #4]
    cmp r2, r3
    mvnne r1, #0
owned_end:
    mov r0, r1
    bx lr

line_free:                  @ r0 a line
    push {{r4, lr}}
    mov r4, r0
    bl line_owned
    mov r1, #0
    str r1, [r4]
    cmn r0, #1
    blne {TEXT_FREE:#x}
    pop {{r4, pc}}

line_put:                   @ r0 a line, r1 its text: a new slot at the line's place and screen
    push {{r4, r5, r6, lr}}
    sub sp, sp, #16
    mov r5, r0
    mov r6, r1
    mov r0, #0
    str r0, [r5]
    bl {FREE_SLOT:#x}
    cmn r0, #1
    beq put_end
    mov r4, r0
    mov r0, #0x80
    bl {ALLOC:#x}
    bl {ARROW_SLOT:#x}
    add r1, r4, #1
    str r1, [r5]
    str r0, [r5, #4]
    cmp r0, #0
    beq put_end
    mov r1, #0xC
    str r1, [sp]
    mov r1, #1
    str r1, [sp, #4]
    mov r1, #0
    str r1, [sp, #8]
    str r6, [sp, #12]
    ldr r1, [r5, #16]       @ r0 is still the buffer, as TEXT_CREATE wants
    ldr r2, [r5, #20]
    ldr r3, [r5, #12]
    bl {TEXT_CREATE:#x}
put_end:
    add sp, sp, #16
    pop {{r4, r5, r6, pc}}

.ltorg
x_line:                     @ slot + 1, buffer, what it shows, screen mode, centre x, top y
.word 0, 0, 0, 0, {CAMP_X_AT[0]}, {CAMP_X_AT[1]}
n_line:
.word 0, 0, 0, {TOP_TEXT}, 128, {CAMP_NAME_Y}
n_texts:
.word n_0, n_1, n_2
n_cur:
.word -1
x_text:
.short {entext.X_TOKEN:#x}, 0xFFFD
.align 2
{names}
"""


def camp_keep_src(var):
    return f"""
    b keep_begin
    b keep_end
    b keep_save
    b keep_costume

keep_begin:                 @ the hero walking the map when camp opens
    ldr r1, [r12, #{PLAYER}]
    ldr r1, [r1, #0x81C]
    ldr r12, ={CAMP_DATA:#x}
    str r1, [r12]
    mov r1, #0
    str r1, [r12, #4]
    b {CAMP_START:#x}

keep_end:                   @ camp closing: the hero chosen with A or Y, else the one from before camp
    push {{r0, r1, r2, r3, lr}}    @ (at camp the costume never loads: it blanks sprites)
    ldr r12, ={CAMP_DATA:#x}
    ldr r1, [r12]
    ldr r2, [r12, #4]
    ldr r12, ={var:#x}
    ldr r3, [r12, #{HERO}]
    add r3, r3, #1
    cmp r2, r3
    subeq r1, r2, #1
    ldr r0, [r12, #{PLAYER}]
    cmp r0, #0
    beq keep_done
    ldr r3, [r0, #0x81C]
    cmp r3, r1
    beq keep_done
    mov r2, #1
    mov r3, #1
    bl {SET_COSTUME:#x}
keep_done:
    pop {{r0, r1, r2, r3, lr}}
    b {CAMP_LEAVE:#x}       @ then the portrait of who is played, before the fade back in

keep_costume:               @ the camp script asking who is being played: leaving shows them again
    ldr r12, ={var:#x}
    ldr r1, [r12, #{CAMP}]
    cmp r1, #0
    beq keep_save
    ldr r1, ={CAMP_DATA:#x}
    ldr r1, [r1]
    cmp r1, #2
    bhi keep_save
    str r1, [r12, #{HERO}]      @ the cursor is on them now, and its glide spot is over them
    ldr r3, [r12, #{CAMP_SEL}]
    cmp r3, #5                  @ the camel asked: the cursor stays on it
    beq keep_glide
    str r1, [r12, #{CAMP_SEL}]
    mov r0, lr
    cmp r3, #3                  @ leaving from Save: its green rim goes too
    bleq {CAMP_RIM:#x}
    mov lr, r0
keep_glide:
    adr r3, keep_tops
    add r3, r3, r1, lsl #1
    ldrb r1, [r3]
    lsl r1, r1, #12
    str r1, [r12, #{AX}]
    ldrb r1, [r3, #1]
    lsl r1, r1, #12
    str r1, [r12, #{AY}]
    mov r1, #0
    str r1, [r12, #{GLIDE}]
keep_save:                  @ a save at camp stores the hero from before it
    ldr r12, ={var:#x}
    ldr r1, [r12, #{CAMP}]
    cmp r1, #0
    ldrne r12, ={CAMP_DATA:#x}
    ldrne r0, [r12]
    bxne lr
    ldr r0, [r0, #0x81C]
    bx lr

.ltorg
keep_tops:                  @ where the scene puts the arrow for each hero
.byte 195, 126, 77, 127, 181, 31, 0, 0
"""


def camp_hearts_src(var):
    """The hearts at camp: for a hero under the cursor who isn't the one played (the costume
    only changes as camp closes), their saved health (hero block +0, the object's +0xBC) and
    maximum: as the game's FUN_02090ABC, but with that hero's own gear (block +0x8C and +0x90,
    the player's +0xE08 and +0xE0C) and base (+4, the object's +0xC0). Each hero wears their
    own gear; with the player's gear instead, Jasmine showed 13 hearts in 12 containers, and the
    gauge then rebuilt itself from the card every frame (a save deadlocked against it).
    A switch of whose hearts show uses the gauge's own instant mode (FUN_02095D24's second
    argument, kept in r5): no fill or drain."""
    return f"""
    b heart_cur
    b heart_max

heart_cur:                  @ for bl {HP_OF:#x}: r0 the player (the gauge's own object)
    push {{r1, r2, r3, lr}}
    ldr r12, ={SAVE_GAUGE:#x}
    str r0, [r12]           @ for the save's hold
    mov r3, r0
    bl {HP_OF:#x}
    bl camp_other
    cmp r2, #0
    movne r5, #1            @ whose hearts show just changed: set them at once
    cmp r1, #0
    ldrne r0, [r1]
    pop {{r1, r2, r3, pc}}

heart_max:                  @ for blx r8 (the maximum with gear): r0 the player
    push {{r4, r5, r6, lr}}
    mov r4, r0
    blx r8
    mov r5, r0
    mov r3, r4
    bl camp_other
    movs r6, r1
    moveq r0, r5            @ the hero played: the game's own
    popeq {{r4, r5, r6, pc}}
    mov r0, r4
    mov r1, #1
    ldr r2, [r6, #0x8C]     @ their gear slot 1
    bl {GEAR_BONUS:#x}
    mov r5, r0
    mov r0, r4
    mov r1, #2
    ldr r2, [r6, #0x90]     @ and slot 2
    bl {GEAR_BONUS:#x}
    add r0, r0, r5
    ldr r1, [r6, #4]        @ and their base
    add r0, r0, r1
    pop {{r4, r5, r6, pc}}

camp_other:                 @ r3 the player: r1 the cursor's hero's block, or 0; r2 1 if that changed
    ldr r12, ={var:#x}
    ldr r1, [r12, #{CAMP}]
    cmp r1, #0
    beq other_set
    ldr r2, [r12, #{HERO}]
    cmp r2, #2
    movhi r1, #0
    bhi other_done
    ldr r1, [r3, #0x81C]
    cmp r1, r2
    moveq r1, #0
    beq other_done
    ldr r1, ={HERO_BLOCKS:#x}
    mov r12, #{HERO_BLOCK}
    mla r1, r2, r12, r1
other_done:                 @ while the card is in use (a save), the hearts keep what they show:
    ldr r2, ={CARD_LOCKS:#x}    @ a change rebuilds the gauge, which reads its files from the card,
    ldr r2, [r2, #8]        @ and waiting on it there (holding the graphics lock) hangs the game
    cmn r2, #3
    ldrne r1, other_last
other_set:
    ldr r2, other_last
    subs r2, r1, r2
    movne r2, #1
    str r1, other_last
    bx lr
.ltorg
other_last:
.word 0
"""


def save_hold_src():
    """For the save thread's bls after cmp r8, #0x3c (r8 its frames so far): the game's 60 frames
    of "Saving..." are dropped. The write waits only for the camp's portrait and the hearts, never
    for ever. The hearts are settled when the gauge (SAVE_GAUGE) shows its target (+0x1194 target,
    +0x1198 shown) and has the containers for it (+0x1190): otherwise it reads the card again."""
    return f"""
    cmp r8, #{SAVE_HOLD_MAX}
    bxhi lr
    ldr r0, ={DEFER + 24:#x}    @ d_mode: a portrait still waiting for the cursor to rest (camp's input
    ldr r1, [r0]            @ doesn't run behind the save screen): load it now, as scripts do
    cmp r1, #0
    beq hearts_check
    mov r1, #1
    str r1, [r0, #-8]       @ d_left: due on this tick
    push {{lr}}
    bl {DEFER_TICK + 4:#x}
    pop {{lr}}
    b hold                  @ checked again next frame
hearts_check:
    ldr r12, ={SAVE_GAUGE:#x}
    ldr r12, [r12]
    cmp r12, #0
    bxeq lr
    add r12, r12, #0x1000
    ldr r0, [r12, #0x194]
    ldr r1, [r12, #0x198]
    cmp r0, r1
    bne hold
    ldr r0, [r12, #0x190]
    cmp r0, r1
    bxge lr                 @ settled: the write
hold:
    ldr lr, ={SAVE_WRITE_SKIP:#x}
    bx lr
.ltorg
"""


def camp_leave_src():
    """Camp closing (sb_CallCamp's unload, so the script can wait): the portrait last shown may be
    another hero's, or the state worked out from their saved values; if it isn't what the hero
    now played gets from the game, load theirs, as sb_SetSubScreen does, before the fade back in."""
    return f"""
    push {{r0, r1, r2, r3, r4, r5, r6, lr}}
    sub sp, sp, #8
    ldr r0, ={EVENTS:#x}
    bl {PARTY_LEAD:#x}
    movs r4, r0
    beq leave_end
    bl {COSTUME_OF:#x}
    mov r5, r0
    mov r0, r4
    bl {BIO_OF:#x}
    mov r6, r0
    ldr r0, ={EVENTS:#x}
    ldr r1, [r0, #0x164]    @ what PORTRAIT_LOAD last stored: costume, then state
    ldr r2, [r0, #0x168]
    cmp r1, r5
    cmpeq r2, r6
    beq leave_end
    mov r1, #6              @ the game's own wait, which frees the files
    str r1, [sp]
    ldr r1, [r0, #0x160]    @ the same screen mode
    mov r2, r5
    mov r3, r6
    bl {PORTRAIT_LOAD:#x}
leave_end:
    add sp, sp, #8
    pop {{r0, r1, r2, r3, r4, r5, r6, lr}}
    b {CAMP_END:#x}
.ltorg
"""


def camp_move_src():
    """r0 the camp's move table, r1 the direction, r10 the spot now, r9 our vars: r2 the spot that
    way. 6 is back to the selected hero; a hero the scene left out (the camp script shows Barda and
    Jasmine by party flags) is passed over the same way, so Left from Lief reaches the camel.
    +4, camp opening (r5 the camp's first value, r12 and r1 kept for keep_begin): the script
    shows Lief alone when that value is 32 (the Valley of the Lost), whatever the party flags."""
    return f"""
    b move
    cmp r5, #32
    moveq r3, #1
    movne r3, #0
    str r3, lone
    b {CAMP_KEEP:#x}
lone:
.word 0
move:
    push {{r0, lr}}
    add r12, r0, r10, lsl #2
    ldrb r2, [r12, r1]
    cmp r2, #6
    ldreq r2, [r9, #{HERO}]
move_check:
    cmp r2, #1
    moveq r3, #{BARDA_BIT}
    beq move_flag
    cmp r2, #2
    bne move_end
    mov r3, #{JASMINE_BIT}
move_flag:
    ldr r12, lone
    cmp r12, #0
    bne not_there
    ldr r12, ={SCRIPT_LONGS:#x}
    ldr r12, [r12]
    cmp r12, #0
    beq move_end
    ldr r12, [r12, #{PARTY_GROUP * 8}]
    mov lr, #1
    tst r12, lr, lsl r3
    bne move_end
not_there:
    ldr r0, [sp]            @ not there: on past them, the same way
    add r12, r0, r2, lsl #2
    ldrb r3, [r12, r1]
    cmp r3, r2
    moveq r2, r10           @ nowhere further: stay
    beq move_end
    mov r2, r3
    b move_check
move_end:
    pop {{r0, pc}}
.ltorg
"""


def camp_rim_src():
    return f"""
    ldr r3, [r12, #{SIGN}]      @ r12 is the vars; as camp's sign() does
    cmp r3, #0
    bxeq lr
    add r3, r3, #0x200
    push {{r1}}
    mov r1, #0
    str r1, [r3, #0xE8]
    mvn r1, #0
    str r1, [r3, #0xEC]
    mov r1, #0x1000
    str r1, [r3, #0xF0]
    pop {{r1}}
    bx lr
"""


def camp_src():
    return f"""
camp:                       @ campfire scene, script 2595
    bl tick
    ldr r0, [r9, #{LIVE}]
    mov r1, #0
    str r1, [r9, #{LIVE}]
    cmp r0, #0
    bne camp_live
    ands r0, r7, #0xF0      @ scene busy: keep the press until it can act
    strne r0, [r9, #{PEND}]
    tst r7, #1              @ or a Yes/No prompt
    movne r5, #144
    movne r6, #160
    bne {ON:#x}
    tst r7, #2
    movne r5, #{BAG_X}
    movne r6, #{BAG_Y}
    bne {ON:#x}
    b {OFF:#x}
camp_live:
    ldr r0, [r9, #{RETRY}]  @ a hero tap can land while the scene is busy: check it took
    cmp r0, #0
    beq camp_tapped
    bl {SHOWN_CODE + 4:#x}   @ NE once the scene shows the hero tapped
    mov r0, r0
    mov r0, r0
    bne camp_taken
    ldr r1, [r9, #{RETRY_N}]
    subs r1, r1, #1
    str r1, [r9, #{RETRY_N}]
    bne camp_keys
    mov r1, #4
    str r1, [r9, #{RETRY_N}]
    sub r2, r0, #1
    b {CAMP2_CODE + 12:#x}
camp_taken:
    mov r0, #0
    str r0, [r9, #{RETRY}]
camp_tapped:
    ldr r0, [r9, #{TAP2}]
    cmp r0, #0
    beq camp_keys
    ldr r1, [r9, #{WAIT}]
    subs r1, r1, #1
    str r1, [r9, #{WAIT}]
    bne camp_keys
    mov r1, #0
    str r1, [r9, #{TAP2}]
    mov r1, #1
    str r1, [r9, #{ARM}]
    and r5, r0, #0xFF
    lsr r6, r0, #8
    b {ON:#x}
camp_keys:
    ldr r0, [r9, #{PEND}]
    orr r7, r7, r0
    mov r0, #0
    str r0, [r9, #{PEND}]
    mov r1, #4
    tst r7, #0x10
    movne r1, #0
    tst r7, #0x20
    movne r1, #1
    tst r7, #0x40
    movne r1, #2
    tst r7, #0x80
    movne r1, #3
    cmp r1, #4
    beq {CAMP2_CODE + 8:#x}
    ldr r10, [r9, #{CAMP_SEL}]
    adr r0, camp_moves
    bl {CAMP_MOVE:#x}       @ r2: the spot that way
    cmp r2, #3              @ no Save at camp type 2
    bne not_save
    ldr r0, [r9, #{CAMP_KIND}]
    cmp r0, #2
    beq {CAMP2_CODE + 8:#x}
not_save:
    cmp r2, #5
    bne chosen_spot
    ldr r0, [r9, #{CAMEL}]
    cmp r0, #0
    beq {CAMP2_CODE + 8:#x}
chosen_spot:
    cmp r2, r10
    beq {CAMP2_CODE + 8:#x}
    str r2, [r9, #{CAMP_SEL}]
    cmp r10, #3             @ leaving Save: plain sign
    bne sign_off
    mov r0, #0
    bl sign
sign_off:
    ldr r2, [r9, #{CAMP_SEL}]
    cmp r2, #3              @ on Save: the sequence with the green rim
    bne sign_on
    mov r0, #1
    bl sign
sign_on:
    ldr r11, [r9, #{POINTER}]
    cmp r2, #3
    blo {CAMP2_CODE + 4:#x}
    b {CAMP2_CODE:#x}

sign:                       @ what the object's motion call stores; its update plays it
    ldr r3, [r9, #{SIGN}]
    cmp r3, #0
    bxeq lr
    add r3, r3, #0x200
    str r0, [r3, #0xE8]
    mvn r1, #0
    str r1, [r3, #0xEC]
    mov r1, #0x1000
    str r1, [r3, #0xF0]
    bx lr

tick:                       @ put the crow or caterpillar back once its animation ends
    push {{r4, lr}}
    ldr r4, [r9, #{HOLD_OBJ}]
    cmp r4, #0
    popeq {{r4, pc}}
    ldr r0, [r9, #{HOLD_MOTION}]
    cmn r0, #1
    popeq {{r4, pc}}
    mov r0, r4
    mov r1, #1
    bl {MOTION_BUSY:#x}
    cmp r0, #0
    popne {{r4, pc}}
    ldr r12, [r4]
    ldr r12, [r12, #0x90]
    mov r0, r4
    blx r12
    ldr r0, ={EVENTS:#x}
    mov r1, r4
    ldr r2, [r9, #{HOLD_MOTION}]
    bl {SET_MOTION:#x}
    mov r0, r4
    bl {MOTION_LOOP:#x}
    mov r0, #0
    str r0, [r9, #{HOLD_OBJ}]
    pop {{r4, pc}}

.ltorg
camp_moves:                 @ right, left, up, down for Lief, Barda, Jasmine, Save, Back, camel; X saves, so the cursor skips Save
.byte 0, 1, 2, 0
.byte 0, 5, 2, 1
.byte 2, 1, 2, 0
.byte 3, 6, 3, 0
.byte 4, 0, 0, 4
.byte 1, 5, 1, 5
"""


def camp2_src():
    return f"""
    b place
    b to_hero
    b camp_input
    b camp_tap

place:
    mov r0, #1
    str r0, [r9, #{SE_REQ}]
    ldr r1, [r9, #{GLIDE}]
    cmp r10, #3             @ remember where the arrow sat over the hero
    bhs placed
    str r0, [r9, #{POSE_REQ}]
    cmp r1, #0              @ mid-glide, the spot is already saved
    bne placed
    ldr r0, [r11, #0x220]
    str r0, [r9, #{AX}]
    ldr r0, [r11, #0x224]
    str r0, [r9, #{AY}]
placed:
    mov r0, #0
    str r0, [r9, #{GLIDE}]
    str r0, [r9, #{TAP2}]
    adr r1, camp_places
    sub r0, r2, #3
    add r1, r1, r0, lsl #1
    ldrb r0, [r1]           @ the camp's objects use plain screen coordinates
    ldrb r1, [r1, #1]
    lsl r0, r0, #12
    str r0, [r11, #0x220]
    lsl r1, r1, #12
    str r1, [r11, #0x224]
    b camp_input

to_hero:
    mov r0, #0
    str r0, [r9, #{RETRY}]      @ a move cancels the retry of a hero tap already sent
    cmp r2, #1
    ldreq r0, ={58 | 178 << 8:#x}   @ Barda: the caterpillar
    cmp r2, #2
    ldreq r0, ={156 | 44 << 8:#x}   @ Jasmine: the crow
    str r0, [r9, #{TAP2}]
    mov r0, #{CAMP_PET_DELAY}    @ after the portrait has changed
    str r0, [r9, #{WAIT}]
    bl {SHOWN_CODE:#x}      @ the scene's hero, not our guess: a tap on them would confirm
    cmp r0, r2
    streq r2, [r9, #{HERO}]
    bne new_hero
    mov r0, #1
    str r0, [r9, #{SE_REQ}]
    mov r0, #2
    str r0, [r9, #{POSE_REQ}]
    bl {ACTIONS_CODE + 16:#x}    @ already selected: a tap here would confirm, so glide here
    cmp r10, #3
    beq camp_input
    ldr r0, [r9, #{AX}]
    ldr r1, [r11, #0x220]
    sub r0, r0, r1
    asr r0, r0, #3
    str r0, [r9, #{GLIDE_X}]
    ldr r0, [r9, #{AY}]
    ldr r1, [r11, #0x224]
    sub r0, r0, r1
    asr r0, r0, #3
    str r0, [r9, #{GLIDE_Y}]
    mov r0, #8
    str r0, [r9, #{GLIDE}]
    b camp_input
new_hero:                   @ the scene moves the arrow; its costume and portrait wait for the cursor to rest
    bl {ACTIONS_CODE + 16:#x}
    ldr r2, [r9, #{CAMP_SEL}]
    str r2, [r9, #{HERO}]
    add r0, r2, #1
    str r0, [r9, #{RETRY}]
    mov r0, #4
    str r0, [r9, #{RETRY_N}]
    b camp_tap

camp_input:
    b {CAMP_BACK:#x}
camp_tap:
    adr r1, camp_spots
    add r1, r1, r2, lsl #1
    ldrb r5, [r1]
    ldrb r6, [r1, #1]
    b {ON:#x}

.ltorg
camp_places:                @ where the arrow goes: Save moves it off screen; unused; camel
.byte 240, 224, 0, 0, {CAMEL_SPOT[0]}, {CAMEL_SPOT[1]}, 0, 0
camp_spots:                 @ tap points
.byte 195, 134, 77, 134, 181, 40, 240, 18, 240, 176, 19, 115
"""


def patch_camp(script):
    """Camp, script 2595: leaving by the corner arrow first shows the hero from before camp
    again, so the leaving animation is theirs. The Muddlet's question changes nothing on screen;
    camp_keep_src's keep_end still gives back the hero from before camp. The new steps go after the file's
    end, and StartScript's length grows to reach them, since a function stops at its length."""
    b = bytearray(script)
    funcs, imports = scr.recs(b)
    main = scr.rec(b, funcs[0])
    assert main["name"] == "StartScript"
    code = main["code"]
    word = lambda i, n: list(struct.unpack_from(f"<{n}H", b, code + i * 2))
    play = [0x4000, 0, 0x4000, 100, 0x2102, 0x15, 0xA000]           # PlaySe(0, 100)
    ask = word(1201, 8)                                             # var 7 = GetCostume(0)
    assert ask == [0x601A, 7, 0x4000, 0, 0x2102, 0x11, 0x14, 0xA000]
    show = word(1935, 38)       # if var 14 != var 7: PlaySe, CharDisp(var 7, ...), var 14 = var 7
    assert show[:9] == [0x601A, 0xE, 0x601A, 7, 0xE, 0x101, 0x4001, 26, 0x103]
    assert show[-6:] == [0x601A, 0xE, 0x601A, 7, 0x14, 0xA000]
    # Type 3 (the Tower of Illusion's rest rooms) can save: var 23, Save's switch, was 0 for types
    # 2 and 3 (now 2 and 2), and its Adventure tips (204) become the list with X: Save (201)
    assert word(232, 9) == [0x601A, 1, 0x4000, 2, 0xD, 0x601A, 1, 0x4000, 3]
    struct.pack_into("<H", b, code + 240 * 2, 2)
    assert word(899, 4) == [0x601A, 0x18, 0x4001, 204]
    struct.pack_into("<H", b, code + 902 * 2, 201)
    if len(b) % 2:
        b.append(0)
    for site in (1660,):        # before the corner arrow's leave question; the Muddlet's (1741) shows nothing
        assert word(site, 7) == play
        at = (len(b) - code) // 2
        struct.pack_into("<2H", b, code + site * 2, 0x4001, at - site)
        struct.pack_into("<H", b, code + site * 2 + 4, 0x103)
        steps = play + ask + show
        back = site + 7 - (at + len(steps))
        b += struct.pack(f"<{len(steps)}H", *steps) + struct.pack("<3H", 0x4001, back & 0xFFFF, 0x103)
    struct.pack_into("<I", b, main["off"] + 16, (len(b) - code) // 2)
    # Adventure tips: MessageC(message | 0x80000000, y, ...) at y 60; one line (16) higher, so the
    # English list's Muddlet line still sits in the dark box
    tips = struct.pack("<3H", 0x11, 0x4000, CAMP_TIPS_Y_WAS)
    sites = [i for i in range(code, len(b) - 5, 2) if b[i:i + 6] == tips]
    assert len(sites) == 6, sites
    for i in sites:
        struct.pack_into("<H", b, i + 4, CAMP_TIPS_Y)
    return bytes(b)
SIGN_OBJ = 57                          # the signpost SpawnObj puts up in other stages (scripts 2485, 2614)
