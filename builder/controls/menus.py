"""Menus: the D-pad cursor, item lists, prompts and their arrows.

Part of the controls namespace (see __init__.py): names from every part are shared."""

KEY_COLS, KEY_COLS_ROOM = 0x02212B90, 60
WHO_COL, WHO_COL_ROOM = 0x02212BD0, 112
ARROW_SLOT, ARROW_SLOT_ROOM = 0x02212C40, 56
ARROW_ONLY, ARROW_ONLY_ROOM = 0x02212C78, 48
TEXT_OAM_SITE, TEXT_OAM = 0x0204E648, 0x0204E97C     # a text strip's eight 32x16 sprites
ARROW_REDRAW, ARROW_REDRAW_ROOM = 0x02215B00, 0xA0   # the menu arrow's tiles sent again while shown
ARROW_REFRESH = True
DEFER, DEFER_ROOM = 0x02212DA0, 0xE0   # free between CAMP_PICK and CAMP_BACK
PROMPT_SITES = 0x0204EBE0, 0x0204E690
TEXT_BUFS = 0x022156F0        # the buffer each of our text slots was given: the menu arrow, then the 6 option lines
ITEM_SLIDE, ITEM_SLIDE_ROOM = 0x02211A7C, 180    # the end of the MAT block
ITEM_SLIDE2, ITEM_SLIDE2_ROOM = 0x022121B4, 32   # the end of the POSE block
ITEM_SLIDE3, ITEM_SLIDE3_ROOM = 0x02212870, 28   # the end of the SHOP_YN2 block
DEFER_TICK, DEFER_TICK_ROOM = 0x022168E0, 0x180    # the camp's held costume and portrait, each idle frame (+4: the save's hold); CAMP_HEARTS took its old spot
CURSOR_CODE, CURSOR_ROOM = 0x022153E0, 0x150     # moved to the 20 KB block's end
SHOWN_CODE, SHOWN_ROOM = 0x02215530, 0x90       # which hero the camp scene really shows
KEY_COLS2, KEY_COLS3 = 0x02210CAC, 0x02212A00      # ends of the ICON_SEQ and ICONS2 blocks
ICONS_CODE, ICONS_ROOM = 0x022126B8, 144
ICONS2_CODE, ICONS2_ROOM = 0x022129D4, 60       # ScDebugPrint, unused
TEXT_SLOTS = 0x020D2024
FREE_SLOT = 0x02033360
ALLOC = 0x02035350
TEXT_CREATE = 0x0204C718
TEXT_FREE = 0x0203338C
ARROW_TOKEN = 0x3FF
TEXT_HEAP, HEAP_ALLOC = 0x020D4164, 0x020352D8     # as Text_Create gets its render buffer
TEXT_CLEAR, TEXT_RENDER, TEXT_UPLOAD = 0x0204C1F0, 0x0204DACC, 0x0204CE58


def icons_src():
    return f"""
    b show
    b hide
    b special

special:                    @ an attack only becomes a special with R held, or a shout
    add r1, r0, #0x1200
    ldr r1, [r1, #{MIC_LEVEL - 0x1200:#x}]
    cmp r1, #0x1F
    bgt {IS_PEAK:#x}
    mov r0, #0
    bx lr

show:                       @ r4 the menu, r7 the selection; only that icon animates
    push {{r5, lr}}
    ldr r5, =shown
    ldr r0, [r5]
    cmp r0, r7
    beq show_end
    str r7, [r5]
    cmp r0, #0
    blt show_new
    mov r2, #0
    bl {ICON_SEQ:#x}
show_new:
    mov r0, r7
    mov r2, #0x1000
    bl {ICON_SEQ:#x}
show_end:
    pop {{r5, pc}}

hide:
    ldr r0, =shown
    mvn r1, #0
    str r1, [r0]
    bx lr

.ltorg
shown:
.word -1
"""


def icon_seq_src():
    return f"""
icon:                       @ r0 selection, r2 speed; restarts the sequence
    push {{lr}}
    sub sp, sp, #12
    adr r3, seqs
    ldrb r1, [r3, r0]
    cmp r0, #4
    moveq r0, #5
    mov r3, #0x44
    mul r0, r3, r0
    add r0, r0, r4
    add r0, r0, #0x1000
    ldr r0, [r0, #0x98]
    b {ICONS2_CODE + 16:#x}

.ltorg
seqs:
.byte 0, 1, 2, 4, 5, 0, 0, 0
"""


