"""The field: walking with the D-pad, talking with A, attacking with Y, the heads-up display.

Part of the controls namespace (see __init__.py): names from every part are shared."""

SLOW_CODE, SLOW_ROOM = 0x0221134C, 132     # SetTempoSeq, unused
CAP_EDGE, CAP_EDGE_ROOM = 0x02212CDC, 148
ALERT_DATA = 0x022145E0         # the low-health alert: frames since its sound started, that sound
ALERT_CODE, ALERT_ROOM = 0x022145E8, 280
TALK_REACH = 48         # A's limit for anyone without their own (tools/talk.py): chests, script-made people
TALK_LIMITS = 0x02210F08    # talk.table(): each placed character's own touch limit; the old cursor block's 328 bytes
TALK_BEHIND = 64        # ranking penalty for someone behind Lief
TALK_LOW = {2006: 256}  # record id: ranking penalty, so A picks others in reach first (the Grand Farm's dog: its farmer)
SPIKE_ATTACK, SPIKE_ATTACK_ROOM = 0x02215BA0, 0x60   # protected on spikes: taps and attacks work
SPIKE_A_SITE, SPIKE_B_SITE = 0x02098074, 0x02098084  # FUN_02097f58's test of the floor flags
BIO_KEEP, BIO_KEEP_ROOM = 0x02215C00, 0x140    # Pumpkin Soup's biorhythm MAX ends where each hero began
FS_CODE, FS_ROOM = 0x02216D60, 0xC0    # Final Slash's red circle half again as fast (the 26th kilobyte)
REACH_MORE, REACH_MORE_ROOM = 0x02217D60, 0x40   # A's ranking, continued: low-priority characters (REACH is full)
FS_MAKE_SITE = 0x02099468       # Final Slash (FUN_020990ec) state 3: the red circle (FUN_02034b00(0, 0x1f, 4, 4))
FS_TICK_SITE = 0x02099524       # its state 5: the frame count, + 1
FX_TIMER_SITE = 0x0201A55C      # the red circle (FUN_0201a2a4): a piece's frames left, - 1
FX_COUNT_SITE = 0x0201A5C0      # its frame count, + 1 (done after 0x30)
FX_TABLE = 0x020D1FA4           # the screen effects: (object, type) per id
FS_MARK = 98                    # its +0x6a (99 for a coloured one): Final Slash's, the fast one
# the lions' slides (FUN_0208c55c/540: speed, frames): 1.5 times the speed for two thirds of the frames
FS_SLIDES = ((0x020994F4, "mov r1, #0x6000", "mov r1, #0x9000"), (0x020994F8, "mov r2, #0xc", "mov r2, #8"),
             (0x02099628, "mov r1, #0x6000", "mov r1, #0x9000"), (0x0209962C, "mov r2, #0xc", "mov r2, #8"),
             (0x0209963C, "mov r1, #0x8000", "mov r1, #0xc000"), (0x02099648, "mov r2, #0xc", "mov r2, #8"),
             (0x02099658, "mov r1, #0x6000", "mov r1, #0x9000"), (0x02099664, "mov r2, #0xc", "mov r2, #8"),
             (0x02099678, "mov r1, #0x8000", "mov r1, #0xc000"), (0x0209967C, "mov r2, #0xc", "mov r2, #8"))
PICK_CODE, PICK_ROOM = 0x02215F60, 0x180   # the 23rd kilobyte: Y's enemy, not what lies on it
PICK_SITE = 0x020982EC          # FUN_02097f58: bl FUN_02096cd4, what a touch lands on
PICK_NEAR = 12                  # pixels (x + y) from the touch an enemy may be to take it
SCROLL_EDGE, SCROLL_EDGE_ROOM = 0x022160E0, 0x10  # auto-scroll: Lief kept whole on screen
SCROLL_EDGE_SITE = 0x0208158C   # FUN_02081418: ldr r3, [r0, #0x278], the screen's left edge
SCROLL_RIGHT_SITES = ((0x020815B8, "cmp r2, #0x100", "cmp r2, #0xe0"), (0x020815C0, "add r0, r3, #0x100", "add r0, r3, #0xe0"))
SCROLL_MARGIN = 16              # pixels in from each side
HEART_CUR_SITE, HEART_MAX_SITE = 0x02095D38, 0x02095D5C  # the hearts' health and maximum (FUN_02095D24)
HP_OF = 0x0208B79C             # an object's health, +0xBC; +0xC0 its own maximum, before gear
ATTACK_CAN, SET_TARGET, ATTACK_END = 0x0206D444, 0x020878C0, 0x0206D44C    # FUN_02096fc4's own steps
HUD_GUARD, HUD_GUARD_ROOM = 0x02214300, 160     # free space after the options block
HUD_TAP_SITE = 0x02098208      # the field's bag icon and item square read the touch here
ALERT_SITE = 0x02095BA0         # the alert's per-frame start cooldown (4 instructions)
ALERT_STOP = (96, 150)          # frames to just past the third beep: the 1-heart sound, the others
ALERT_EVERY = 300               # a new set of three beeps every 5 seconds
TALK_FLAGS = 2                  # tap paging, with the dark panel (0x80000 would drop it)
AREA_BATTLE = 0x021F00A8       # stage+0x6244: the monster area battle, while one runs
NEAREST = 0x020873F0           # nearest object of a hit-list type within a range
BATTLE_RANGE = 0x80000         # 128 px
BIO_CUE_SITES = (0x020943E0, 0x020943FC, 0x02094418, 0x020983A4, 0x020983C0, 0x020983DC)
ANIM_CODE, ANIM_ROOM = 0x022111D4, 256      # ReloadSavedSound and friends, unused
POSE_CODE, POSE_ROOM = 0x022120D8, 252      # SetAttackTarget and friends, unused
ACTIONS_CODE, ACTIONS_ROOM = 0x02211F54, 388    # MessageMobBlock, MessageMobC, MessageMobCBlock
OPEN, USE, CHARGE, CAP = (ACTIONS_CODE + i * 4 for i in range(4))
GATE_SITE = 0x020371C8
WALK_SITE = 0x020927D8
MIC_READ = 0x02094F00
MIC_SITE = 0x020924E4
MIC_LEVEL = 0x1294          # loudness; the game fires a special on a peak if this is over 0x1F
PLACE_ENTRY = PLACE_CODE
SHOUT = SHARED_CODE
CAP_SITE = 0x020939D4       # DO_MOVE applying its step
ATTACK_SPEED = (0x02092FE8, "moveq r0, #0x2400"), (0x02092FEC, "movne r0, #0x1800")    # was 0x1800, 0x1000
# FUN_02096cd4 picks the enemy a tap swings at, but only if it's already inside the
# attack's reach box; otherwise no swing starts and Lief just turns. Now any live
# enemy tapped gets a swing toward it, hitting whatever the swing reaches.
SWING_ANY = 0x02096F94, "b 0x2096fa4"     # was bne: the reach box test
PARTY_LEAD, COSTUME_OF, BIO_OF = 0x0203A9E0, 0x020903A0, 0x020947F8


