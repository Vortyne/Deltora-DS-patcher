"""The seven gems of Deltora on one ring of light: the belt's circle drawn as a halo, with the gems
on it in the order that spells DELTORA clockwise from the lower left. Writes docs/gems.svg.

    python art/make_gems.py
"""
import math
import os

W = H = 760
CX, CY = W / 2, H / 2
RING = 255                  # the circle the gems sit on, and the halo
SPREAD = 49                 # degrees between neighbouring gems
GEM = (44, 34)
LIGHT = "#d6f4ff"           # the halo: white-hot light blue at its heart
LIGHT_EDGE = "#5cc8ff"      # and a deeper blue where it burns off

# DELTORA: (body centre, body mid, body rim, light veins, dark veins, glow)
GEMS = [
    ("diamond", ("#ffffff", "#d3f0ff", "#4a7fae", "#ffffff", "#8fc6ea", "#d8f2ff")),
    ("emerald", ("#b4ffca", "#14ad4a", "#022a11", "#c8ff8a", "#013d18", "#2dff7a")),
    ("lapis", ("#7f9fff", "#1d40c4", "#050e46", "#90aeff", "#06155e", "#3f72ff")),
    ("topaz", ("#fff2a8", "#f5a417", "#552800", "#ffd94e", "#743800", "#ffb52e")),
    ("opal", ("#3d6f8c", "#14304a", "#040d16", None, None, "#5fd8ff")),
    ("ruby", ("#ff9090", "#d3061e", "#3a000a", "#ff5d6d", "#55000f", "#ff2d48")),
    ("amethyst", ("#f0caff", "#8b2bd8", "#20053c", "#d69aff", "#360962", "#b45cff")),
]
OPAL_FIRE = [("#2fff6e", 4), ("#22c8ff", 17), ("#ff8a1a", 29), ("#ff2f4f", 41)]


def stops(pairs):
    return "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in pairs)


