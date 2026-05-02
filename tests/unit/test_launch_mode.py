#!/usr/bin/env python3
"""Unit tests for launch mode detection (--tray flag)."""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.launch_mode import is_tray_launch


class TestIsTrayLaunch(unittest.TestCase):

    def test_tray_flag_detected(self):
        self.assertTrue(is_tray_launch(["whiz.exe", "--tray"]))

    def test_no_flag_returns_false(self):
        self.assertFalse(is_tray_launch(["whiz.exe"]))

    def test_empty_argv_returns_false(self):
        self.assertFalse(is_tray_launch([]))

    def test_other_flags_do_not_trigger_tray(self):
        self.assertFalse(is_tray_launch(["whiz.exe", "--debug"]))

    def test_tray_flag_among_others(self):
        self.assertTrue(is_tray_launch(["whiz.exe", "--debug", "--tray"]))


if __name__ == '__main__':
    unittest.main()