def steer_src():
    return f"""
steer:                      @ a wall just ahead: angle 45 degrees along it if that way is open
    push {{r4, r5, r6, r7, r8, lr}}
    mov r4, r0
    mov r5, r1
    mov r6, r2
    mov r7, r3
    mov r1, #3
    bl probe
    cmp r0, #0
    beq steer_go
    mov r8, #1
steer_try:
    mul r0, r7, r8
    sub r2, r6, r0
    mul r0, r6, r8
    add r3, r7, r0
    mov r0, #0xB5           @ 0.707, 8.8 fixed point
    mul r2, r0, r2
    asr r2, r2, #8
    mul r3, r0, r3
    asr r3, r3, #8
    cmp r6, #0
    cmpne r7, #0            @ straight into a flat wall must not slip sideways, so look further
    moveq r1, #7
    movne r1, #3
    push {{r2, r3}}
    bl probe
    pop {{r2, r3}}
    cmp r0, #0
    beq steer_use
    cmp r8, #1
    bne steer_go
    mvn r8, #0
    b steer_try
steer_use:
    mov r6, r2
    mov r7, r3
    mov r0, #0x2000
    mul r0, r8, r0
    add r5, r5, r0
steer_go:
    mov r0, r4
    lsl r1, r5, #16
    lsr r1, r1, #16
    mov r2, r6
    mov r3, r7
    pop {{r4, r5, r6, r7, r8, lr}}
    b {SLOW_CODE:#x}

probe:                      @ r1 steps of (r2, r3) ahead of r4; r0 is 1 if that tile blocks
    push {{r5, r6, r7, lr}}
    ldr r5, [r4, #0x220]
    mla r5, r2, r1, r5
    ldr r6, [r4, #0x224]
    mla r6, r3, r1, r6
    ldr r0, ={STAGE_OWNER:#x}
    bl {GET_STAGE:#x}
    mov r1, r5
    mov r2, r6
    mov r3, #0
    bl {TILE_AT:#x}
    sub r0, r0, #1
    cmp r0, #13
    movlo r0, #1
    movhs r0, #0
    pop {{r5, r6, r7, pc}}

.ltorg
"""


def slow_src():
    return f"""
slow:                       @ SET_MOVE for the D-pad, with gentler slowdowns than a touch walk
    push {{r4, lr}}
    ldr r12, [r0, #0x6DC]
    tst r12, #8             @ poison
    beq slow_armour
    ldr r12, =0xCCC         @ 0.8 times
    bl scale
slow_armour:
    ldr r12, [r0, #0xE08]
    cmp r12, #4
    cmpne r12, #7
    cmpne r12, #10
    bne slow_done
    ldr r12, =0xE66         @ heavy armour: 0.9 times
    bl scale
slow_done:
    pop {{r4, lr}}
    b {SET_MOVE:#x}

scale:                      @ r12 the factor; both speeds and the step limit
    mul r2, r12, r2
    asr r2, r2, #12
    mul r3, r12, r3
    asr r3, r3, #12
    ldr r4, [sp, #8]
    mul r4, r12, r4
    asr r4, r4, #12
    str r4, [sp, #8]
    bx lr

.ltorg
"""

# Kept out of the assembly: keystone miscounts .byte data placed before branches.
PLACE_DATA = bytes((
    8, 4, 0x1C, 0x30, 24, 32, 0x20, 1, 0, 0, 0x16, 0,   # item grids
    3, 1, 0x84, 0xA8, 32, 0, 0, 0, 0, 0, 0x1C, 0,       # who gets it
    7, 4, 0x20, 0x28, 32, 40, 0, 1, 0, 0, 0x16, 0,      # card book
))


