#!/bin/env python3

import subprocess
import sys
import os


class Size(object):
    _value = None
    _unit = None

    def __init__(self, value, unit):
        self._value = value
        self._unit = unit

    def _unit_less_than(self, other):
        # The units are the same; compare the numbers
        if self._unit == other:
            return -1

        # The other has no unit; this must be greater
        if other is None:
            return False

        # This has no unit; the other must be greater
        if self._unit is None:
            return True

        # Since we've already covered equal units, if this unit is G, it must
        # be greater
        if self._unit == "G":
            return False

        # Since we've already established that this isn't G, if the other is G,
        # the other must be greater
        if other == "G":
            return True

        # k < m, therefore if this is less than that, this must be smaller
        if self._unit < other:
            return True

        # Otherwise, this must be greater
        return False

    def __lt__(self, other):
        unit_result = self._unit_less_than(other._unit)
        if unit_result != -1:
            return unit_result

        return self._value < other._value

    def __str__(self):
        return "%d%s" % (self._value,
                         self._unit if self._unit is not None else "B")


def get_folder_size(folder):
    try:
        size = subprocess.check_output(
            ["du", "-sh", folder]).decode('UTF-8').strip('\n').split('\t')[0]
    except subprocess.CalledProcessError:
        print("Error: unable to find size of file/folder %s" % folder)
        return Size(0, None)

    # If du returns no unit (i.e., this many bytes)
    to_convert = float if "." in size else int
    try:
        int(size[-1])
        return Size(to_convert(size), None)
    except ValueError:
        return Size(to_convert(size[:-1]), size[-1])


def fix_str_len(to_fix, length, empty_fill=" ", extra_term="..."):
    if len(to_fix) < length:
        return to_fix + (empty_fill * (length - len(to_fix)))
    if len(to_fix) > length:
        return to_fix[:-(len(to_fix) - (length + 3))] + extra_term


def main():
    if len(sys.argv) < 2:
        folder = os.getcwd()
    else:
        folder = sys.argv[1]

    try:
        contents = [x for x in os.listdir(folder) if not x.startswith(".")]
    except NotADirectoryError:
        print("Error: %s is not a directory." % folder)
        print("Usage: sizesrt [directory]")
        print("If no arguments provided, sizsrt runs in the current directory")
        sys.exit(1)

    os.chdir(folder)
    sizes = {}
    for item in contents:
        size = get_folder_size(item)
        sizes[size] = item

    thing = sorted(list(sizes.keys()))

    print(fix_str_len("File", 25), "\t\tSize")
    print("-" * 32, "\t-----")

    for item in thing:
        print("%s\t\t%s" % (fix_str_len(sizes[item], 25), item))

if __name__ == '__main__':
    main()
