"""Build the English ROM: every patch applied to the original game's files and code."""
import paths
import os
import sys
import struct
import build_rom
import card_patch
import controls
import entext
import itemdb
import mapfix
import drops
import title_patch
import translate
from lf2 import read_lf2

SRC = paths.ROM
OUT = paths.OUT
OVERLAY2_RAM = 0x021F0760
MIX_BACK = controls.MIX_BACK
MIX_BACK_SRC = f"""
    push {{r4, lr}}
    mov r4, r0
    bl {controls.MIX_SOUND:#x}       @ the jingle plays on, the music fades back in
    mov r2, #0              @ the bowl was used up
    str r2, [r4, #0x3C]
    mvn r2, #0
    str r2, [r4, #0x40]
    str r2, [r4, #0x44]
    str r2, [r4, #0x48]
    bl 0x021F5664           @ no prompts
    mov r0, r4
    add r1, r4, #300
    bl 0x021F5550           @ the result's item
    mov r0, r4
    bl 0x021F2A98           @ and its text
    mov r1, #0x04000000     @ the bowl's blending, which would thin out the item grid
    add r1, r1, #0x50
    mov r2, #0
    strh r2, [r1]
    add r0, r4, #900        @ Jasmine's normal pose
    mov r1, #0
    bl 0x02034508
    mov r0, r4
    mov r1, #3
    pop {{r4, lr}}
    b 0x021F2B40
"""
MIX_WAIT = MIX_BACK + 104
MIX_WAIT_SRC = f"""
    ldr r12, ={controls.PAD:#x}
    ldrh r12, [r12, #2]
    tst r12, #1             @ for the timer's own compare: past the limit once A is pressed
    moveq r12, #0
    movne r12, #0x100
    cmp r12, #0x3C
    bx lr
.ltorg
"""
MIX_TICKS = 90             # how long the bowl swirls
MIX_PATCHES = (
    (0x021F5AF0, "add r0, r6, #0x200"),     # no stirring: spin up to a steady speed
    (0x021F5AF4, "ldrh r5, [r0, #0x9c]"),
    (0x021F5AF8, "add r1, r5, #0x40"),
    (0x021F5AFC, "cmp r1, #0x800"),
    (0x021F5B00, "movgt r1, #0x800"),
    (0x021F5B04, "strh r1, [r0, #0x9c]"),
    (0x021F5B08, "b 0x021F5CE0"),
    (0x021F3700, f"cmp r0, #{MIX_TICKS}"),
    (0x021F3720, "cmp r1, #0"),             # no stirring score to reach
    (0x021F5650, "mov r2, #0x5A000"),       # the prompts' cell is built around this point
    (0x021F5654, f"bl {controls.MIX_PROMPTS:#x}"),
    (0x021F4FD8, "mov r0, r6"),             # adding to the bowl keeps the selection
    (0x021F4FDC, "ldr r1, [r6, #0x4C]"),    # and redraws its count
    (0x021F4FE0, "bl 0x021F53C0"),
    (0x021F4FE4, "mov r0, r0"),
    (0x021F3520, f"bl {controls.MIX_START:#x}"),    # no prompts while it swirls
    (0x021F3A6C, f"bl {MIX_BACK:#x}"),      # the three results return to the items
    (0x021F3C58, f"bl {MIX_BACK:#x}"),
    (0x021F3D90, f"bl {MIX_BACK:#x}"),
    (0x021F3A28, f"bl {MIX_WAIT:#x}"),      # and stay on screen until A
    (0x021F3C20, f"bl {MIX_WAIT:#x}"),
    (0x021F3D7C, f"bl {MIX_WAIT:#x}"),
    (0x021F3240, f"bl {controls.MIX_SOUND + 8:#x}"),     # leaving the room frees a kept jingle
    (0x021FD0A4, f"bl {controls.MAT_PULSE:#x}"),    # the smith's materials: only the chosen one pulses
    (0x021FB11C, "mov r2, #0x67"),          # with the item menus' cursor sound
    (0x021FD538, "add r12, r1, #0x87"),     # its selection ring, orange: palette 5503
)
MONEY_FORMAT = 0x021FD7DC   # the shop's money amount
def main():
    rom = open(SRC, "rb").read()
    fd = rom[0x130A00:0x130A00 + 44061128]
    ents = read_lf2(fd)
    reps = {}
    get = lambda i: fd[ents[i][0]:ents[i][0] + ents[i][1]]
    o, s = ents[509]
    _, widths = entext.patch_font(fd[o:o + s])
    version = open(paths.VERSION, encoding="utf-8").read().strip()
    translate.EXTRA[(2199, controls.TITLE_VERSION_MSG)] = controls.title_version_text(version)
    edits, report = translate.load_edits(widths)
    # double-letter glyphs go in font slots no surviving text uses
    used = set()
    for fid in translate.BANKS:
        _, rows = translate.load_bank(fid)
        for k, r in enumerate(rows):
            if k not in edits.get(fid, {}):
                used.update(r)
    for toks in edits.values():
        for t in toks.values():
            used.update(t)
    packer = itemdb.Packer([t for t in range(0x200, entext.X_TOKEN) if t not in used], entext.name_font())
    reps[2176], n = itemdb.patch(get(2176), packer)
    print("database names", n, "double-letter glyphs", len(packer.pairs))
    for fid in (506, 509):
        o, s = ents[fid]
        reps[fid], widths = entext.patch_font(fd[o:o + s], {**packer.pairs, entext.ARROW: controls.ARROW_TOKEN, entext.A_BUTTON: entext.A_TOKEN, entext.X_BUTTON: entext.X_TOKEN})
    for line in report:
        print("CHECK", line)
    print(len(report), "layout warnings")
    for fid, toks in edits.items():
        o, s = ents[fid]
        reps[fid] = entext.rebuild_bank(fd[o:o + s], toks)
    for t, p, m in ((1625, 1624, 1626), (1620, 1621, 1622)):
        reps[t], reps[m] = title_patch.patch(get(t), get(p), get(m))
    reps[465], reps[466] = title_patch.patch(get(465), get(464), get(466), paper=False)
    for c, (top, main, bold) in card_patch.CARDS.items():
        pf = next(i for i in range(c - 1, c - 14, -1) if get(i)[:4] == b"RLCN")
        reps[c - 1] = card_patch.patch(get(c - 1), get(pf), get(c), top, main, bold)
    reps[5308], reps[5311], reps[5309], reps[5310] = card_patch.menu_gear(
        get(5308), *card_patch.menu_labels(get(5311), get(5309), get(5310)))
    reps[1620], reps[1622] = card_patch.patch_copyright(reps[1620], get(1621), reps[1622],
                                                        "(C)2006 Deltora Quest Production Committee, TV Aichi",
                                                        (16, 162, 240, 173))
    for grid, chars, pal, small, name in card_patch.MOVE_TITLES:
        reps[chars] = card_patch.move_title(get(chars), get(grid), get(pal), small, name)[0]
    reps[5523], reps[5521] = card_patch.move_title(get(5523), get(5522), get(5524), None, "Mash A!", get(5521))
    reps[5417], reps[5415], reps[5416], reps[5414] = card_patch.mix_prompts(
        get(5417), get(5415), get(5416), get(5414))
    reps[526] = card_patch.mix_page(get(526))
    reps[525], reps[524] = card_patch.book_buttons(get(525), get(524), reps[526], ((card_patch.mix_switch(), 4, 3),))
    reps[5393], reps[5392], reps[5391] = card_patch.shop_door(get(5393), get(5392), get(5391))
    reps[5567] = card_patch.menu_board(get(5567))
    reps[5316], reps[5315] = card_patch.item_badge(get(5316), get(5315))
    reps[5359] = card_patch.smith_rows(get(5359))
    reps[5592], reps[5591] = card_patch.weapon_effect(get(5592), get(5591))
    reps[5384], reps[5385], reps[5383], reps[5386] = card_patch.title_glow(get(5384), get(5385), get(5383), get(5386))
    for (pal, chars, grid), badges in zip(card_patch.BOOK_PAGES, card_patch.BOOK_BADGES):
        reps[chars], reps[pal] = card_patch.book_buttons(get(chars), get(pal), get(grid), badges)
    reps[5411], reps[5412], reps[5410], reps[5413] = card_patch.sign_highlight(
        card_patch.patch_save_sign(get(5411)), get(5412), get(5410), get(5413))
    # bitmap twins of the Yes/No labels
    src = get(5373)[0x30:0x130], get(5373)[0x1B30:0x1C30]
    table = {src[0]: card_patch._label_tiles("Yes"), src[1]: card_patch._label_tiles("No")}
    for f in (5371, 5376):
        reps[f], n = card_patch.patch_bitmap_labels(get(f), table)
        print("bitmap labels in", f, n)
    for t, pf, m, box, text in ((541, 540, 542, (54, 6, 204, 22), "Items to Use in the Field"),
                                (1674, 1673, 1675, (60, 6, 216, 20), "Deltora Card Trade"),
                                (1677, 1676, 1678, (60, 6, 216, 20), "Trading Deltora Cards…")):
        reps[t], reps[m] = card_patch.patch_bar(get(t), get(pf), get(m), box, text)
    for i, name in enumerate(card_patch.NAME_PLATES):
        f = card_patch.PLATE_BASE + i
        reps[f] = card_patch.patch_name_plate(get(f), name)
    reps[424], reps[425] = card_patch.patch_game_over(get(424), get(423), get(425))
    yes, no = get(5373)[0x30:0x130], get(5373)[0x1B30:0x1C30]
    for i in range(len(ents)):
        if get(i)[:4] == b"RGCN":
            new, n = card_patch.patch_yes_no(reps.get(i, get(i)), yes, no)
            if n:
                reps[i] = new
                print("yes/no rows replaced in", i, n)
    reps[2497] = controls.patch_kin(get(2497))
    reps[2609] = controls.patch_map(get(2609))
    reps[2595] = controls.patch_camp(get(2595))
    reps[2375] = controls.patch_tower_fire(get(2375))     # the Tower's rest rooms: camp 43, with Save
    reps[2608] = controls.patch_tower_load(get(2608))
    reps[2613] = controls.patch_tower_rest(get(2613))
    for fid in mapfix.FIXES:
        reps[fid] = mapfix.patch(fid, get(fid))
    for fid in mapfix.CAMPS:
        reps[fid], n = mapfix.patch_camps(fid, get(fid))
        print('camp moved in', fid, n)
    assert get(2377) == open(drops.ENEMIES, "rb").read()
    reps[2377] = drops.enemies()       # rarer material and gear drops raised
    reps[2380] = controls.patch_hole(get(2380))
    reps[2381] = controls.patch_quiz(get(2381))
    reps[2605] = controls.patch_farm(get(2605))
    reps[2606] = controls.patch_mix_sign(get(2606))     # after the ending: a sign of the unlisted gear mixes
    reps[2618] = controls.patch_sound_test(get(2618))   # the sound test: D-pad, A and B
    reps[2338] = controls.patch_crop(get(2338))
    reps[2386] = controls.patch_belt(get(2386))
    reps[1798] = controls.patch_ending(reps.get(1798, get(1798)))
    for fid, reach in controls.TALK_RANGE.items():
        reps[fid] = controls.patch_talk_range(reps.get(fid, get(fid)), reach)
    reps[controls.GROUP_SPAWNS] = controls.patch_group(get(controls.GROUP_SPAWNS))
    reps[1797] = controls.patch_title_version(controls.patch_title(get(1797)))   # and the patch's version
    reps[2593] = controls.patch_debug_combos(get(2593))
    reps[5378], reps[5376], reps[5377], reps[5375] = card_patch.shop_yes_no(
        reps.get(5378, get(5378)), reps.get(5376, get(5376)), get(5377), get(5375))
    reps[5373], reps[5371], reps[5372], reps[5370], reps[5374] = card_patch.yes_no_highlight(
        reps.get(5373, get(5373)), reps.get(5371, get(5371)), get(5372), get(5370), get(5374))
    reps[5487], reps[5485], reps[5486] = card_patch.prompt_button(
        reps.get(5487, get(5487)), reps.get(5485, get(5485)), get(5486))
    a = rom[0x4000:0x4000 + 845752]
    extra = (MIX_BACK, 104, MIX_BACK_SRC), (MIX_WAIT, 56, MIX_WAIT_SRC)
    out = build_rom.build(rom, reps, controls.install(entext.patch_arm9(a), extra))
    out = bytearray(out)
    fat = struct.unpack_from("<I", out, 0x48)[0]
    money = struct.unpack_from("<I", out, fat + 2 * 8)[0] + MONEY_FORMAT - OVERLAY2_RAM
    assert out[money:money + 4] == b"%7d\0"
    base = money - MONEY_FORMAT
    for addr, line in MIX_PATCHES:
        out[base + addr:base + addr + 4] = entext.asm(line, addr)
    out[money:money + 4] = b"%d\0\0"     # English spaces are too wide to pad with
    out = bytes(out)
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    open(OUT, "wb").write(out)
    print("wrote", OUT, len(out))


if __name__ == "__main__":
    main()