def bio_keep_src():
    """Pumpkin Soup (item 0x57) starts status timer 7 on the player, and while it runs every
    read of the biorhythm (FUN_0209490c) holds it at the top, 0x60. When the timer runs out,
    FUN_020a3310 set it to the bottom, -0x20, whatever it had been. The timer stays through
    hero changes, and a hero leaving has the held 0x60 saved in their record (+0x74).

    Now each hero's own biorhythm is kept the first time they are played under the soup (when
    it is drunk, or as they come in), and when it ends every hero gets theirs back: the one
    being played directly, the others in their records. A hero kept nothing for keeps -0x20."""
    return f"""
    b soup_end              @ +0: the timer has run out (r0 the player)
    b soup_drunk            @ +4: from the item (r0 the player, r1 7, r2 the time)
                            @ +8: SET_COSTUME (r0 the player, r1 the biorhythm, r6 the hero coming in)
    add r12, r0, #0xE00
    ldrh r12, [r12, #0x46]  @ timer 7 (+0xE38 + 14)
    cmp r12, #0
    beq {SET_BIO:#x}
    push {{r0, r1, lr}}
    mov r2, r6
    bl remember
    pop {{r0, r1, lr}}
    b {SET_BIO:#x}
soup_drunk:
    add r12, r0, #0xE00
    ldrh r12, [r12, #0x46]
    cmp r12, #0
    bne {SET_TIMER:#x}      @ already working: what is kept stays
    push {{r0, r1, r2, lr}}
    mov r3, #0
    str r3, kept            @ a new soup: nothing kept yet
    add r12, r0, #0x1000
    ldr r1, [r12, #0x54]    @ the biorhythm, +0x1054
    ldr r2, [r0, #0x81C]    @ of the hero being played
    bl remember
    pop {{r0, r1, r2, lr}}
    b {SET_TIMER:#x}
soup_end:
    push {{r4, r5, r6, r7, lr}}
    mov r4, r0
    ldr r2, [r0, #0x81C]
    bl slot_of
    mov r7, r2              @ the hero being played: given theirs below
    ldr r5, kept
    mov r0, #0
    str r0, kept
    adr r6, saved
    ldr r12, ={HERO_BLOCKS + HERO_BIO:#x}
    mov r3, #0
others:                     @ every other hero kept: their record
    cmp r3, r7
    beq next
    mov r0, #1
    tst r5, r0, lsl r3
    ldrne r0, [r6, r3, lsl #2]
    movne r1, #{HERO_BLOCK}
    mlane r1, r3, r1, r12
    strne r0, [r1]
next:
    add r3, r3, #1
    cmp r3, #4
    blt others
    mvn r1, #0x1F           @ nothing kept: the bottom, as before
    mov r0, #1
    tst r5, r0, lsl r7
    ldrne r1, [r6, r7, lsl #2]
    mov r0, r4
    pop {{r4, r5, r6, r7, lr}}
    b {SET_BIO:#x}
remember:                   @ r1 a biorhythm, r2 a hero (costume): kept, unless theirs is already
    push {{lr}}
    bl slot_of
    ldr r3, kept
    mov r12, #1
    tst r3, r12, lsl r2
    popne {{pc}}
    orr r3, r3, r12, lsl r2
    str r3, kept
    adr r3, saved
    str r1, [r3, r2, lsl #2]
    pop {{pc}}
slot_of:                    @ r2 a costume: its record slot, as FUN_02090358
    cmp r2, #6
    movhi r2, #7
    adr r3, slots
    ldrb r2, [r3, r2]
    bx lr
    .ltorg
kept:
    .word 0                 @ bit per slot: saved[slot] holds that hero's own biorhythm
saved:
    .word 0, 0, 0, 0
slots:
    .byte 0, 1, 2, 0, 1, 3, 3, 0
"""


def pick_src(var):
    """Y attacks by touching the nearest enemy's own spot (the scan before ON). Two things got
    in the way: an enemy in its death animation is still an enemy, so it could be the nearest,
    and the touch is the game's (FUN_02096cd4), so a dropped item or a dying enemy on that spot
    took it: Lief picked the item up, or twitched at the corpse.
    The touch could also give an item that wasn't at that spot at all: items' touch boxes are
    large, and in some states the game takes the first fit object on screen, wherever the touch.
    Now Y's ranking (REACH) skips enemies with no health left, and when what a touch lands on
    isn't a live enemy, the live enemy nearest the touch (within {PICK_NEAR} pixels across both
    axes, since it may move between Y and the touch), that the game would let him target, is."""
    return f"""
    b pick
y_reach:                    @ +4, from REACH for Y: r1 the distance to r7, an enemy
    ldr r12, [r7, #0xBC]
    cmp r12, #0x1000
    mvnlt r1, #0x80000000   @ no health left: out of reach
    bx lr
pick:                       @ as FUN_02096cd4: r0 the player, r1 touched, r2 and r3 the touch
    push {{r4, r5, r6, r7, r8, lr}}
    sub sp, sp, #24         @ +4 a position (12 bytes), +16 the best so far, +20 its distance
    mov r4, r0
    mov r5, r1
    mov r6, r2
    mov r7, r3
    bl {TOUCH_PICK:#x}
    movs r8, r0
    cmp r5, #0
    beq pick_done
    cmp r8, #0
    beq pick_look
    bl {OBJ_TYPE:#x}
    cmp r0, #4
    bne pick_look
    ldr r0, [r8, #0xBC]
    cmp r0, #0x1000
    bge pick_done           @ a live enemy: as the game chose
pick_look:
    mov r0, #{PICK_NEAR + 1}
    str r0, [sp, #20]
    str r8, [sp, #16]       @ nothing nearer: the game's choice stands
    ldr r0, ={HITLIST:#x}
    mov r1, #0
    bl {LIST_RESET:#x}
pick_next:
    ldr r0, ={HITLIST:#x}
    mov r1, #13
    bl {LIST_NEXT:#x}
    movs r5, r0
    beq pick_best
    bl {OBJ_TYPE:#x}
    cmp r0, #4
    bne pick_next
    ldr r0, [r5, #0xBC]
    cmp r0, #0x1000
    blt pick_next
    ldr r12, [r5]
    ldr r12, [r12, #0x6c]
    mov r0, r5
    add r1, sp, #4
    blx r12
    ldr r12, ={var:#x}
    ldr r1, [r12, #{CAMX}]
    ldr r0, [sp, #4]
    rsb r0, r1, r0, asr #12
    subs r0, r0, r6
    rsblt r0, r0, #0
    ldr r1, [r12, #{CAMY}]
    ldr r2, [sp, #8]
    rsb r2, r1, r2, asr #12
    subs r2, r2, r7
    rsblt r2, r2, #0
    add r0, r0, r2
    ldr r1, [sp, #20]
    cmp r0, r1
    bge pick_next           @ no nearer than the best so far
    str r0, [sp, #12]       @ kept past the calls (+12, the position's unused third word)
    mov r0, r4              @ as the game's own test of what a touch may target
    mov r1, r5
    mov r2, #1
    bl {CAN_TARGET:#x}
    cmp r0, #1
    bne pick_next
    ldr r12, [r5]
    ldr r12, [r12, #0x118]
    mov r0, r5
    mov r1, #1
    blx r12
    cmp r0, #0
    beq pick_next
    ldr r12, [r5]
    ldr r12, [r12, #0xa8]
    mov r0, r5
    blx r12
    cmp r0, #1
    bne pick_next
    str r5, [sp, #16]
    ldr r0, [sp, #12]
    str r0, [sp, #20]
    b pick_next
pick_best:
    ldr r8, [sp, #16]
pick_done:
    mov r0, r8
    add sp, sp, #24
    pop {{r4, r5, r6, r7, r8, pc}}
.ltorg
"""


