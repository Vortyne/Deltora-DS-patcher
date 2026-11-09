"""The title's file screen: play time, completion and the Tower floor; the save's play time.

Part of the controls namespace (see __init__.py): names from every part are shared."""

PT_CODE, PT_ROOM = 0x02216E20, 0x388   # play time: kept with the save, shown on the title's file screen; LOC_CODE follows
PT_SAVE_AT = 0x1FB8             # backup bytes after the kill counts (they end at 0x1FB4): frames played, 0xFFFFFFFF never saved
VBLANK_COUNT = 0x027FFC3C       # NitroSDK's count of vertical blanks (OS_GetVBlankCount): real time, whatever the game's frame rate
PT_PER_SECOND = 71790862        # 2^32 / 59.8261 (the DS's frame rate): frames * this >> 32 = seconds
PT_MAX = 9999 * 3600 + 59 * 60 + 59    # 9999:59:59
INFO_SHOW_SITES = (0x0206B53C, 0x0206B558, 0x0206B574)   # the file screen's info box for a file: messages 0x3D, 0x3E, chapter + 0xF
TOWER_NAME_CODE, TOWER_NAME_ROOM = 0x02217B20, 0x40   # the title's file box: a Tower rest room's floor (to the 29th kilobyte's end)
PT_X, PT_Y = 86, 98             # the time's centre x and top y: the black box's bottom right, under the chapter's lines
# 0x02216760 (0x180 bytes, the 25th kilobyte) is free: the memory log was there. DEFER_TICK follows.
LOAD_RESULT_SITE, LOAD_RESULT = 0x02048570, 0x0206AF98    # BuckupDataLoad: the save file screen's result
BACKUP_UNLOCK_OBJ = 0x020356AC
BACKUP_READ, BACKUP_WRITE = 0x02035598, 0x020358D0
LOCK_ID, LOCK_RELEASE = 0x020061B8, 0x02006210
CARD_LOCK, CARD_UNLOCK = 0x0200F7F4, 0x0200F804
CARD_LOCKS = 0x020C7EA0      # the card's lock: +8 its owner's lock id, -3 (0xFFFFFFFD) when free


