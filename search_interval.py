from file_util import get_scl_paths
from scale_util import parse_interval
import argparse
import math


def search(lines: list[str], smtn_diffs: list[float], epsilon: float = 1e-9):
    a: list[(float, str)] = [(0, "1/1")]
    smtn_diffs = [s % 12 for s in smtn_diffs]
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
                a.append((v, l))
                c += 1

    matches: list[tuple[str, str]] = []
    match_set = set(smtn_diffs)
    for i in range(0, len(a)):
        for j in range(i + 1, len(a)):
            diff = abs((a[i][0] - a[j][0]) % 12)
            for s in smtn_diffs:
                if math.isclose(diff, s, abs_tol=epsilon):
                    matches.append((a[j][1], a[i][1]))
                    match_set.discard(s)
                elif math.isclose(12 - diff, s, abs_tol=epsilon):
                    matches.append((a[i][1], a[j][1]))
                    match_set.discard(s)
    if match_set:
        return []
    return matches


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("interval", type=parse_interval, nargs="+")
    a.add_argument("--epsilon", type=float, nargs="?", default=1e-4)
    args = a.parse_args()

    d = {}
    for i in get_scl_paths():
        with open(i.scl_path) as f:
            try:
                r = search(f.readlines(), args.interval, args.epsilon)
                l = len(r)
                if l > 0:
                    d[i.scale] = r
                    print(f'- "{i.scale}":')
                    print(f"{l:2d} matching interval(s) found:")
                    for (l1, l2) in r:
                        print(f"{l1:>13s} » {l2:<13s}")
                    print()
            except ValueError:
                pass