def scroll_edge_src():
    """An auto-scrolling stage (SetMapAutoScroll; Mokeet's Mansion's sideways rooms) holds the
    player inside the screen (FUN_02081418), but at its very edge: his position is his middle, so
    half of him was off screen. The left limit moves SCROLL_MARGIN in (this load of the edge), and
    the right one too (SCROLL_RIGHT_SITES: 0x100 - 2 * 16 from the moved edge)."""
    assert 0x100 - 2 * SCROLL_MARGIN == 0xE0
    return f"""
    ldr r3, [r0, #0x278]
    add r3, r3, #{SCROLL_MARGIN}
    bx lr
"""


def fs_src():
    """Lief's Final Slash: the red circle and what plays over it, half again as fast. Its circle
    (the screen effect FUN_0201a2a4, shared with other moves) is marked FS_MARK as it is made, and
    for that one the frame count and the pieces' frames left step 3 every 2 frames (48 frames
    become 32). The move's state 5 count (the lions every 10 frames, the end from 46) steps the
    same way, never past a lion's frame; FS_SLIDES speed the lions' slides to match.
    +0 make (for bl FUN_02034b00), +4 the circle's piece (r1 - step), +8 its count (r0 + step),
    +12 state 5's count (r4 = r0 + step)."""
    return f"""
    b fs_make
    b fs_timer
    b fs_count
    b fs_state
fs_make:
    push {{lr}}
    bl 0x02034b00
    cmp r0, #0
    poplt {{pc}}
    ldr r1, ={FX_TABLE:#x}
    ldr r1, [r1, r0, lsl #3]
    cmp r1, #0
    movne r2, #{FS_MARK}
    strhne r2, [r1, #0x6a]
    pop {{pc}}
fs_timer:                   @ sl the circle
    push {{lr}}
    bl fs_step
    sub r1, r1, r12
    pop {{pc}}
fs_count:
    push {{lr}}
    bl fs_step
    add r0, r0, r12
    pop {{pc}}
fs_step:                    @ r12 1, or 2 on the marked circle's frames whose count is 1 past a multiple of 3
    ldrh r12, [sl, #0x6a]
    cmp r12, #{FS_MARK}
    movne r12, #1
    bxne lr
    ldrsh r12, [sl, #2]
fs_mod:
    subs r12, r12, #3
    bge fs_mod
    cmn r12, #2
    moveq r12, #2
    movne r12, #1
    bx lr
fs_state:                   @ r0 the count: r4 the next
    add r4, r0, #1
    mov r12, r0
fs_mod3:
    subs r12, r12, #3
    bge fs_mod3
    cmn r12, #2
    bxne lr
    mov r12, r4             @ an extra step, unless it would pass a lion's frame (a multiple of 10)
fs_mod10:
    subs r12, r12, #10
    bgt fs_mod10
    cmp r12, #0
    addne r4, r4, #1
    bx lr
.ltorg
"""


def spike_attack_src():
    """The player's tap update (FUN_02097f58) skips all tapping and attacking while either
    floor flag is set (spikes and the like), and only checks whether the feet gear (slot 5:
    item 0xD for the first flag, 0xC for the second) protects him. With that gear on, the
    floor counts as plain ground here, so Y and taps attack as anywhere else."""
    return f"""
    b floor_a
    mov r12, #0xC
    b floor
floor_a:
    mov r12, #0xD
floor:
    push {{r4, r5, lr}}
    mov r4, r0
    mov r5, r12
    cmp r5, #0xD
    bne test_b
    bl {ON_FLOOR_A:#x}
    b tested
test_b:
    bl {ON_FLOOR_B:#x}
tested:
    cmp r0, #0
    popeq {{r4, r5, pc}}
    mov r0, r4
    mov r1, #5
    mov r2, r5
    mov r3, #0
    bl {HAS_GEAR:#x}
    cmp r0, #0
    moveq r0, #1            @ unprotected: the flag stands
    movne r0, #0
    pop {{r4, r5, pc}}
"""


def cap_edge_src(var):
    return f"""
    push {{r4, r5}}           @ the D-pad stops at the screen's edge where it can't scroll on
    ldr r4, ={var:#x}
    ldr r5, [r4, #{CTRL}]
    cmp r5, #1
    bne edge_done
    ldr r5, [r4, #{PLAYER}]
    cmp r0, r5
    bne edge_done
    ldr r5, [r0, #0x220]
    add r5, r5, r1
    asr r5, r5, #12
    ldr r12, [r4, #{CAMX}]
    sub r5, r5, r12
    cmp r1, #0
    blt edge_left
    cmp r5, #{EDGE_RIGHT}
    movgt r1, #0
    b edge_y
edge_left:
    cmp r5, #{EDGE_LEFT}
    movlt r1, #0
edge_y:
    ldr r5, [r0, #0x224]
    add r5, r5, r2
    asr r5, r5, #12
    ldr r12, [r4, #{CAMY}]
    sub r5, r5, r12
    cmp r2, #0
    blt edge_top
    cmp r5, #{EDGE_BOTTOM}
    movgt r2, #0
    b edge_done
edge_top:
    cmp r5, #{EDGE_TOP}
    movlt r2, #0
edge_done:
    pop {{r4, r5}}
    bx r3

.ltorg
"""