def noise(fid, colour, freq, octaves, seed, gain, bias, blur=0):
    """Noise turned into veins or patches of one colour: alpha = gain * noise + bias, so only the
    noise's peaks show."""
    r, g, b = (int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    soften = f'<feGaussianBlur stdDeviation="{blur}"/>' if blur else ""
    return (f'<filter id="{fid}" x="0" y="0" width="100%" height="100%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{freq:.3f}" numOctaves="{octaves}" seed="{seed}"/>'
            f'<feColorMatrix type="matrix" values="0 0 0 0 {r:.3f}  0 0 0 0 {g:.3f}  0 0 0 0 {b:.3f}  {gain} 0 0 0 {bias}"/>{soften}</filter>')


def defs():
    out = ['<filter id="blur1" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="0.8"/></filter>',
           '<filter id="blur2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2"/></filter>',
           '<filter id="blur-glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="7"/></filter>',
           '<filter id="blur-wide" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="20"/></filter>',
           noise("crackle", "#ffffff", 0.12, 2, 77, 4.2, -2.5),
           flame("flame-wide", "0.018 0.045", 46, 5, 12),
           flame("flame-tight", "0.03 0.07", 22, 2.5, 31)]
    out.append(f'<radialGradient id="flare-bloom">{stops([(0, LIGHT, 0.95), (0.25, LIGHT_EDGE, 0.55), (0.6, LIGHT_EDGE, 0.15), (1, LIGHT_EDGE, 0)])}</radialGradient>')
    out.append(f'<radialGradient id="flare-core">{stops([(0, "#ffffff", 1), (0.3, "#ffffff", 1), (0.55, LIGHT, 0.7), (1, LIGHT, 0)])}</radialGradient>')
    out += [noise(f"fire-{seed}", c, 0.05, 1, seed, 6, -3.3, 0.9) for c, seed in OPAL_FIRE]
    for i, (name, (c0, c1, c2, light, dark, glow)) in enumerate(GEMS):
        out.append(f'<radialGradient id="body-{name}" cx="50%" cy="50%" r="60%" fx="46%" fy="40%">'
                   f'{stops([(0, c0, 1), (0.45, c1, 1), (1, c2, 1)])}</radialGradient>')
        out.append(f'<radialGradient id="glow-{name}">{stops([(0, glow, 0.8), (0.4, glow, 0.3), (1, glow, 0)])}</radialGradient>')
        if light:
            out.append(noise(f"vl-{name}", light, 0.026 + 0.004 * i, 3, i * 7 + 3, 3.3, -1.75))
            out.append(noise(f"vd-{name}", dark, 0.034 + 0.003 * i, 2, i * 7 + 5, 3.1, -1.55))
    return out


def ring_of_light():
    """One halo behind all seven gems, light blue and burning: a wide glow, two bands whose edges
    are pushed about by noise so they flicker like flame, and a white-hot core."""
    c = f'cx="{CX}" cy="{CY}" r="{RING}" fill="none"'
    return (f'<circle {c} stroke="{LIGHT_EDGE}" stroke-opacity="0.35" stroke-width="120" filter="url(#blur-wide)"/>'
            f'<circle {c} stroke="{LIGHT_EDGE}" stroke-opacity="0.75" stroke-width="44" filter="url(#flame-wide)"/>'
            f'<circle {c} stroke="{LIGHT}" stroke-opacity="0.9" stroke-width="18" filter="url(#flame-tight)"/>'
            f'<circle {c} stroke="#ffffff" stroke-opacity="0.95" stroke-width="5" filter="url(#blur2)"/>')


def lens_flare():
    """A bright light-blue flare at the centre of the ring: a wide soft bloom, a thin ring around
    it, and a white-hot core."""
    c = f'cx="{CX}" cy="{CY}"'
    return (f'<circle {c} r="225" fill="url(#flare-bloom)"/>'
            f'<circle {c} r="92" fill="none" stroke="{LIGHT_EDGE}" stroke-opacity="0.5" stroke-width="4" filter="url(#blur2)"/>'
            f'<circle {c} r="140" fill="none" stroke="{LIGHT}" stroke-opacity="0.18" stroke-width="10" filter="url(#blur-glow)"/>'
            f'<circle {c} r="95" fill="url(#flare-core)"/>')


def flame(fid, freq, scale, blur, seed):
    """Noise pushes the stroke's pixels about (wider apart along the ring than across it), then a
    blur softens them: a flickering, flame-like edge."""
    return (f'<filter id="{fid}" x="-20%" y="-20%" width="140%" height="140%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="3" seed="{seed}" result="n"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="n" scale="{scale}" xChannelSelector="R" yChannelSelector="G" result="d"/>'
            f'<feGaussianBlur in="d" stdDeviation="{blur}"/></filter>')


def inside(name, gx, gy):
    """The gem: a glowing body, its veins, fire or crackle, depth at the rim, and the polish."""
    box = f'x="{-gx}" y="{-gy}" width="{2 * gx}" height="{2 * gy}"'
    out = [f'<ellipse rx="{gx}" ry="{gy}" fill="url(#body-{name})"/>']
    if name == "opal":
        out += [f'<rect {box} filter="url(#fire-{seed})" opacity="0.95"/>' for _, seed in OPAL_FIRE]
    else:
        out += [f'<rect {box} filter="url(#vl-{name})" opacity="0.55"/>',
                f'<rect {box} filter="url(#vd-{name})" opacity="0.5"/>']
    if name == "diamond":
        out.append(f'<rect {box} filter="url(#crackle)" opacity="0.6"/>')
        pts = [(gx * math.cos(math.radians(a)), gy * math.sin(math.radians(a))) for a in range(0, 360, 30)]
        mid = [(x * 0.5, y * 0.5) for x, y in pts]
        for k in range(len(pts)):
            p, q, m, n = pts[k], pts[(k + 1) % 12], mid[k], mid[(k + 1) % 12]
            out.append(f'<polygon points="{p[0]:.1f},{p[1]:.1f} {q[0]:.1f},{q[1]:.1f} {n[0]:.1f},{n[1]:.1f} {m[0]:.1f},{m[1]:.1f}" '
                       f'fill="{"#ffffff" if k % 2 else "#9ccbee"}" opacity="0.28" stroke="#ffffff" stroke-opacity="0.7" stroke-width="0.6"/>')
        out.append('<polygon points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in mid)
                   + '" fill="#ffffff" opacity="0.25" stroke="#ffffff" stroke-width="0.7"/>')
    out.append(f'<ellipse rx="{gx}" ry="{gy}" fill="none" stroke="#000000" stroke-opacity="0.55" stroke-width="11" filter="url(#blur2)"/>')
    return "".join(out)


def polish(gx, gy):
    """The light on the gem's surface, always from the upper left whichever way the gem lies; kept
    within its shorter radius so it stays on the gem."""
    gx = gy
    out = [
        f'<ellipse cy="{gy * 0.15:.1f}" rx="{gx * 0.45:.1f}" ry="{gy * 0.38:.1f}" fill="#ffffff" opacity="0.16" filter="url(#blur-glow)"/>',
        f'<ellipse cx="{-gx * 0.16:.1f}" cy="{-gy * 0.5:.1f}" rx="{gx * 0.62:.1f}" ry="{gy * 0.3:.1f}" fill="#ffffff" opacity="0.3" filter="url(#blur2)"/>',
        f'<path d="M {-gx * 0.64:.1f} {-gy * 0.24:.1f} Q {-gx * 0.5:.1f} {-gy * 0.8:.1f} {gx * 0.08:.1f} {-gy * 0.76:.1f} '
        f'Q {-gx * 0.36:.1f} {-gy * 0.6:.1f} {-gx * 0.64:.1f} {-gy * 0.24:.1f} Z" fill="#ffffff" opacity="0.88" filter="url(#blur1)"/>',
        f'<circle cx="{-gx * 0.5:.1f}" cy="{-gy * 0.42:.1f}" r="2.2" fill="#ffffff"/>',
        f'<path d="M {-gx * 0.56:.1f} {gy * 0.72:.1f} Q 0 {gy * 1.02:.1f} {gx * 0.56:.1f} {gy * 0.72:.1f}" fill="none" '
        f'stroke="#ffffff" stroke-opacity="0.45" stroke-width="2" filter="url(#blur1)"/>',
    ]
    return "".join(out)


def gem(name, i):
    gx, gy = GEM
    angle = -90 + (i - 3) * SPREAD                     # D at the lower left, A at the lower right
    x, y = CX + RING * math.cos(math.radians(angle)), CY + RING * math.sin(math.radians(angle))
    turn = f"rotate({angle + 90:.1f})"                 # the long axis along the halo
    return f'''<g transform="translate({x:.1f} {y:.1f})">
  <circle r="{gx * 1.8:.0f}" fill="url(#glow-{name})" opacity="0.7"/>
  <clipPath id="clip-{name}"><ellipse rx="{gx}" ry="{gy}" transform="{turn}"/></clipPath>
  <g clip-path="url(#clip-{name})">
    <g transform="{turn}">{inside(name, gx, gy)}</g>
    {polish(gx, gy)}
  </g>
  <ellipse rx="{gx}" ry="{gy}" transform="{turn}" fill="none" stroke="#0e1013" stroke-opacity="0.6" stroke-width="1.2"/>
</g>'''


def main():
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
             "<title>The seven gems of Deltora</title>",
             "<defs>", *defs(), "</defs>", lens_flare(), ring_of_light()]
    parts += [gem(name, i) for i, (name, _) in enumerate(GEMS)]
    parts.append("</svg>")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "gems.svg")
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(parts) + "\n")
    print("wrote", os.path.normpath(out))


if __name__ == "__main__":
    main()
