import argparse
import os
import math
import sys
import struct
import re

KEYS = ["C ", "C#", "D ", "D#", "E ", "F ", "F#", "G ", "G#", "A ", "A#", "B "]
FST_SEEK = [
    2407,
    325,
    4489,
    6573,
    8655,
    10737,
    12821,
    14903,
    16987,
    19069,
    21153,
    23235,
    25337,
]

SUB_CHARS = {
    "[": "{",
    "]": "}",
    "/": "-",
    "\\": "-",
    ";": "-",
    ",": "-",
    ">": "-",
    "<": "-",
    "&": "-",
    "*": "-",
    ":": "-",
    "%": "-",
    "=": "-",
    "+": "-",
    "@": "-",
    "!": "-",
    "#": "-",
    "^": "-",
    "(": "-",
    ")": "-",
    "|": "-",
    "?": "-",
    "^": "-",
}


class info:
    description: str
    offset: float
    pitches: list[float]
    fst: str


def parse():
    a = argparse.ArgumentParser()
    a.add_argument("file", type=argparse.FileType("r"))
    a.add_argument("-o", "--pitch-shift", type=float, default=0)
    a.add_argument("--fst", action="store_true")
    return a.parse_args()


def calc(o):
    desc: str = None
    a: list[(float, str)] = []
    n: int = -1
    c: int = 0
    for l in o.file or sys.stdin:
        l = l.strip()
        if l.startswith("!"):
            continue
        elif not desc:
            desc = l
            fn = (
                os.path.split(o.file.name)[1]
                if o.file and "<" not in o.file.name
                else "".join(SUB_CHARS.get(c, c) for c in desc)
            )
        elif n == -1:
            n = int(l)
            if n > 12:
                raise ValueError(f"Should contain at most twelve notes, but has {n}.")
        elif c < 12:
            f = l.split(" ", 1)[0].split("/")
            v = (
                (
                    12 * math.log2(int(f[0]) / int(f[1] if len(f) > 1 else 1))
                    if not "." in l
                    else float(f[0]) / 100
                )
                + o.pitch_shift
            ) % 12
            a.append((v, l))
            c += 1
    a.sort()
    if c < 12:
        t = c
        a += [None] * (12 - c)
        while t > 0:
            t -= 1
            v = a[t]
            a[t] = None
            if v[0] < 12:
                i2 = int(v[0])
                if a[i2 - 1] is None:
                    a[i2 - 1] = v
                if a[i2] is None:
                    a[i2 + 0] = v
                if i2 < 11 and a[i2 + 1] is not None and a[i2 + 0][0] == a[i2 + 1][0]:
                    if i2 > 1 and a[i2 - 1][0] == a[i2 + 0][0]:
                        a[i2 - 1] = v
                    a[i2 + 0] = v
                if i2 < 11 and a[i2 + 1] is None:
                    a[i2 + 1] = v
                if i2 < 10 and a[i2 + 0] is not None and a[i2 + 1][0] == a[i2 + 2][0]:
                    a[i2 + 1] = v
        if a[0] is None and not a[11] is None:
            a[0] = (a[11][0] - 12, *a[11][1:])

    if any(map(lambda n: n is None, a)):
        d = [(t[0] - i, i, *t[1:]) if t else (0, i, None) for i, t in enumerate(a)]
        raise ValueError("Some intervals were not able to be filled.", d)

    d = [(s - i, i, *e) for i, (s, *e) in enumerate(a)]
    mn, mx, off = min(d)[0], max(d)[0], 0
    if mx - mn > 2:
        raise ValueError("Intervals are too far apart to use in Patcher.", d)
    elif mn < -1 or mx > 1:
        off = (mx + mn) / 2
        d = [(s - off, *e) for s, *e in d]

    t = info()
    t.description = desc
    t.pitches = d
    t.offset = off
    t.fst = (
        f'{os.environ["USERPROFILE"]}/Documents/Image-Line/FL Studio/Presets/Plugin presets/Effects/Control Surface/{fn}.fst'
        if o.fst
        else None
    )
    return t


def output_pitches(t):
    for (s, i, l) in t:
        print(f'{KEYS[i]} {s*100:+06.1f} cents - "{l}"')


def output_table(t: info):
    print(t.description)
    output_pitches(t.pitches)
    print(f"   {t.offset*100:+06.1f} cents")
    fst_from_file(t)


def fst_from_file(t: info):
    if not t.fst:
        return
    rf = open(sys.path[0] + "/_template.fst", "rb")
    b = list(rf.raw.readall())
    FST_OFFSET = FST_SEEK[12]
    for (s, *_), p in zip(t.pitches, FST_SEEK):
        b[p : p + 4] = struct.pack("f", 0.5 + s / 2)
    b[FST_OFFSET : FST_OFFSET + 4] = struct.pack("f", 0.5 + t.offset / 24)
    wf = open(t.fst, "wb")
    wf.write(bytes(b))
    rf.close()
    wf.close()


if __name__ == "__main__":
    try:
        output_table(calc(parse()))
    except ValueError as x:
        print(x.args[0])
        if len(x.args) > 1:
            print("\nERROR LOG:")
            output_pitches(x.args[1])
        exit(1)