def icon_still_src():
    return f"""
still:                      @ the menu's setup: icons start on their first frame
    push {{lr}}
    sub sp, sp, #12
    ldr r0, [r0, #4]
    mov r2, #0
start_seq:
    cmp r0, #0
    beq icon_end
    mov r3, #0
    str r3, [sp]
    bl {SPRITE_SEQ:#x}
icon_end:
    add sp, sp, #12
    pop {{pc}}
"""


def nav_src(var):
    return f"""
    b nav
    b aim

aim:                        @ touch-to-world for wall slides; under buttons, aim where we're heading
    ldr r12, ={PAD:#x}
    ldrh r12, [r12]
    tst r12, #0xF0
    beq {TO_WORLD:#x}
    ldr r12, ={var:#x}
    ldr r0, [r12, #{PLAYER}]
    ldr r1, [r12, #{MOVE_X}]
    ldr r2, [r0, #0x220]
    add r2, r2, r1, lsl #4
    str r2, [r3]
    ldr r1, [r12, #{MOVE_Y}]
    ldr r2, [r0, #0x224]
    add r2, r2, r1, lsl #4
    ldr r3, [sp]
    str r2, [r3]
    bx lr

nav:
    push {{r4, r5, r6, r7, lr}}
    mov r4, r0
    adr r5, sel
    bl {OPT_CODE + 12:#x}   @ the options gear and page; 1 skips this frame's moves, 2 the page too
    cmp r0, #1
    beq nav_end
    popgt {{r4, r5, r6, r7, pc}}
    ldr r0, [r4, #0x10]
    cmp r0, #2
    bne nav_off
    ldr r0, ={PAD:#x}
    ldrh r6, [r0, #2]
    mov r1, #4
    tst r6, #0x10
    movne r1, #0
    tst r6, #0x20
    movne r1, #1
    tst r6, #0x40
    movne r1, #2
    tst r6, #0x80
    movne r1, #3
    ldr r7, [r5]
    cmp r1, #4
    beq nav_draw
    adr r0, moves
    add r0, r0, r7, lsl #2
    ldrb r0, [r0, r1]
    cmp r0, r7
    beq nav_draw
    mov r7, r0
    str r7, [r5]
    bl {OPT_CODE + 16:#x}   @ the arrow goes, and the sub-menus' change of selection sound
nav_draw:
    bl {ICONS_CODE:#x}
    adr r2, spots
    add r2, r2, r7, lsl #1
    ldrb r0, [r2]
    ldrb r1, [r2, #1]
    bl {DRAW:#x}
    tst r6, #1
    beq nav_end
    cmp r7, #4
    moveq r7, #5
    add r1, r4, #0x1000
    str r7, [r1, #0x90]
    mov r0, #3
    str r0, [r4, #0x10]
    ldr r0, ={SOUND:#x}
    mov r1, #0
    mov r2, #100
    bl {PLAY_SE:#x}
nav_off:
    bl {ICONS_CODE + 4:#x}
    add r1, r4, #0x1000
    ldr r0, [r1, #0x90]
    mov r1, #1
    cmp r0, #4              @ closed: the next opening starts on Equip
    streq r1, [r5]
    bl {KILL:#x}
nav_end:
    mov r0, r4
    pop {{r4, r5, r6, r7, lr}}
    b {MENU_PAGE:#x}

.ltorg
moves:                      @ right, left, up, down for Mats, Equip, Key, Cards, Items
.byte 4, 0, 0, 0
.byte 2, 4, 1, 1
.byte 3, 1, 2, 2
.byte 3, 2, 3, 3
.byte 1, 0, 4, 4
spots:                      @ arrow centre x, top y
.byte 0x24, 0x41, 0x80, 0x41, 0xAE, 0x41, 0xDC, 0x41, 0x52, 0x41, 0, 0
sel:
.word 1
"""


