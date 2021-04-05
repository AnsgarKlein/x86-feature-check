# x86-feature-check

`x86-feature-check.py` checks `/proc/cpuinfo` for CPU flags and outputs the maximum
[x86-64 feature set](https://en.wikipedia.org/wiki/X86-64#Microarchitecture_Levels)
that is supported.

Possible valid values:
- x86-64
- x86-64-v2
- x86-64-v3
- x86-64-v4

This script relies on `/proc/cpuinfo` and thus only works on Linux.
