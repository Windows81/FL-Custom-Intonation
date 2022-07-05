import math


def parse_interval(l: str) -> float:
    l = l.strip()
    if "/" in l:
        f = l.split("/")
        return 12 * math.log2(float(f[0]) / float(f[1]))
    elif "\\" in l:
        f = l.split("\\")
        return float(f[0]) / float(f[1]) * 12
    return float(l) / 100