def alert_src():
    """Low health: the game loops one beeping sound until health recovers. Stop it after three
    beeps and start it again every ALERT_EVERY frames; the game still ends it as before."""
    return f"""
    push {{lr}}             @ r4 the player: +0xFC4 the sound, +0xFC8 which one
    ldr r12, ={OPT_DATA:#x}
    ldrb r1, [r12, #{OPT_ALERT}]
    ldr r12, ={ALERT_DATA:#x}
    ldr r0, [r4, #0xFC4]
    cmp r1, #1              @ Off: each sound the game starts is stopped at once; the handle stays
    bne alert_beeps
    cmp r0, #0
    beq alert_tick
    ldr r1, [r12, #4]
    cmp r0, r1
    beq alert_tick
    str r0, [r12, #4]
    mov r1, r0
    mov r0, r4
    bl {VOICE_STOP:#x}
    b alert_tick
alert_beeps:
    cmp r0, #0
    moveq r1, #0
    streq r1, [r12]
    streq r1, [r12, #4]
    beq alert_tick
    ldr r1, [r12, #4]
    cmp r0, r1              @ the game started a sound: count from here
    movne r1, #0
    strne r1, [r12]
    strne r0, [r12, #4]
    ldr r1, [r12]
    add r1, r1, #1
    str r1, [r12]
    ldr r2, [r4, #0xFC8]
    cmp r2, #1
    moveq r3, #{ALERT_STOP[0]}
    movne r3, #{ALERT_STOP[1]}
    cmp r1, r3
    bne alert_wait
    mov r1, r0              @ three beeps done: quiet, but the handle stays so the game waits
    mov r0, r4
    bl {VOICE_STOP:#x}
    ldr r12, ={ALERT_DATA:#x}
    ldr r1, [r12]
alert_wait:
    cmp r1, #{ALERT_EVERY}
    blt alert_tick
    ldr r2, [r4, #0xFC8]
    cmp r2, #3
    bhi alert_tick
    adr r3, alert_sounds
    ldrb r2, [r3, r2]
    mov r0, r4
    mov r1, #0
    bl {PLAY_VOICE:#x}
    str r0, [r4, #0xFC4]
    ldr r12, ={ALERT_DATA:#x}
    str r0, [r12, #4]
    mov r1, #0
    str r1, [r12]
alert_tick:                 @ the four instructions this replaced
    ldr r0, [r4, #0xFCC]
    cmp r0, #0
    subgt r0, r0, #1
    strgt r0, [r4, #0xFCC]
    pop {{pc}}

.ltorg
alert_sounds:
.byte 0, 0x77, 0x76, 0x78
"""


def hud_guard_src(var):
    """The field's bag icon and item square answer the stylus only: an attack or talk tap on
    someone drawn behind them must not open the bag or use the item."""
    return f"""
    b hud_tap
    b bag_draw
    b bag_tap
    ldr r12, ={OPT_DATA:#x}   @ the bag icon's corner in the first check: nothing while hidden
    ldrb r12, [r12, #{OPT_BAG}]
    cmp r12, #1
    cmpne r1, #0
    bx lr

hud_tap:
    ldr r1, [sp, #0x14]     @ the touch's just-pressed flag, as the code here reads it
    ldr r12, ={var:#x}
    ldr r12, [r12, #{ACTIVE}]
    cmp r12, #0
    movne r1, #0
    bx lr

bag_tap:                    @ the icon's own tap check: the stylus only, and only while it shows
    ldr r12, ={var:#x}
    ldr r12, [r12, #{ACTIVE}]
    cmp r12, #0
    movne r0, #0
    bxne lr
    ldr r12, ={OPT_DATA:#x}
    ldrb r12, [r12, #{OPT_BAG}]
    cmp r12, #0
    movne r0, #0
    bxne lr
    b {BAG_SHOWN:#x}

bag_draw:                   @ the Bag Icon option: hidden, the icon is simply not drawn
    ldr r12, ={OPT_DATA:#x}
    ldrb r12, [r12, #{OPT_BAG}]
    cmp r12, #0
    bxne lr
    b {BAG_DRAW:#x}

.ltorg
"""


def swing_src():
    return f"""
swing:                      @ r4 the player: FUN_02096fc4's start of an attack, minus the target
    ldr r0, [r9, #{MODE}]
    cmp r0, #4              @ A found nobody: nothing to do
    beq {OFF:#x}
    ldr r0, ={HITLIST:#x}   @ only with an enemy on screen
    mov r1, #0
    bl {LIST_RESET:#x}
swing_look:
    ldr r0, ={HITLIST:#x}
    mov r1, #13
    bl {LIST_NEXT:#x}
    movs r7, r0
    beq {OFF:#x}
    bl {OBJ_TYPE:#x}
    cmp r0, #4
    bne swing_look
    ldr r12, [r7]
    ldr r12, [r12, #0x6c]
    mov r0, r7
    add r1, sp, #4
    blx r12
    ldr r0, [sp, #4]
    ldr r1, [r9, #{CAMX}]
    rsb r0, r1, r0, asr #12
    cmp r0, #0
    blt swing_look
    cmp r0, #256
    bge swing_look
    ldr r0, [sp, #8]
    ldr r1, [r9, #{CAMY}]
    rsb r0, r1, r0, asr #12
    cmp r0, #0
    blt swing_look
    cmp r0, #192
    bge swing_look
    mov r0, r4
    bl {ATTACK_CAN:#x}
    cmp r0, #0
    beq {OFF:#x}
    mov r0, r4
    ldr r1, [r0]
    ldr r1, [r1, #0xa0]
    blx r1
    cmp r0, #0
    bne {OFF:#x}
    ldr r0, ={EVENTS:#x}
    bl {EVENT_ON:#x}
    cmp r0, #0
    bne {OFF:#x}
    mov r0, r4
    mov r1, #0              @ no target: the swing keeps the way he faces
    bl {SET_TARGET:#x}
    add r1, r4, #{COMBO_AT & ~0xFFF:#x}
    ldr r1, [r1, #{COMBO_AT & 0xFFF:#x}]
    cmp r1, #6
    movhi r1, #0
    adr r2, swing_states
    ldrb r1, [r2, r1]
    mov r0, r4
    ldr r2, [r0]
    ldr r2, [r2, #0x1dc]
    blx r2
    mov r0, r4
    mov r1, #0x2000
    bl {ATTACK_END:#x}
    b {OFF:#x}

.ltorg
swing_states:               @ the state for each hit of the combo, as FUN_02096fc4 picks it
.byte 9, 10, 11, 12, 13, 14, 0x1d, 0
"""


