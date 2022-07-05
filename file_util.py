import math
import os

FST_STORE = f'{os.environ["USERPROFILE"]}/Documents/Image-Line/FL Studio/Presets/Plugin presets/Effects/Control Surface'
DIRECTORY = os.path.dirname(os.path.realpath(__file__))

FREQUENCIES = {
    freq: (math.log2(freq / 440) * 12 - 3, dir_name)
    for freq, dir_name in {
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
    }.items()
}


def list_scales() -> list[str]:
    return os.listdir(f"{DIRECTORY}/scl")


def setup_fst_dirs():
    for (_, dir_name) in FREQUENCIES.values():
        fst_dir = f"{FST_STORE}/Scala/{dir_name}"
        if not os.path.exists(fst_dir):
            os.mkdir(fst_dir)


class fst_info:
    fst_path: str
    freq: float
    shift: str
    dir_name: float
    scale: str


def get_fst_paths() -> list[fst_info]:
    a = []
    for freq, (shift, dir_name) in FREQUENCIES.items():
        fst_dir = f"{FST_STORE}/Scala/{dir_name}"
        for scale in list_scales():
            i = fst_info()
            i.fst_path = f"{fst_dir}/{scale}.fst"
            i.freq = freq
            i.shift = shift
            i.dir_name = dir_name
            i.scale = scale
            a.append(i)
    return a


class scl_info:
    scl_path: str
    scale: str


def get_scl_paths() -> list[scl_info]:
    a = []
    for scale in list_scales():
        i = scl_info()
        i.scl_path = f"{DIRECTORY}/scl/{scale}"
        i.scale = scale
        a.append(i)
    return a