def pt_src():
    """Play time. The game kept none. A file's time is the frames counted by NitroSDK's vertical
    blank count (real time, whatever the game's frame rate), kept as 4 bytes at PT_SAVE_AT:
    +0 load: as the file screen's result is taken (with the kill counts, CARDS_CODE + 4), a new
       game starts from 0 and a loaded file from its saved time (0xFFFFFFFF, saved before this:
       from 0); from then the time is that plus the blanks since. Nothing counts before a game.
    +4 save: when a save goes through (then the kill counts), the time is written.
    +8 show: the title's file screen draws a file's box (INFO_FN, its 3 calls for a file):
       h:mm:ss at its bottom right, from the saved time (none if never saved with one), at most
       9999:59:59. +12 close: closing a message window (MSG_CLOSE) takes the time down with its box."""
    d0, colon = entext.encode("0")[0], entext.encode(":")[0]
    assert entext.encode("9")[0] == d0 + 9
    return f"""
    b pt_load
    b pt_save
    b file_show             @ the file box's lines
    b pt_close
pt_load:                    @ for bl LOAD_RESULT: r0 the result, -1 a new game, 0 and up a file
    push {{r4, r5, lr}}
    bl {CARDS_CODE + 4:#x}  @ the kill counts' own, which takes the result
    mov r4, r0
    ldr r5, =pt_data
    cmn r4, #1
    moveq r0, #0
    beq pt_begin
    cmp r4, #0
    blt pt_loaded
    ldr r0, ={BACKUP_READ:#x}
    add r1, r5, #24
    bl pt_io
    cmp r0, #0
    beq pt_loaded           @ unread: not counted, never written
    ldr r0, [r5, #24]
    cmn r0, #1
    moveq r0, #0
pt_begin:
    str r0, [r5]            @ the time at the start
    ldr r1, ={VBLANK_COUNT:#x}
    ldr r1, [r1]
    str r1, [r5, #4]        @ and the blanks then
    mov r1, #1
    str r1, [r5, #8]
pt_loaded:
    mov r0, r4
    pop {{r4, r5, pc}}

pt_save:                    @ at the save point's message: lr the caller's; then the kill counts
    push {{r4, lr}}
    ldr r4, =pt_data
    ldr r0, [r4, #8]
    cmp r0, #0
    beq pt_saved
    ldr r0, ={VBLANK_COUNT:#x}
    ldr r0, [r0]
    ldr r1, [r4, #4]
    sub r0, r0, r1
    ldr r1, [r4]
    adds r0, r0, r1
    mvncs r0, #1            @ past 2^32: held just under the unset value
    str r0, [r4, #24]
    ldr r0, ={BACKUP_WRITE:#x}
    add r1, r4, #24
    bl pt_io
pt_saved:
    pop {{r4, lr}}
    b {CARDS_CODE + 8:#x}

pt_io:                      @ r0 BACKUP_READ or BACKUP_WRITE, r1 4 bytes: 1 if done
    push {{r4, r5, r6, r7, lr}}
    mov r5, r0
    mov r7, r1
    mov r6, #0
    bl {LOCK_ID:#x}
    mov r4, r0
    cmn r0, #3
    beq pt_io_end
    bl {CARD_LOCK:#x}
    ldr r0, ={PT_SAVE_AT:#x}
    mov r1, r7
    mov r2, #4
    blx r5
    mov r0, r4
    bl {CARD_UNLOCK:#x}
    mov r0, r4
    bl {LOCK_RELEASE:#x}
    mov r6, #1
pt_io_end:
    mov r0, r6
    pop {{r4, r5, r6, r7, pc}}

pt_close:                   @ for MSG_CLOSE's push {{r4, lr}}: r0 the window
    ldr r12, =pt_data
    ldr r12, [r12, #12]
    cmp r12, #0
    beq pt_close_on
    cmp r12, r0
    bne pt_close_on
    push {{r0, lr}}
    bl pt_free
    pop {{r0, lr}}
pt_close_on:
    push {{r4, lr}}
    b {MSG_CLOSE + 4:#x}

pt_free:                    @ the file box's lines
    ldr r0, =pt_data
    b {COMP_CODE + 12:#x}   @ file_free
{file_src()}
pt_data:                    @ +0 time at the start, +4 blanks then, +8 counting, +12 the box shown,
.word 0, 0, 0, 0            @ +16 the time's slot + 1, +20 its buffer, +24 4 bytes for the backup,
.word 0, 0, 0               @ +28 its 12 tokens
.short 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
"""


FILE_RIGHT = 116                # the file box's lines end here (the dark box is x 4-120)
FILE_COMP_Y, FILE_TIME_Y = 80, 96   # its last two lines: "Completion: n%", then "Play time: h:mm"


