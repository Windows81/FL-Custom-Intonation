from file_util import DIRECTORY, FST_STORE
import argparse
import os
import sys
import struct

from scale_util import parse_interval

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
    fst_path: str
    fst_print: bool


def calc(lines: list[str], shift: float) -> tuple[list[tuple[float, int, str]], float]:
    a: list[tuple[float, str]] = [(shift % 12, "1/1")]
    n: int = -1
    c: int = 1
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
            v = parse_interval(l)
            if v % 12 != 0:
                a.append(((v + shift) % 12, l))
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


def interpret(pitch_shift, input_file, fst_file, fst_print, fst) -> info:
    desc: str = None
    a: list[str] = []
    for l in input_file or sys.stdin:
        if not desc:
            desc = l.strip()
            fn = (
                os.path.split(input_file.name)[1]
                if input_file and "<" not in input_file.name
                else "".join(SUB_CHARS.get(c, c) for c in desc)
            )
        a.append(l)

    t = info()
    off = pitch_shift
    t.pitches, t.offset = calc(a, off)
    t.description = desc
    t.fst_print = fst_print
    t.fst_path = (
        fst_file.replace("{}", fn)
        if fst_file
        else f"{FST_STORE}/{fn}.fst"
        if fst
        else None
    )
    return t


def output_pitches(t: info):
    for (s, i, l) in t.pitches:
        base = f'{KEYS[i]} {s*100:+06.1f} cents - "{l}"'
        if t.fst_print:
            base = f'[{(s+1)/2:6.6f}] ' + base
        print(base)


def output_table(t: info):
    print(t.description)
    output_pitches(t)
    base = f"   {t.offset*100:+06.1f} cents"
    if t.fst_print:
        base = f'[{(t.offset+12)/24:6.6f}] ' + base
    print(base)
    fst_from_file(t)


def fst_from_file(t: info) -> bool:
    if not t.fst_path:
        return False
    rf = open(f"{DIRECTORY}/_template.fst", "rb")
    b = list(rf.raw.readall())
    FST_OFFSET = FST_SEEK[12]
    for (s, *_), p in zip(t.pitches, FST_SEEK):
        b[p: p + 4] = struct.pack("f", 0.5 + s / 2)
    b[FST_OFFSET: FST_OFFSET + 4] = struct.pack("f", 0.5 + t.offset / 24)
    wf = open(t.fst_path, "wb")
    wf.write(bytes(b))
    rf.close()
    wf.close()
    return True


def parse_args():
    a = argparse.ArgumentParser()
    a.add_argument("input_file", type=argparse.FileType("r"))
    a.add_argument("--pitch-shift", "-o", type=float, default=0)
    a.add_argument("--fst", "-b", action="store_true")
    a.add_argument("--fst-print", "-c", action="store_true")
    a.add_argument("--fst-file", type=str)
    return a.parse_args()


if __name__ == "__main__":
    try:
        output_table(interpret(**parse_args().__dict__))
    except ValueError as x:
        print(x.args[0])
        if len(x.args) > 1:
            print("\nERROR LOG:")
            output_pitches(x.args[1])
        exit(1)
