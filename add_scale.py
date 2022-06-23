import argparse
import os
import math
import sys
import struct

DIRECTORY = os.path.dirname(os.path.realpath(__file__))
FST_STORE = f'{os.environ["USERPROFILE"]}/Documents/Image-Line/FL Studio/Presets/Plugin presets/Effects/Control Surface'
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
    pitches: list[tuple[float, int, str]]
    fst: str


def calc(lines: list[str], shift: float) -> tuple[list[tuple[float, int, str]], float]:
    a: list[(float, str)] = []
    n: int = -1
    c: int = 0
    for l in lines:
        l = l.strip()
        if l.startswith("!") or l == "":
            continue
        elif n == -1:
            n -= 1
        elif n == -2:
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
                + shift
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
                if a[i2 + 0] is None:
                    a[i2 + 0] = v
                if i2 < 11 and a[i2 + 1] is not None and a[i2 + 0][0] == a[i2 + 1][0]:
                    if i2 > 1 and a[i2 - 1][0] == a[i2 + 0][0]:
                        a[i2 - 1] = v
                    a[i2 + 0] = v
                if i2 < 11 and a[i2 + 1] is None:
                    a[i2 + 1] = v
                if i2 < 10 and a[i2 + 2] is not None and a[i2 + 1][0] == a[i2 + 2][0]:
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
    return d, off


def interpret(o) -> info:
    desc: str = None
    a: list[str] = []
    for l in o.file or sys.stdin:
        if not desc:
            desc = l.strip()
            fn = (
                os.path.split(o.file.name)[1]
                if o.file and "<" not in o.file.name
                else "".join(SUB_CHARS.get(c, c) for c in desc)
            )
        a.append(l)

    t = info()
    off = o.pitch_shift
    t.pitches, t.offset = calc(a, off)
    t.description = desc
    t.fst = (
        o.fst_file.replace("{}", fn)
        if o.fst_file
        else f"{FST_STORE}/{fn}.fst"
        if o.fst
        else None
    )
    return t


def output_pitches(t: info):
    for (s, i, l) in t.pitches:
        print(f'{KEYS[i]} {s*100:+06.1f} cents - "{l}"')


def output_table(t: info):
    print(t.description)
    output_pitches(t)
    print(f"   {t.offset*100:+06.1f} cents")
    fst_from_file(t)


def fst_from_file(t: info):
    if not t.fst:
        return
    rf = open(f"{DIRECTORY}/_template.fst", "rb")
    b = list(rf.raw.readall())
    FST_OFFSET = FST_SEEK[12]
    for (s, *_), p in zip(t.pitches, FST_SEEK):
        b[p : p + 4] = struct.pack("f", 0.5 + s / 2)
    b[FST_OFFSET : FST_OFFSET + 4] = struct.pack("f", 0.5 + t.offset / 24)
    wf = open(t.fst, "wb")
    wf.write(bytes(b))
    rf.close()
    wf.close()


def parse_args():
    a = argparse.ArgumentParser()
    a.add_argument("file", type=argparse.FileType("r"))
    a.add_argument("-o", "--pitch-shift", type=float, default=0)
    a.add_argument("--fst", "-b", action="store_true")
    a.add_argument("--fst-file", type=str)
    return a.parse_args()


if __name__ == "__main__":
    try:
        output_table(interpret(parse_args()))
    except ValueError as x:
        print(x.args[0])
        if len(x.args) > 1:
            print("\nERROR LOG:")
            output_pitches(x.args[1])
        exit(1)
