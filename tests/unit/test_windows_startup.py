#!/usr/bin/env python3
"""Unit tests for WindowsStartupManager (mocked winreg — no real registry access)."""

import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.windows_startup import WindowsStartupManager


class TestWindowsStartupManager(unittest.TestCase):

    @patch('core.windows_startup.winreg')
    def test_enable_writes_correct_registry_key(self, mock_winreg):
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value.__enter__ = MagicMock(return_value=mock_key)
        mock_winreg.OpenKey.return_value.__exit__ = MagicMock(return_value=False)
        mock_winreg.HKEY_CURRENT_USER = 0x80000001
        mock_winreg.KEY_SET_VALUE = 0x0002

        mgr = WindowsStartupManager()
        mgr.enable(r"C:\Program Files\Whiz\whiz.exe")

        mock_winreg.OpenKey.assert_called_once_with(
            mock_winreg.HKEY_CURRENT_USER,
            WindowsStartupManager.RUN_KEY,
            0,
            mock_winreg.KEY_SET_VALUE,
        )
        mock_winreg.SetValueEx.assert_called_once_with(
            mock_key,
            WindowsStartupManager.APP_NAME,
            0,
            mock_winreg.REG_SZ,
            r'C:\Program Files\Whiz\whiz.exe --tray',
        )

    @patch('core.windows_startup.winreg')
    def test_disable_removes_key(self, mock_winreg):
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value.__enter__ = MagicMock(return_value=mock_key)
        mock_winreg.OpenKey.return_value.__exit__ = MagicMock(return_value=False)
        mock_winreg.HKEY_CURRENT_USER = 0x80000001
        mock_winreg.KEY_SET_VALUE = 0x0002

        mgr = WindowsStartupManager()
        mgr.disable()

        mock_winreg.DeleteValue.assert_called_once_with(mock_key, WindowsStartupManager.APP_NAME)

    @patch('core.windows_startup.winreg')
    def test_disable_does_not_raise_if_key_missing(self, mock_winreg):
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value.__enter__ = MagicMock(return_value=mock_key)
        mock_winreg.OpenKey.return_value.__exit__ = MagicMock(return_value=False)
        mock_winreg.HKEY_CURRENT_USER = 0x80000001
        mock_winreg.KEY_SET_VALUE = 0x0002
        mock_winreg.DeleteValue.side_effect = FileNotFoundError

        mgr = WindowsStartupManager()
        try:
            mgr.disable()
        except Exception as e:
            self.fail(f"disable() raised unexpectedly: {e}")

    @patch('core.windows_startup.winreg')
    def test_is_enabled_returns_true_when_key_exists(self, mock_winreg):
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value.__enter__ = MagicMock(return_value=mock_key)
        mock_winreg.OpenKey.return_value.__exit__ = MagicMock(return_value=False)
        mock_winreg.HKEY_CURRENT_USER = 0x80000001
        mock_winreg.KEY_READ = 0x20019
        mock_winreg.QueryValueEx.return_value = (r"C:\Whiz\whiz.exe --tray", 1)

        mgr = WindowsStartupManager()
        self.assertTrue(mgr.is_enabled())

    @patch('core.windows_startup.winreg')
    def test_is_enabled_returns_false_when_key_missing(self, mock_winreg):
        mock_winreg.OpenKey.side_effect = FileNotFoundError
        mock_winreg.HKEY_CURRENT_USER = 0x80000001
        mock_winreg.KEY_READ = 0x20019

        mgr = WindowsStartupManager()
        self.assertFalse(mgr.is_enabled())


if __name__ == '__main__':
    unittest.main()