def file_src():
    """The title's file box, for bl INFO_FN (r0-r3 its arguments, r4 the screen, the file's save at
    FILE_SAVE): after the box's own text, "Completion: n%" (comp_save) and "Play time: h:mm" (the
    backup's frames, if saved with one; at most 9999:59), each right-aligned to FILE_RIGHT by the
    line measure's right mode, as text strips like the menu arrow's. file_free takes both down if
    their slots still hold our buffers; pt_data +12 keeps the box, +16/+20 the first line's slot + 1
    and buffer, file_data the second's."""
    d0, colon, pct = entext.encode("0")[0], entext.encode(":")[0], entext.encode("%")[0]
    toks = lambda t: ", ".join(f"{x:#x}" for x in entext.encode(t))
    return f"""
file_show:
    push {{r4, r5, r6, r7, r8, lr}}
    mov r8, r4
    bl {INFO_FN:#x}
    mov r6, r0
    ldr r0, =pt_data
    bl {COMP_CODE + 12:#x}  @ file_free
    ldr r5, =pt_data
    str r6, [r5, #12]
    cmp r6, #0
    beq file_done
    ldr r0, ={BACKUP_READ:#x}   @ the time first: reading the backup after making a line hung the game
    add r1, r5, #24
    bl pt_io
    mov r6, r0              @ read
    add r0, r8, #{FILE_SAVE:#x}
    bl {COMP_CODE + 4:#x}   @ comp_save
    mov r1, r0
    ldr r7, =file_comp_n
    mov r4, #0
    mov r2, #100
    bl file_digit
    mov r2, #10
    bl file_digit
    add r1, r1, #{d0:#x}
    strh r1, [r7], #2
    mov r0, #{pct:#x}
    strh r0, [r7], #2
    ldr r0, =0xFFFD
    strh r0, [r7]
    ldr r0, =file_comp
    mov r1, #{FILE_COMP_Y}
    add r2, r5, #16
    bl {COMP_CODE + 8:#x}   @ file_strip
    cmp r6, #0
    beq file_done
    ldr r0, [r5, #24]
    cmn r0, #1
    beq file_done           @ never saved with a time
    ldr r1, ={PT_PER_SECOND:#x}
    umull r2, r0, r1, r0    @ seconds
    ldr r1, ={PT_MAX:#x}
    cmp r0, r1
    movhi r0, r1
    ldr r2, =3600
    mov r1, #0
file_h:
    cmp r0, r2
    subhs r0, r0, r2
    addhs r1, r1, #1
    bhs file_h
    mov r3, #0
file_m:
    cmp r0, #60
    subhs r0, r0, #60
    addhs r3, r3, #1
    bhs file_m
    mov r6, r3              @ the minutes (the window is in pt_data now)
    ldr r7, =file_time_n
    mov r4, #0              @ no leading zeros on the hours
    ldr r2, =1000
    bl file_digit
    mov r2, #100
    bl file_digit
    mov r2, #10
    bl file_digit
    add r1, r1, #{d0:#x}
    strh r1, [r7], #2
    mov r0, #{colon:#x}
    strh r0, [r7], #2
    mov r1, r6
    mov r2, #10
    mov r4, #1              @ the minutes: both digits
    bl file_digit
    add r1, r1, #{d0:#x}
    strh r1, [r7], #2
    ldr r0, =0xFFFD
    strh r0, [r7]
    ldr r0, =file_time
    mov r1, #{FILE_TIME_Y}
    add r2, r5, #28         @ the old token buffer: the second line's slot + 1 and buffer
    bl {COMP_CODE + 8:#x}   @ file_strip
file_done:
    ldr r0, [r5, #12]
    pop {{r4, r5, r6, r7, r8, pc}}

file_digit:                 @ r1 the rest, r2 a place: its digit into r7, once a digit has shown (r4)
    mov r3, #0
file_d:
    cmp r1, r2
    subhs r1, r1, r2
    addhs r3, r3, #1
    bhs file_d
    orrs r4, r4, r3
    bxeq lr
    add r3, r3, #{d0:#x}
    strh r3, [r7], #2
    bx lr

.ltorg
file_comp:
.short {toks("Completion: ")}
file_comp_n:
.short 0, 0, 0, 0, 0, 0
file_time:
.short {toks("Play time: ")}
file_time_n:
.short 0, 0, 0, 0, 0, 0, 0, 0
.align 2
"""


FILE_SAVE = 0x60                # the title's file screen (INFO_FN's r4): the file's save image, as the backup holds it
TOWER_NAMES = 64                # bank 2192: "Tower of Illusion 10F" ... "90F", then "99F" (camp + 15 would be 58)


def tower_name_src():
    """The title's file box, for bl INFO_FN with r0 = camp + 0xF (r4 the screen): a file saved at a
    rest room (camp TOWER_CAMP) shows its floor's name, TOWER_NAMES + floor / 10 - 1, 99F the last."""
    return f"""
    cmp r0, #{TOWER_CAMP + 0xF}
    bne {PT_CODE + 8:#x}
    ldr r12, ={TOWER_FLOOR_AT:#x}
    ldr r12, [r4, r12]
    mov r0, #{TOWER_NAMES - 1}
    cmp r12, #99
    movge r12, #100         @ 99F: the tenth
tower_div:
    subs r12, r12, #10
    addge r0, r0, #1
    bgt tower_div
    cmp r0, #{TOWER_NAMES}
    movlt r0, #{TOWER_NAMES}
    b {PT_CODE + 8:#x}
.ltorg
"""