def cursor_src():
    return f"""
cursor:
    push {{r0, r4, r5, r6, r7, r8, lr}}
    mov r4, r0
    ldr r1, [r4, #4]
    ldr r2, [r4, #0x10]
    ldr r5, ={GRID:#x}
    cmp r1, #6
    cmpeq r2, #3
    beq active
    ldr r5, ={WHO:#x}
    cmp r1, #7
    cmpeq r2, #3
    beq active
    cmp r1, #9
    bne idle
    ldr r0, [r4, #0x14]
    ldr r5, ={CARD:#x}
    cmp r2, #3
    cmpeq r0, #0
    bne not_card
    bl {LIST_SYNC + 4:#x}    @ X: Item Info (and the list cursor follows on return)
    b active
not_card:
    ldr r5, ={BOOK:#x}
    cmp r2, #2
    cmpeq r0, #5
    bne idle
    bl {LIST_SYNC:#x}        @ pages opened from the list start on the notes; cursor follows
    b active
idle:
    cmp r1, #3
    blne {KILL:#x}
    pop {{r0, r4, r5, r6, r7, r8, lr}}
    push {{r4, lr}}
    b {DISPATCH + 4:#x}

active:
    ldr r0, ={PAD:#x}
    ldrh r6, [r0, #2]
    ldrb r7, [r5, #{COL}]
    ldrb r8, [r5, #{ROW}]
    ldrb r0, [r5, #{COLS}]
    ldrb r1, [r5, #{ROWS}]
    mov r2, #0              @ moved
    mov r3, #0              @ book tab step
    tst r6, #0x10
    beq not_right
    mov r2, #1
    add r7, r7, #1
    cmp r7, r0
    movge r7, #0
    movge r3, #1
not_right:
    tst r6, #0x20
    beq not_left
    mov r2, #1
    subs r7, r7, #1
    submi r7, r0, #1
    mvnmi r3, #0
not_left:
    tst r6, #0x40
    beq not_up
    mov r2, #1
    subs r8, r8, #1
    submi r8, r1, #1
not_up:
    tst r6, #0x80
    beq not_down
    mov r2, #1
    add r8, r8, #1
    cmp r8, r1
    movge r8, #0
not_down:
    ldrb r0, [r5, #{COLS}]
    cmp r0, #7              @ L and R turn the book's tabs
    bne not_tabs
    tst r6, #0x100
    movne r3, #1
    tst r6, #0x200
    mvnne r3, #0
not_tabs:
    cmp r2, #0
    beq position
    strb r7, [r5, #{COL}]
    strb r8, [r5, #{ROW}]
    push {{r2, r3}}
    bl {KILL:#x}
    pop {{r2, r3}}
position:
    b {PLACE_ENTRY:#x}

.ltorg
"""


def list_sync_src():
    """The card list, r4 the book, r5 its cursor table (7 columns): when the game's selected
    slot (book+0x1AF0) changes, from a card page's arrows or a stylus tap, the D-pad cursor
    moves to it. +4, each frame on a card page: the return always moves it. Each then goes
    on to the cards block's own entry (card_list, card_key)."""
    return f"""
    b sync
    mvn r0, #1
    str r0, slot
    b {CARDS_CODE + 20:#x}
sync:
    add r2, r4, #0x1000
    ldr r2, [r2, #0xAF0]
    cmp r2, #0
    blt synced
    ldr r3, slot
    cmp r2, r3
    beq synced
    str r2, slot
    mov r3, #0
row_of:
    subs r2, r2, #7
    addge r3, r3, #1
    bge row_of
    add r2, r2, #7
    strb r2, [r5, #{COL}]
    strb r3, [r5, #{ROW}]
synced:
    b {CARDS_CODE + 24:#x}
slot:
.word -2
"""


def next_item_src():
    return f"""
    add r2, r4, #0xAE0      @ r1 the item count: the newest goes to the back
    add r3, r2, r1, lsl #1
    ldrh r0, [r3, #-2]!
shift:
    ldrh r12, [r3, #-2]
    strh r12, [r3], #-2
    cmp r3, r2
    bne shift
    strh r0, [r2]
    b {ITEM_SLIDE:#x}
"""


def item_slide_src():
    return f"""
    push {{r5, r6, r7, r8, lr}}  @ r1 the count, r2 the list: the sprites follow it round
    sub sp, sp, #0x44
    add r5, r2, #0xC
    mov r6, r1
    sub r0, r6, #1
    add r0, r0, r0, lsl #4
    add r8, r5, r0, lsl #2
    mov r0, r8
    mov r1, sp
    bl copy
shift:
    sub r0, r8, #0x44
    mov r1, r8
    bl copy
    sub r8, r8, #0x44
    cmp r8, r5
    bne shift
    mov r0, sp
    mov r1, r5
    bl copy
    mov r7, #0
    add r8, r4, #0xC40
slide:                      @ each one glides from where it is, as after using an item
    mov r0, r4
    mov r1, r5
    add r2, r8, #4
    bl {ITEM_POS:#x}
    sub r3, r6, r7
    subs r3, r3, #1
    moveq r0, #0xEC000
    moveq r1, #0x10000
    moveq r2, #0x100
    movne r0, #0xE6000
    subne r0, r0, r3, lsl #16
    movne r1, #0xA000
    mvnne r2, #0xFF
    str r2, [r8]
    str r0, [r8, #0x10]
    str r1, [r8, #0x14]
    mov r0, #8
    str r0, [r8, #0x1C]
    mov r0, #0
    str r0, [r8, #0x20]
    b {ITEM_SLIDE2:#x}
copy:
    mov r2, #0x44
    b {COPY:#x}
"""


