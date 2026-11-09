"""Button controls: turn pad input into synthetic stylus input.

All touch passes through FUN_02037500 (pressed?) and FUN_02037560 (read x, y),
once per frame. Both are hooked. Code lives in free ITCM, added as a third
autoload block so nothing else in the ARM9 moves.

The patches are split by feature into the files below. They share one namespace: each part is
run in order into this package, so a constant or function from any part can be used in another's
assembly, as when the code was a single module. Order matters only for module-level constants
that are computed from others.
"""
import math
import struct
import cardinfo
import drops
import entext
import scr
import talk
import os as _os

PARTS = ['core', 'field', 'menus', 'options_and_title', 'shop_and_mixing', 'camp', 'cards', 'minigames', 'world_map', 'file_screen', 'story_scripts']

for _part in PARTS:
    _path = _os.path.join(_os.path.dirname(__file__), _part + ".py")
    exec(compile(open(_path, encoding="utf-8").read(), _path, "exec"), globals())
