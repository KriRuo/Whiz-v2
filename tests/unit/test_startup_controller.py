#!/usr/bin/env python3
"""Unit tests for StartupController — wires run_at_startup setting to WindowsStartupManager."""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.startup_controller import StartupController


class TestStartupController(unittest.TestCase):

    def _make(self, enabled: bool = False, exe: str = r"C:\Whiz\whiz.exe"):
        mgr = MagicMock()  # WindowsStartupManager mock
        ctrl = StartupController(startup_manager=mgr, exe_path=exe)
        return ctrl, mgr

    def test_apply_true_calls_enable_with_exe_path(self):
        ctrl, mgr = self._make(exe=r"C:\Whiz\whiz.exe")
        ctrl.apply(enabled=True)
        mgr.enable.assert_called_once_with(r"C:\Whiz\whiz.exe")
        mgr.disable.assert_not_called()

    def test_apply_false_calls_disable(self):
        ctrl, mgr = self._make()
        ctrl.apply(enabled=False)
        mgr.disable.assert_called_once()
        mgr.enable.assert_not_called()

    def test_current_state_delegates_to_manager(self):
        ctrl, mgr = self._make()
        mgr.is_enabled.return_value = True
        self.assertTrue(ctrl.current_state())

        mgr.is_enabled.return_value = False
        self.assertFalse(ctrl.current_state())


if __name__ == '__main__':
    unittest.main()
