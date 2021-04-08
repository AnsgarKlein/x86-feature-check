#!/usr/bin/env python3

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

X86_64_REQUIRED_FEATURES = [
    'CMOV',
    'CMPXCHG8B',
    'FPU',
    'FXSR',
    'MMX',
    'SCE',
    'SSE',
    'SSE2',
] # type: List[str]

X86_64_V2_REQUIRED_FEATURES = [
    'CMPXCHG16B',
    'LAHF',
    'POPCNT',
    'SSE3',
    'SSE4-1',
    'SSE4-2',
    'SSSE3',
] # type: List[str]

X86_64_V3_REQUIRED_FEATURES = [
    'AVX',
    'AVX2',
    'BMI1',
    'BMI2',
    'F16C',
    'FMA',
    'LZCNT',
    'MOVBE',
    'OSXSAVE',
] # type: List[str]

X86_64_V4_REQUIRED_FEATURES = [
    'AVX512BW',
    'AVX512CD',
    'AVX512DQ',
    'AVX512F',
    'AVX512VL',
] # type: List[str]

def main() -> int:
    """
    Main function

    :return: 0 on success, non-zero on error
    :rtype: int
    """

    flags = get_current_cpu_flags()
    feature_set = get_max_feature_set(flags)

    if feature_set is None:
        print('No x86-64 feature set fully supported!', file = sys.stderr)
        return 1

    print('{}'.format(get_max_feature_set(flags)))
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

def has_feature(flags: Set[str], feature: str) -> bool:
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

def supports_feature_set(flags: Set[str], featureset: List[str]) -> bool:
    """
    Checks if the given flags indicate support of a given feature set.

    :param flags: Set of flags to check for support of given feature set
    :type flags: set

    :param featureset: Feature set to check support of
    :type featureset: list

    :return: True if support of feature set is indicated by given flags.
        False otherwise
    :rtype: bool
    """

    return not False in (has_feature(flags, feat) for feat in featureset)

def supports_x86v1(flags: Set[str]) -> bool:
    """
    Checks if the given flags indicate support for x86-64 (baseline) feature set.

    :param flags: Set of flags to check for support of x86-64 (baseline)
    :type flags: set

    :return: True if support of x86-64 (baseline) is indicated by given flags.
        False otherwise
    :rtype: bool
    """

    return supports_feature_set(flags, X86_64_REQUIRED_FEATURES)

def supports_x86v2(flags: Set[str]) -> bool:
    """
    Checks if the given flags indicate support for x86-64-v2 feature set.

    :param flags: Set of flags to check for support of x86-64-v2
    :type flags: set

    :return: True if support of x86-64-v2 is indicated by given flags.
        False otherwise
    :rtype: bool
    """

    return supports_feature_set(flags, X86_64_V2_REQUIRED_FEATURES)

def supports_x86v3(flags: Set[str]) -> bool:
    """
    Checks if the given flags indicate support for x86-64-v3 feature set.

    :param flags: Set of flags to check for support of x86-64-v3
    :type flags: set

    :return: True if support of x86-64-v3 is indicated by given flags.
        False otherwise
    :rtype: bool
    """

    return supports_feature_set(flags, X86_64_V3_REQUIRED_FEATURES)

def supports_x86v4(flags: Set[str]) -> bool:
    """
    Checks if the given flags indicate support for x86-64-v4 feature set.

    :param flags: Set of flags to check for support of x86-64-v4
    :type flags: set

    :return: True if support of x86-64-v4 is indicated by given flags.
        False otherwise
    :rtype: bool
    """

    return supports_feature_set(flags, X86_64_V4_REQUIRED_FEATURES)

def get_max_feature_set(flags) -> Optional[str]:
    """
    Returns the latest supported feature set indicated by given flags.

    :param flags: Set of flags to check for feature set support
    :type flags: set

    :return: The latest feature set that is supported or None if no
        known feature set is supported
    :rtype: str
    """

    if supports_x86v1(flags):
        if supports_x86v2(flags):
            if supports_x86v3(flags):
                if supports_x86v4(flags):
                    return 'x86-64-v4'
                return 'x86-64-v3'
            return 'x86-64-v2'
        return 'x86-64'

    return None

if __name__ == '__main__':
    sys.exit(main())
