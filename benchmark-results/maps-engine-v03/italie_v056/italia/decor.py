"""Lettering and compass rose as stud bitmaps -> real LEGO tiles (1x1 / 1x2 / 1x4 / 2x2 with groove) laid on sea plates. No raster, no print."""
import math
FONT = {"I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"], "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
        "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"], "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
        "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."], "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"], "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
        "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#", "#...#", "#...#"], "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"], "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."]}
def text_cells(text, gap=1):
    cells = set(); x = 0
    for ch in text:
        g = FONT[ch]
        for r, row in enumerate(g):
            for c, v in enumerate(row):
                if v == "#": cells.add((r, x + c))
        x += len(g[0]) + gap
    return cells, (7, x - gap)
def compass_cells(d=15):
    """{(r,c): role} : ring, four tapered cardinal blades (north in red), short diagonal points, centre. d odd, blade length d//2 - 1"""
    n = d // 2; out = {}; L = n - 1
    for r in range(-n, n + 1):
        for c in range(-n, n + 1):
            if abs(math.hypot(r, c) - n) < 0.62: out[(r + n, c + n)] = "ring"
    for t in range(1, L + 1):
        hw = (L - t) // 2
        for p in range(-hw, hw + 1):
            for (r, c, role) in ((-t, p, "north"), (t, p, "blade"), (p, t, "blade"), (p, -t, "blade")): out[(r + n, c + n)] = role
    for t in range(2, 5): 
        for (r, c) in ((t, t), (-t, t), (t, -t), (-t, -t)): out[(r + n, c + n)] = "diag"
    out[(n, n)] = "centre"; return out
