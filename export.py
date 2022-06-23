from add_scale import fst_from_file
from add_scale import FST_STORE
from add_scale import DIRECTORY
from add_scale import calc
from add_scale import info
import math
import os.path
import os

a = {
    523.251: "~523.251 Hz [C♮]",
    400.000: "400 Hz [G+]",
    432.000: "432 Hz [A−]",
    440.000: "440 Hz [A♮]",
    480.000: "480 Hz [B−]",
    500.000: "500 Hz [B+]",
    512.000: "512 Hz [C−]",
    576.000: "576 Hz [D−]",
    600.000: "600 Hz [D+]",
    640.000: "640 Hz [E−]",
    672.000: "672 Hz [E+]",
    720.000: "720 Hz [F+]",
    768.000: "768 Hz [G−]",
}

for freq, dir_name in a.items():
    shift = math.log2(freq / 440) * 12 - 3
    fst_dir = f"{FST_STORE}/Scala/{dir_name}"
    if not os.path.exists(fst_dir):
        os.mkdir(fst_dir)
    for l in os.listdir(f"{DIRECTORY}/scl"):
        fst = f"{fst_dir}/{l}.fst"
        if os.path.exists(fst):
            continue
        try:
            i = info()
            i.description = ""
            i.fst = fst
            i.pitches, i.offset = calc(open(f"./scl/{l}"), shift)
            fst_from_file(i)
            print(f'Successfully parsed at {dir_name}: "{l}"')
        except ValueError:
            pass