def reach_src():
    return f"""
reach:                      @ r1 + r3 is the distance to r7 (r0, r2); A ranks people in reach by where Lief faces
    add r1, r1, r3
    ldr r12, [r9, #{MODE}]
    cmp r12, #4
    bne {PICK_CODE + 4:#x}  @ Y: plain distance, for live enemies
    push {{r0, r2, r3, r4, lr}}
    mov r0, r4
    mov r1, r7
    bl {MOB_DISTANCE:#x}    @ what the touch scripts' GetMobDistance gives
    asr r1, r0, #12
    ldr r12, [r7, #0x410]
    ldr r2, ={TALK_LIMITS:#x}
reach_find:                 @ their own limit, or {TALK_REACH}
    ldrh r3, [r2], #2
    cmp r3, #0
    moveq r3, #{TALK_REACH // 4 << 12}
    beq reach_found
    lsl r0, r3, #20
    cmp r12, r0, lsr #20
    bne reach_find
reach_found:
    lsr r3, r3, #12
    cmp r1, r3, lsl #2
    movge r1, #0x1000       @ their script wouldn't answer
    bge reach_done
    ldr r0, [sp]
    ldr r2, [sp, #4]
    sub r0, r0, r5          @ their offset from Lief
    sub r2, r2, r6
    ldr r3, [r9, #{FX}]     @ the way he last walked
    ldr r12, [r9, #{FY}]
    mul r4, r0, r3
    mla r4, r2, r12, r4
    cmp r4, #0
    addlt r1, r1, #{TALK_BEHIND}    @ behind him
    mul r4, r0, r12
    mul r0, r2, r3
    subs r4, r4, r0
    rsblt r4, r4, #0
    add r1, r1, r4          @ how far off to the side of where he faces
reach_done:
    b {REACH_MORE:#x}
.ltorg
"""


def reach_more_src():
    """reach's end: a low-priority character (TALK_LOW, by the record id at +0x410) ranks behind
    anyone else A could talk to, and still ahead of anyone out of reach (0x1000)."""
    rows = "\n".join(f"    ldr r2, ={rid:#x}\n    cmp r0, r2\n    addeq r1, r1, #{pen}" for rid, pen in TALK_LOW.items())
    return f"""
    ldr r0, [r7, #0x410]
{rows}
    pop {{r0, r2, r3, r4, pc}}
.ltorg
"""


def place_src(tap):
    return f"""
    bl {KEY_COLS:#x}
    ldrb r0, [r5, #{DX}]
    ldrb r1, [r5, #{X0}]
    mla r0, r7, r0, r1
    cmp r7, #4
    ldrbge r1, [r5, #{GAP}]
    addge r0, r0, r1
    ldrb r1, [r5, #{DY}]
    ldrb r12, [r5, #{Y0}]
    mla r1, r8, r1, r12
    ldrb r12, [r5, #{COLS}]
    cmp r12, #7
    cmpeq r3, #0
    beq check_tap
    cmp r12, #7
    bne check_tap
    add r12, r4, #0x1A00
    ldr r12, [r12, #{BOOK_TAB - 0x1A00:#x}]
    add r3, r12, r3
    cmp r3, #4
    bhs check_tap
    rsb r3, r3, r3, lsl #3
    lsl r3, r3, #3
    add r3, r3, #0x24
    orr r3, r3, #0x1000
    b store
check_tap:
    ldrb r12, [r5, #{COLS}]
    cmp r12, #7             @ the book's back button is at top right
    bne not_book
    tst r6, #2
    movne r3, #0xF4
    orrne r3, r3, #0x1000
    bne store
not_book:
    tst r6, #1
    bne use_cell
    ldrb r12, [r5, #{AUTO}]
    ands r12, r12, r2
    beq drawit
use_cell:
    orr r3, r0, r1, lsl #8
store:
    ldr r12, ={tap:#x}
    str r3, [r12]
drawit:
    ldrb r2, [r5, #{AUTO}]  @ these pages highlight their own selection
    cmp r2, #0
    ldrbeq r2, [r5, #{RISE}]
    subeq r1, r1, r2
    bleq {DRAW:#x}
    pop {{r0, r4, r5, r6, r7, r8, lr}}
    push {{r4, lr}}
    b {DISPATCH + 4:#x}

.ltorg
"""


def actions_src():
    return f"""
    b open_bag
    b use_item
    b charge
    b cap
    b from_save

cap:                        @ DO_MOVE applying its step: no axis beyond walk or run speed
    ldr r12, ={PAD:#x}
    ldrh r12, [r12]
    tst r12, #0xF0
    bxeq r3
    tst r12, #2
    mov r12, #{WALK_SPEED:#x}
    lslne r12, r12, #1
    cmp r1, r12
    movgt r1, r12
    cmn r1, r12
    rsblt r1, r12, #0
    cmp r2, r12
    movgt r2, r12
    cmn r2, r12
    rsblt r2, r12, #0
    b {CAP_EDGE:#x}

ready:                      @ Z clear when the game's own bag and item checks pass
    push {{lr}}
    mov r0, #0
    bl {FLAG:#x}
    cmp r0, #0
    popeq {{pc}}
    mov r0, r4
    bl {IN_FIELD:#x}
    cmp r0, #0
    popeq {{pc}}
    ldr r12, [r4]
    ldr r12, [r12, #0xa0]
    mov r0, r4
    blx r12
    cmp r0, #0
    bne not_ready
    ldr r0, ={EVENTS:#x}
    bl {EVENT_ON:#x}
    cmp r0, #0
not_ready:
    moveq r0, #1
    movne r0, #0
    cmp r0, #0
    pop {{pc}}

open_bag:
    bl ready
    beq {OFF:#x}
    ldr r0, ={MENU:#x}
    bl {OPEN_BAG:#x}
    mov r0, r4
    bl {HIDE_ICON:#x}
    mov r0, r4
    mov r1, #0
    mov r2, #0x71
    bl {PLAY_VOICE:#x}
    b {OFF:#x}

use_item:
    bl ready
    beq {OFF:#x}
    mov r0, r4
    bl {ITEM_HELD:#x}
    cmn r0, #1
    beq {OFF:#x}
    ldr r12, [r4]
    ldr r12, [r12, #0x1dc]
    mov r0, r4
    mov r1, #0x33
    blx r12
    b {OFF:#x}

charge:                     @ only where the game allows dash attacks
    mov r0, #10
    bl {FLAG:#x}
    cmp r0, #0
    beq {OFF:#x}
    ldr r0, [r4, #0xf14]
    and r0, r0, #3
    cmp r0, #3
    bne {OFF:#x}
    mov r0, #2
    str r0, [r9, #{MODE}]
    b {ON:#x}

from_save:                  @ leaving Save, the arrow appears on the hero at once
    cmp r10, #3
    bxne lr
    ldr r2, [r9, #{CAMP_SEL}]
    adr r1, hero_tops
    add r1, r1, r2, lsl #1
    ldrb r0, [r1]
    lsl r0, r0, #12
    str r0, [r11, #0x220]
    ldrb r0, [r1, #1]
    lsl r0, r0, #12
    str r0, [r11, #0x224]
    bx lr

.ltorg
hero_tops:                  @ where the scene puts the arrow for each hero
.byte 195, 126, 77, 127, 181, 31, 0, 0
"""