def item_slide2_src():
    return f"""
    add r5, r5, #0x44
    add r8, r8, #0x24
    add r7, r7, #1
    cmp r7, r6
    blt {ITEM_SLIDE + 84:#x}
    mov r0, #6              @ the bar's rearranging state
    str r0, [r4, #0xD60]
    b {ITEM_SLIDE3:#x}
"""


def item_slide3_src():
    return f"""
    add sp, sp, #0x44
    pop {{r5, r6, r7, r8, lr}}
    ldr r0, ={SOUND:#x}
    mov r1, #0
    mov r2, #0x67           @ the item menus' cursor sound
    b {PLAY_SE:#x}

.ltorg
"""


def key_cols_src():
    return f"""
    ldrb r12, [r5, #{COLS}]
    cmp r12, #9             @ the card page's left and right arrows
    beq {CARD_COL:#x}
    cmp r12, #3             @ who gets an item
    beq {WHO_COL:#x}
    cmp r12, #8
    bxne lr
    ldr r12, [r4]           @ Key items: the right half is the note paper, stylus only
    cmp r12, #2
    bxne lr
    cmp r7, #4
    bxlt lr
    b {KEY_COLS2:#x}
"""


def who_col_src():
    return f"""
    push {{r10, r11, lr}}    @ the cursor only stops on someone who is here and can use it
    mov r10, #3
    ldr r0, ={PLAYER_DATA:#x}
    bl {GET_PARTY:#x}
    mov r11, r0
who_next:
    ldr r0, [r4, #0x9C]
    mov r1, #1
    tst r0, r1, lsl r7
    beq who_skip
    mov r0, r11
    mov r1, r7
    bl {IN_PARTY:#x}
    cmp r0, #0
    bne who_found
who_skip:
    tst r6, #0x20
    subne r7, r7, #1
    addeq r7, r7, #1
    cmp r7, #0
    movlt r7, #2
    cmp r7, #3
    movge r7, #0
    subs r10, r10, #1
    bne who_next
who_found:
    strb r7, [r5, #{COL}]
    pop {{r10, r11, pc}}

.ltorg
"""


def arrow_redraw_src():
    """Entered from DRAW when the arrow is already shown (r0 its slot + 1, DRAW's frame on the
    stack). Other graphics can land in the arrow's VRAM after its one upload (seen after
    battles), leaving garbage where it should be. So the arrow's 2 KB strip is rendered once
    into a buffer kept for good (the arrow never changes), and copied to its VRAM every frame
    it is shown: no allocation, rendering or queued upload per frame."""
    return f"""
    ldr r4, ={TEXT_BUFS:#x}
    ldr r4, [r4]
    ldr r1, ={TEXT_SLOTS:#x}
    sub r0, r0, #1
    ldr r1, [r1, r0, lsl #5]
    cmp r1, r4              @ the bag may have cleared all text: then the slot is not ours
    bne redraw_end
    cmp r4, #0
    beq redraw_end
    ldr r6, =copy
    ldr r5, [r6]
    cmp r5, #0
    bne send
    ldr r0, ={TEXT_HEAP:#x}
    mov r1, #0x800          @ the arrow's one 2 KB chunk
    mov r2, #4
    bl {HEAP_ALLOC:#x}
    movs r5, r0
    beq redraw_end
    str r5, [r6]
    mov r1, #0x800
    bl {TEXT_CLEAR:#x}
    mov r0, r4
    mov r1, r5
    mov r2, #0
    bl {TEXT_RENDER:#x}
    mov r0, r5
    mov r1, #0x800
    bl {DC_FLUSH:#x}        @ the copy is read by DMA
send:
    mov r0, r5
    ldr r1, [r4, #0x4c]     @ the strip's place in sprite VRAM
    mov r2, #0x800
    bl {LOAD_OBJ:#x}
redraw_end:
    add sp, sp, #16
    pop {{r4, r5, r6, pc}}

.ltorg
copy:
.word 0
"""


