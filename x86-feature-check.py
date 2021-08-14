#!/usr/bin/env python3

import argparse
import re
import sys

from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Union

FLAG_NAMES = {
    'AVX2': 'avx2',
    'AVX512BW': 'avx512bw',
    'AVX512CD': 'avx512cd',
    'AVX512DQ': 'avx512dq',
    'AVX512F': 'avx512f',
    'AVX512VL': 'avx512vl',
    'AVX': 'avx',
    'BMI1': 'bmi1',
    'BMI2': 'bmi2',
    'CMOV': 'cmov',
    'CMPXCHG16B': 'cx16',
    'CMPXCHG8B': 'cx8',
    'F16C': 'f16c',
    'FMA': 'fma',
    'FPU': 'fpu',
    'FXSR': ['fxsr', 'fxsr_opt'],
    'LAHF': 'lahf_lm',
    'LZCNT': 'abm',
    'MMX': ['mmx', 'mmxext'],
    'MOVBE': 'movbe',
    'OSXSAVE': 'xsave',
    'POPCNT': ['popcnt', 'abm'],
    'SCE': 'syscall',
    'SSE2': 'sse2',
    'SSE3': ['sse3', 'ssse3', 'pni'],
    'SSE4-1': 'sse4_1',
    'SSE4-2': 'sse4_2',
    'SSE': 'sse',
    'SSSE3': 'ssse3',
} # type: Dict[str, Union[str, List[str]]]

REQUIRED_FEATURES = {
    'x86-64-v4': [
        'AVX512BW',
        'AVX512CD',
        'AVX512DQ',
        'AVX512F',
        'AVX512VL',
    ],
    'x86-64-v3': [
        'AVX',
        'AVX2',
        'BMI1',
        'BMI2',
        'F16C',
        'FMA',
        'LZCNT',
        'MOVBE',
        'OSXSAVE',
    ],
    'x86-64-v2': [
        'CMPXCHG16B',
        'LAHF',
        'POPCNT',
        'SSE3',
        'SSE4-1',
        'SSE4-2',
        'SSSE3',
    ],
    'x86-64': [
        'CMOV',
        'CMPXCHG8B',
        'FPU',
        'FXSR',
        'MMX',
        'SCE',
        'SSE',
        'SSE2',
    ],
} # type: Dict[str, List[str]]

"""
List of microarchitecture levels where first entry is the most advanced level
"""
MICROARCHITECTURE_LEVELS = [
    'x86-64-v4',
    'x86-64-v3',
    'x86-64-v2',
    'x86-64',
] # type: List[str]


def main() -> int:
    """
    Main function

    :return: 0 on success, non-zero on error
    :rtype: int
    """
    # parse command line arguments
    parser = argparse.ArgumentParser(description="Check for supported x86_64 feature sets.")
    parser.add_argument("--all", action='store_true', help="show not only the latest, but all supported feature sets.")
    args = parser.parse_args()

    flags = get_current_cpu_flags()

    if args.all:
        feature_sets = get_all_architecture_levels(flags)
        if len(feature_sets) == 0:
            print('No x86-64 feature set fully supported!', file = sys.stderr)
            return 1

        print(' '.join(feature_sets))
    else:
        feature_set = get_max_architecture_level(flags)
        if feature_set is None:
            print('No x86-64 feature set fully supported!', file = sys.stderr)
            return 1

        print(feature_set)

    return 0


def get_cpuinfo() -> str:
    """
    Returns the content of the /proc/cpuinfo file.

    :return: Content of /proc/cpuinfo or empty string if not found
    :rtype: str
    """

    # Read /proc/cpuinfo
    try:
        with open('/proc/cpuinfo', 'r') as f:
            return f.read()
    except IOError:
        print('Error: Could not read /proc/cpuinfo', file = sys.stderr)
        return ''


def extract_cpu_flags(cpuinfo: str) -> Set[str]:
    """
    Extract CPU flags from /proc/cpuinfo string

    :return: Set of CPU flags for which given cpuinfo string indicates support
    :rtype: set
    """

    # Prepare cpuinfo str
    lines = [line.strip() for line in cpuinfo.split('\n')]

    # Get lines defining flags
    flag_lines = []
    flag_line_expression = re.compile(r'^(flags)(\s*:\s*)(.*)$', re.MULTILINE)
    for match in re.findall(flag_line_expression, '\n'.join(lines)):
        flag_lines += [' '.join(match[2].split())]

    # There could be different flags in different flag lines.
    # We add all flags from all flag lines to set in order to
    # get maximum number of flags supported.
    flags = set()
    for line in flag_lines:
        for flag in line.split(' '):
            flags.add(flag)

    return flags


def get_current_cpu_flags() -> Set[str]:
    """
    Returns CPU flags supported by current cpu.

    :return: Set of cpu flags supported
    :rtype: set
    """

    cpuinfo = get_cpuinfo()
    flags = extract_cpu_flags(cpuinfo)
    return flags


def supports_feature(flags: Set[str], feature: str) -> bool:
    """
    Checks if the given flags indicate support of a given feature.

    :param flags: Set of flags to check for support of given feature
    :type flags: set

    :param feature: Feature to check support of
    :type flags: str

    :return: True if support of feature is indicated by given flags.
        False otherwise
    :rtype: bool
    """

    if not isinstance(feature, str):
        raise Exception('Given feature is not of type str')
    if feature not in FLAG_NAMES:
        raise Exception('Unknown feature flag "{}"'.format(feature))

    # Check if there are multiple flags that signal this feature
    flag = FLAG_NAMES[feature]
    if isinstance(flag, str):
        required_flags = [flag]
    elif isinstance(flag, list):
        required_flags = flag

    return True in (flag in flags for flag in required_flags)


def supports_features(flags: Set[str], required_features: List[str]) -> bool:
    """
    Checks if the given flags indicate support of all given features.

    :param flags: Set of flags to check for support of given features
    :type flags: set

    :param required_features: Features to check support of
    :type required_features: list

    :return: True if support of all given features is indicated by flags.
        False otherwise
    :rtype: bool
    """

    return not False in (supports_feature(flags, feat) for feat in required_features)


def supports_feature_set(flags: Set[str], feature_set: str) -> bool:
    """
    Checks if the given flags indicate support of a given feature set.

    :param flags: Set of flags to check for support of given feature set
    :type flags: set

    :param feature_set: Feature set to check support of
    :type feature_set: list

    :return: True if support of feature set is indicated by given flags.
        False otherwise
    :rtype: bool
    """

    if feature_set not in REQUIRED_FEATURES:
        raise Exception('Unknown feature set "{}"'.format(feature_set))

    return supports_features(flags, REQUIRED_FEATURES[feature_set])


def get_max_architecture_level(flags) -> Optional[str]:
    """
    Returns the latest supported microarchitecture level indicated by given flags.

    :param flags: Set of flags to check for microarchitecture level support
    :type flags: set

    :return: The latest microarchitecture level that is supported or None if no
        known microarchitecture level is supported
    :rtype: str
    """

    for microarchitecture_level in MICROARCHITECTURE_LEVELS:
        if supports_feature_set(flags, microarchitecture_level):
            return microarchitecture_level

    return None


def get_all_architecture_levels(flags) -> List[str]:
    supported = [lvl for lvl in MICROARCHITECTURE_LEVELS if supports_feature_set(flags, lvl)]
    supported.reverse()
    return supported


if __name__ == '__main__':
    sys.exit(main())