def input_src(attack, camp):
    return f"""
    b update
    b on
    b off

update:
    push {{lr}}
    ldr r8, ={PAD:#x}
    ldrh r8, [r8]
    ldr r7, [r9, #{PREV}]
    str r8, [r9, #{PREV}]
    bic r7, r8, r7
    bl {OPT_CODE + 40:#x}   @ an options info box asked for a tap to turn its page: it goes on from there
    ldr r0, [r9, #{PROMPT_ON}]  @ a Yes/No prompt reads the buttons itself
    mov r1, #0
    str r1, [r9, #{PROMPT_ON}]
    cmp r0, #0
    bne off
    ldr r0, [r9, #{CAMP}]
    cmp r0, #0
    bne {CAMP_X + 20:#x}     @ camp: Y first, then the camp's own input
    ldr r0, [r9, #{TITLE}]
    cmp r0, #0
    bne {TITLE_CODE:#x}
    ldr r0, [r9, #{ANY_KEY}]
    cmp r0, #0
    beq no_any
    movs r0, r7, lsl #20    @ "Press Any Button"
    beq off
    mov r0, #0
    str r0, [r9, #{ANY_KEY}]
    mov r5, #128
    mov r6, #96
    b on
no_any:
    bl {MIX_CODE:#x}
    ldr r4, [r9, #{PLAYER}]
    ldr r0, [r9, #{CTRL}]
    cmp r0, #2
    beq off
    cmp r0, #1
    bne scene
    ldr r0, ={STAGE:#x}
    ldr r1, [r0, #0x278]
    ldr r2, [r0, #0x2a0]
    add r1, r1, r2
    str r1, [r9, #{CAMX}]
    ldr r5, [r4, #0x220]
    sub r5, r1, r5, asr #12
    rsb r5, r5, #0
    ldr r1, [r0, #0x27c]
    ldr r2, [r0, #0x2a4]
    add r1, r1, r2
    str r1, [r9, #{CAMY}]
    ldr r6, [r4, #0x224]
    sub r6, r1, r6, asr #12
    rsb r6, r6, #0
    ldr r0, [r9, #{MODE}]
    cmp r0, #3
    beq flick
    mov r1, #0
    mov r2, #0
    tst r8, #0x20
    subne r1, r1, #1
    tst r8, #0x10
    addne r1, r1, #1
    tst r8, #0x40
    subne r2, r2, #1
    tst r8, #0x80
    addne r2, r2, #1
    orrs r12, r1, r2
    strne r1, [r9, #{FX}]
    strne r2, [r9, #{FY}]
    tst r7, #4
    bne swap
    tst r8, #0x400
    bne {CHARGE:#x}
    cmp r0, #2
    beq start_flick
    tst r7, #0x800
    bne {attack:#x}
    tst r7, #0x200
    bne {USE:#x}
    tst r7, #1
    bne {attack + 8:#x}
    tst r7, #8
    bne {OPEN:#x}
    b off
on:
    cmp r5, #1
    movlt r5, #1
    cmp r5, #254
    movgt r5, #254
    cmp r6, #1
    movlt r6, #1
    cmp r6, #190
    movgt r6, #190
    str r5, [r9, #{VX}]
    str r6, [r9, #{VY}]
    mov r0, #1
    pop {{pc}}
off:
    mov r0, #0
    str r0, [r9, #{MODE}]
    pop {{pc}}

scene:
    ldr r0, [r9, #{TAP}]
    cmp r0, #0
    beq keys
    mov r1, #0
    str r1, [r9, #{TAP}]
    and r5, r0, #0xFF
    lsr r6, r0, #8
    b on
keys:
    ldr r2, [r9, #{CTRL}]
    cmp r2, #4
    bne not_town
    tst r7, #8
    bne {OPEN:#x}
    b off
not_town:
    tst r7, #8
    beq no_start
    ldr r0, ={MENU:#x}
    ldr r0, [r0]
    cmp r0, #0
    beq off
    ldr r0, [r0, #4]
    cmp r0, #13
    beq off
    b corner
no_start:
    tst r7, #2
    beq no_back
corner:
    b {OPT_CODE + 36:#x}     @ the bag's back corner, unless the options page is open
no_back:
    tst r7, #1
    beq off
    mov r5, #4              @ away from every menu's touch zones
    mov r6, #100
    b on

swap:                       @ Select: the next item comes to the big square
    ldr r0, [r4, #0xD60]
    cmp r0, #3              @ the item bar is at rest
    bne off
    ldr r1, [r4, #0xADC]
    cmp r1, #2
    blt off
    bl {NEXT_ITEM:#x}
    b off

start_flick:
    mov r0, #3
    str r0, [r9, #{MODE}]
    mov r0, #6
    str r0, [r9, #{CNT}]
    b on

flick:
    ldr r0, [r9, #{CNT}]
    subs r0, r0, #1
    str r0, [r9, #{CNT}]
    beq off
    ldr r5, [r9, #{VX}]
    ldr r6, [r9, #{VY}]
    ldr r1, [r9, #{FX}]
    ldr r2, [r9, #{FY}]
    add r5, r5, r1, lsl #4
    add r6, r6, r2, lsl #4
    b on

.ltorg
"""