def arrow_only_src():
    return f"""
    ldr r12, [r9, #0x20]    @ r9 the text, r6 which sprite: the arrow needs only the middle two
    cmp r12, #0
    ldrhne r12, [r12]
    add r12, r12, #1
    cmp r12, #{ARROW_TOKEN + 1:#x}
    bne {TEXT_OAM:#x}
    sub r12, r6, #3
    cmp r12, #1
    bls {TEXT_OAM:#x}
    mov r12, #0x200         @ the others stay hidden: their tiles can hold anything
    str r12, [r0]
    bx lr
"""


def prompt_reset_src():
    return f"""
    ldr r0, [r5, #{SAVE_SEL}]   @ Yes/No starts on Yes, or on No when deleting a file
    tst r0, #4
    moveq r0, #1
    movne r0, #0
    cmp r0, r0              @ the caller's next steps need Z set
    bx lr
"""


def shown_src():
    return f"""
    b shown
    b retry_check

shown:                      @ r0: the hero the camp scene shows, from the mob in the selected pose
    push {{r1, r2, r3, lr}}
    ldr r1, [r9, #{SEL_MOB}]
    cmp r1, #0
    beq shown_guess
    ldr r0, ={WORLD:#x}
    bl {FIND_MOB:#x}
    cmp r0, #0
    beq shown_guess
    ldr r1, [r0, #0x224]    @ camp objects use screen coordinates: Lief (195, 161), Barda (77, 163), Jasmine (181, 66)
    ldr r0, [r0, #0x220]
    asr r1, r1, #12
    asr r0, r0, #12
    cmp r1, #110
    movlt r0, #2
    blt shown_end
    cmp r0, #136
    movlt r0, #1
    movge r0, #0
    b shown_end
shown_guess:                @ before the scene's first pose
    ldr r0, [r9, #{HERO}]
shown_end:
    pop {{r1, r2, r3, pc}}

retry_check:                @ flags NE once the scene shows the hero a retry is for (RETRY - 1)
    push {{r0, r1, r2, r3, lr}}
    bl shown
    ldr r1, [r9, #{RETRY}]
    sub r1, r1, #1
    cmp r0, r1
    moveq r0, #1
    movne r0, #0
    cmp r0, #0
    pop {{r0, r1, r2, r3, pc}}

.ltorg
"""


def defer_src(var):
    return f"""
    b costume_hook
    b {DEFER_TICK:#x}
    b defer_leave
    b portrait_hook
d_left:                     @ DEFER + 16: idle frames until the costume and portrait load
.word 0
d_costume:                  @ + 20: the hero under the cursor, for the portrait (the costume changes as camp closes), or -1
.word -1
d_mode:                     @ + 24: the portrait's screen mode waiting, or 0
.word 0
d_free:                     @ + 28: frames until the loaded portrait's files are freed
.word 0
d_ready:                    @ + 32: set by the camp's first portrait, which loads the normal way
.word 0

costume_hook:               @ sb_SetCostume's SET_COSTUME: at camp, only once the cursor rests
    ldr r12, ={var:#x}
    ldr r12, [r12, #{CAMP}]
    cmp r12, #0
    beq {SET_COSTUME:#x}
    ldr r12, d_ready
    cmp r12, #0
    beq {SET_COSTUME:#x}
    str r1, d_costume
    mov r0, #{CAMP_TAP_DELAY}
    str r0, d_left
    mov r0, #1
    bx lr

portrait_hook:              @ sb_SetSubScreen's portrait load (FUN_0203d390): the same
    ldr r12, ={var:#x}
    ldr r12, [r12, #{CAMP}]
    cmp r12, #0
    beq {PORTRAIT_LOAD:#x}
    ldr r12, d_ready
    cmp r12, #0
    moveq r12, #1
    streq r12, d_ready      @ the opening's portrait: as the game loads it
    beq {PORTRAIT_LOAD:#x}
    str r1, d_mode
    mov r1, #{CAMP_TAP_DELAY}
    str r1, d_left
    bx lr

defer_leave:                @ the camp closing: free what's held, drop what waits
    push {{lr}}
    mov r0, #0
    str r0, d_left
    str r0, d_mode
    str r0, d_ready
    mvn r0, #0
    str r0, d_costume
    ldr r0, d_free
    cmp r0, #0
    mov r0, #0
    str r0, d_free
    blgt {PORTRAIT_FREE:#x}
    pop {{lr}}
    b {CAMP_X + 12:#x}

.ltorg
"""


