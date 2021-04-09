#!/usr/bin/env python3

import importlib
import os
import unittest

x86_feature_check = importlib.import_module('x86-feature-check')
importlib.invalidate_caches()

def get_resource(filename):
    """Returns the content of a resource with the given filename."""

    dirname = os.path.dirname(__file__)
    resource_path = os.path.join(dirname, 'resources')
    file_path = os.path.join(resource_path, filename)
    with open(file_path, 'r') as f:
        return f.read()

class Test_Main(unittest.TestCase):
    def test_get_current_cpu_flags(self):
        current_flags = x86_feature_check.get_current_cpu_flags()
        self.assertTrue(isinstance(current_flags, set))

        for flag in current_flags:
            self.assertTrue(isinstance(flag, str))

class Test_X86Levels(unittest.TestCase):
    """
    Map from CPU Name to expected maximum feature set
    """
    LEVELMAP = {
        'AMD_Athlon_X2_4000+':             'x86-64',
        'AMD_Athlon_5370':                 'x86-64-v2',
        'AMD_FX8120':                      'x86-64-v2',
        'AMD_Opteron_6174':                'x86-64',
        'AMD_EPYC_7351':                   'x86-64-v3',
        'AMD_EPYC_7401':                   'x86-64-v3',
        'AMD_EPYC_7352':                   'x86-64-v3',
        'AMD_EPYC_7452':                   'x86-64-v3',
        'Intel_Core_i5-4300U':             'x86-64-v3',
        'Intel_Core_i7-4790':              'x86-64-v3',
        'Intel_Core_i5-5200U':             'x86-64-v3',
        'Intel_Core_i3-6100':              'x86-64-v3',
        'Intel_Core_i7-6700T':             'x86-64-v3',
        'Intel_Core_i3-7100':              'x86-64-v3',
        'Intel_Core_i3-8100':              'x86-64-v3',
        'Intel_Xeon_L5420':                'x86-64',
        'Intel_Xeon_L5520':                'x86-64-v2',
        'Intel_Xeon_X5550':                'x86-64-v2',
        'Intel_Xeon_L5640':                'x86-64-v2',
        'Intel_Xeon_X5650':                'x86-64-v2',
        'Intel_Xeon_E5-2650':              'x86-64-v2',
        'Intel_Xeon_E5-2670v2':            'x86-64-v2',
        'Intel_Xeon_E3-1220v3':            'x86-64-v3',
        'Intel_Xeon_E5-2623v3':            'x86-64-v3',
        'Intel_Xeon_E5-2650v3':            'x86-64-v3',
        'Intel_Xeon_E5-2630v4':            'x86-64-v3',
        'Intel_Xeon_E5-2680v4':            'x86-64-v3',
        'Intel_Xeon_Scalable_4114_Silver': 'x86-64-v4',
        'Intel_Xeon_Scalable_6130_Gold':   'x86-64-v4',
    }

    def test_x86_levels(self):
        for cpu_name, expected_feature_set in self.LEVELMAP.items():
            with self.subTest(
                    cpu_name = cpu_name,
                    expected_feature_set = expected_feature_set):

                cpuinfo = get_resource(cpu_name)
                self.assertTrue(isinstance(cpuinfo, str))

                flags = x86_feature_check.extract_cpu_flags(cpuinfo)
                self.assertTrue(isinstance(flags, set))

                feature_set = x86_feature_check.get_max_feature_set(flags)
                self.assertTrue(isinstance(feature_set, str))

                self.assertEqual(
                    expected_feature_set,
                    feature_set,
                    msg = 'Expected max feature level of CPU "{}" to be "{}"'.format(
                        cpu_name,
                        expected_feature_set))

if __name__ == '__main__':
    # cd to directory of this python file
    os.chdir(os.path.dirname(__file__))

    test_loader = unittest.defaultTestLoader
    test_runner = unittest.TextTestRunner(buffer = True)
    test_suite = test_loader.discover('.')
    test_runner.run(test_suite)