def pose_src(var):
    return f"""
    push {{r4, r5, lr}}
    ldr r4, ={var:#x}
    ldr r0, [r4, #{SE_REQ}]
    cmp r0, #0
    beq no_sound
    mov r0, #0
    str r0, [r4, #{SE_REQ}]
    ldr r0, ={SOUND:#x}
    mov r1, #0
    mov r2, #103            @ the hero cursor sound
    bl {PLAY_SE:#x}
no_sound:
    ldr r0, [r4, #{GLIDE}]
    cmp r0, #0
    beq no_glide
    ldr r3, [r4, #{POINTER}]
    subs r0, r0, #1
    str r0, [r4, #{GLIDE}]
    ldrne r1, [r3, #0x220]
    ldrne r2, [r4, #{GLIDE_X}]
    addne r1, r1, r2
    ldreq r1, [r4, #{AX}]
    str r1, [r3, #0x220]
    ldrne r1, [r3, #0x224]
    ldrne r2, [r4, #{GLIDE_Y}]
    addne r1, r1, r2
    ldreq r1, [r4, #{AY}]
    str r1, [r3, #0x224]
no_glide:
    ldr r5, [r4, #{POSE_REQ}]
    cmp r5, #0
    popeq {{r4, r5, pc}}
    mov r0, #0
    str r0, [r4, #{POSE_REQ}]
    ldr r0, ={WORLD:#x}
    ldr r1, [r4, #{SEL_MOB}]
    bl {FIND_MOB:#x}
    movs r1, r0
    popeq {{r4, r5, pc}}
    ldr r3, [r4, #{HERO}]
    cmp r5, #2              @ back on the hero: selected pose
    moveq r2, #1
    movne r2, #0
    cmpne r3, #1            @ otherwise idle, which is motion 2 for Barda
    moveq r2, #2
    cmp r5, #2
    moveq r2, #1
    mov r5, r1
    ldr r0, ={EVENTS:#x}
    bl {SET_MOTION:#x}
    mov r0, r5
    bl {MOTION_LOOP:#x}
    pop {{r4, r5, pc}}

.ltorg
"""


def anim_src(var):
    return f"""
    b direct
    b loop

direct:                     @ the crow or caterpillar shouldn't stop the camp loop
    ldr r12, ={var:#x}
    ldr r1, [r12, #{ARM}]
    cmp r1, #0
    beq {SB_DIRECT:#x}
    mov r1, #0
    str r1, [r12, #{ARM}]
    push {{r4, r5, r6, lr}}
    mov r4, r0
    bl {SCRIPT_ARG:#x}
    mov r5, r0
    mov r1, r5
    ldr r0, ={WORLD:#x}
    bl {FIND_MOB:#x}
    mov r6, r0
    mov r0, r4
    mov r1, #1
    bl {SCRIPT_ARG:#x}
    mov r2, r0
    mov r1, r6
    ldr r0, ={EVENTS:#x}
    bl {SET_MOTION:#x}
    mov r0, r6
    bl {START_MOTION:#x}
    ldr r12, ={var:#x}
    str r5, [r12, #{HOLD_ID}]
    str r6, [r12, #{HOLD_OBJ}]
    mvn r0, #0
    str r0, [r12, #{HOLD_MOTION}]
    mov r0, #1
    pop {{r4, r5, r6, pc}}

loop:                       @ its return to idle waits for the animation
    push {{r4, r5, r6, lr}}
    mov r4, r0
    mov r1, #0
    bl {SCRIPT_ARG:#x}
    mov r5, r0
    mov r0, r4
    mov r1, #1
    bl {SCRIPT_ARG:#x}
    mov r6, r0
    ldr r12, ={var:#x}
    ldr r0, [r12, #{CAMP}]
    cmp r0, #0
    beq not_camp
    cmp r6, #1              @ motion 1 is the selected hero's pose
    streq r5, [r12, #{SEL_MOB}]
    ldr r0, [r12, #{HOLD_OBJ}]
    cmp r0, #0
    beq not_camp
    ldr r0, [r12, #{HOLD_ID}]
    cmp r0, r5
    bne not_camp
    str r6, [r12, #{HOLD_MOTION}]
    mov r0, #1
    pop {{r4, r5, r6, pc}}
not_camp:
    mov r0, r4
    pop {{r4, r5, r6, lr}}
    b {SB_LOOP:#x}

.ltorg
"""


# Mob_Touch's GetMobDistance(player, mob) / 4096 < 32: NPCs standing in a group, whom Lief can't
# get that close to, answer from further away. The final chapter's Jasmine (2306, event 1996), with
# the children, Filli and Kree around her (chapter 9 stage 2 area 1).
TALK_RANGE = {2306: 56}
# That area's spawn table (AreaSpawn file 2823): the four around Jasmine had the do-nothing script
# 2232, so touching them did nothing; now theirs is hers, and any of the group starts the scene.
GROUP_SPAWNS, GROUP_RECORDS = 2823, (0x10C, 0x128, 0x144, 0x160)   # 28-byte records, script at +24


def patch_group(table):
    b = bytearray(table)
    for at in GROUP_RECORDS:
        assert struct.unpack_from("<H", b, at + 24)[0] == 2232, hex(at)
        struct.pack_into("<H", b, at + 24, 2306)
    return bytes(b)


def patch_talk_range(script, reach):
    b = bytearray(script)
    funcs, _ = scr.recs(b)
    touch = scr.rec(b, funcs[3])
    assert touch["name"] == "Mob_Touch"
    at = touch["code"] + 8 * 2
    assert struct.unpack_from("<6H", b, at) == (0x4001, 4096, 0x6, 0x4000, 32, 0x9), struct.unpack_from("<6H", b, at)
    struct.pack_into("<H", b, at + 8, reach)
    return bytes(b)