def defer_tick_src():
    return f"""
    b defer_idle            @ each idle camp frame (the scene has finished moving the arrow), then the X prompt
    b tick_body             @ + 4: only the held work (the save's hold, on the save thread)
defer_idle:
    push {{lr}}
    bl tick_body
    pop {{lr}}
    b {CAMP_X + 4:#x}
tick_body:
    ldr r0, ={CARD_LOCKS:#x}    @ never while the card is in use (a save): the portrait's files
    ldr r0, [r0, #8]        @ come from it
    cmn r0, #3
    bxne lr
    push {{r4, r5, r6, lr}}
    sub sp, sp, #16
    ldr r6, ={DEFER + 16:#x}    @ d_left, d_costume, d_mode, d_free
    ldr r0, [r6, #12]
    subs r0, r0, #1
    bmi tick_wait
    str r0, [r6, #12]
    bne tick_wait
    bl {PORTRAIT_FREE:#x}   @ VRAM has the portrait: its files can go
tick_wait:
    ldr r0, [r6]
    subs r0, r0, #1
    bmi tick_end
    str r0, [r6]
    bne tick_end
    ldr r4, [r6, #8]
    cmp r4, #0
    beq tick_end
    mov r0, #0
    str r0, [r6, #8]
    ldr r0, ={EVENTS:#x}    @ as sb_SetSubScreen: the hero's portrait for their biorhythm
    bl {PARTY_LEAD:#x}
    mov r5, r0
    bl {COSTUME_OF:#x}
    ldr r1, [r6, #4]        @ the costume still waiting is the one to show
    cmn r1, #1
    movne r0, r1
    str r0, [sp, #4]
    ldr r1, [r5, #0x81C]
    cmp r0, r1
    beq tick_bio            @ the hero being played: their own biorhythm
    ldr r1, ={HERO_BLOCKS:#x}   @ another: BIO_OF on what their costume would bring back
    mov r2, #{HERO_BLOCK}
    mla r1, r0, r2, r1
    ldr r2, [r1, #{HERO_BIO} - 4]   @ their level count (FUN_020948C8's, at most 5)
    ldr r1, [r1, #{HERO_BIO}]       @ and value (+0x1054)
    add r1, r1, #0x20
    cmp r2, #5
    movgt r2, #5
    cmp r2, #2
    movlt r0, #0
    blt tick_load
    adr r3, bio_steps - 8   @ 4 thresholds a row, from 2 levels; the state is how many are reached
    add r3, r3, r2, lsl #2
    mov r0, #0
bio_count:
    ldrb r2, [r3, r0]
    cmp r1, r2
    blt tick_load           @ below this one: done
    add r0, r0, #1
    cmp r0, #4
    blt bio_count
    b tick_load
tick_bio:
    mov r0, r5
    bl {BIO_OF:#x}
tick_load:
    mov r3, r0
    mov r1, r4
    ldr r2, [sp, #4]
    mov r0, #0              @ no frame wait: the tick frees the files
    str r0, [sp]
    ldr r0, ={EVENTS:#x}
    bl {PORTRAIT_LOAD:#x}
    mov r0, #2
    str r0, [r6, #12]
tick_end:
    add sp, sp, #16
    pop {{r4, r5, r6, pc}}

.ltorg
bio_steps:                  @ BIO_OF's thresholds for 2, 3, 4 and 5 levels (255: none)
.byte 0x40, 255, 255, 255
.byte 0x2A, 0x54, 255, 255
.byte 0x20, 0x40, 0x60, 255
.byte 0x1A, 0x34, 0x4D, 0x67
"""


def arrow_slot_src():
    return f"""
    ldr r1, ={TEXT_SLOTS:#x}    @ the slot's other fields, as the game's own text sets them
    str r0, [r1, r4, lsl #5]
    add r1, r1, r4, lsl #5
    mov r2, #0
    str r2, [r1, #4]
    str r2, [r1, #12]
    str r2, [r1, #16]
    str r2, [r1, #20]
    str r2, [r1, #24]
    str r2, [r1, #28]
    mvn r2, #0
    str r2, [r1, #8]
    bx lr

.ltorg
"""
