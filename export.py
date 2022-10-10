from add_scale import fst_from_file, calc, info
from file_util import get_fst_paths, setup_fst_dirs
import os.path
import os


def export():
    setup_fst_dirs()
    for f in get_fst_paths():
        if os.path.exists(f.fst_path):
            continue
        try:
            i = info()
            i.description = ""
            i.fst_path = f.fst_path
            i.pitches, i.offset = calc(open(f"./scl/{f.scale}"), f.shift)
            if fst_from_file(i):
                print(f'Successfully parsed at {f.dir_name}: "{f.scale}"')
        except ValueError:
            pass


if __name__ == "__main__":
    export()
