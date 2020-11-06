import re

__all__ = [
    "parse_cpu",
    "parse_memory"
]

cpu_re = re.compile(r"^([0-9]+)m$")


def parse_cpu(string):
    milliMatch = cpu_re.match(string)
    if milliMatch:
        return float(milliMatch.group(1)) / 1000
    # TODO use float?
    return float(string)


memoryMultipliers = {
    "k": 1000,
    "M": 1000 ** 2,
    "G": 1000 ** 3,
    "T": 1000 ** 4,
    "P": 1000 ** 5,
    "E": 1000 ** 6,
    "Ki": 1024,
    "Mi": 1024 ** 2,
    "Gi": 1024 ** 3,
    "Ti": 1024 ** 4,
    "Pi": 1024 ** 5,
    "Ei": 1024 ** 6,
}


memory_re = re.compile(r"^([0-9]+)([A-Za-z]+)$")


def parse_memory(s):
    unitMatch = memory_re.match(s)
    if unitMatch:
        return int(unitMatch.group(1)) * memoryMultipliers[unitMatch.group(2)]
    return int(s)
