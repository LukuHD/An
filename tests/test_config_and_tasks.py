"""Tests for ConfigManager and TaskManager logic."""
import json
import os
import sys
import tempfile
import unittest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.config_manager import ConfigManager, DEFAULT_THEME, THEME_FILE
from modules.schedule_tool import TaskManager, TASKS_FILE


class TestConfigManager(unittest.TestCase):
    """Tests for theme configuration management."""

    def setUp(self):
        """Backup existing theme file if present."""
        self.backup = None
        if os.path.exists(THEME_FILE):
            with open(THEME_FILE, 'r') as f:
                self.backup = f.read()

    def tearDown(self):
        """Restore original theme file."""
        if self.backup is not None:
            with open(THEME_FILE, 'w') as f:
                f.write(self.backup)
        elif os.path.exists(THEME_FILE):
            os.remove(THEME_FILE)

    def test_load_default_theme_when_no_file(self):
        """Should return default theme when theme.json doesn't exist."""
        if os.path.exists(THEME_FILE):
            os.remove(THEME_FILE)
        theme = ConfigManager.load_theme()
        for key in DEFAULT_THEME:
            self.assertIn(key, theme)
            self.assertEqual(theme[key], DEFAULT_THEME[key])

    def test_default_theme_has_all_keys(self):
        """Default theme should have all expected keys."""
        expected_keys = ['accent', 'background', 'text', 'secondary',
                         'border', 'title_bar', 'card_text', 'highlight',
                         'use_background', 'background_image']
        for key in expected_keys:
            self.assertIn(key, DEFAULT_THEME, f"Missing key: {key}")

    def test_save_and_load_theme(self):
        """Theme should persist correctly through save/load."""
        custom = {
            "accent": "#ff0000",
            "background": "#000000",
            "text": "#ffffff",
            "secondary": "#111111",
            "border": "#222222",
            "title_bar": "#333333",
            "card_text": "#444444",
            "highlight": "#55ff55",
            "use_background": True,
            "background_image": "/path/to/image.png"
        }
        ConfigManager.save_theme(custom)
        loaded = ConfigManager.load_theme()
        for key, val in custom.items():
            self.assertEqual(loaded[key], val, f"Mismatch for key: {key}")

    def test_load_partial_theme_merges_defaults(self):
        """Loading a theme with missing keys should merge with defaults."""
        partial = {"accent": "#ff0000"}
        with open(THEME_FILE, 'w') as f:
            json.dump(partial, f)
        loaded = ConfigManager.load_theme()
        self.assertEqual(loaded['accent'], "#ff0000")
        self.assertEqual(loaded['background'], DEFAULT_THEME['background'])
        self.assertEqual(loaded['text'], DEFAULT_THEME['text'])
        self.assertIn('border', loaded)
        self.assertIn('use_background', loaded)

    def test_load_corrupted_file_returns_default(self):
        """Loading a corrupted JSON should return default theme."""
        with open(THEME_FILE, 'w') as f:
            f.write("{invalid json content")
        theme = ConfigManager.load_theme()
        self.assertEqual(theme['accent'], DEFAULT_THEME['accent'])


class TestTaskManager(unittest.TestCase):
    """Tests for task management."""

    def setUp(self):
        self.backup = None
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r') as f:
                self.backup = f.read()

    def tearDown(self):
        if self.backup is not None:
            with open(TASKS_FILE, 'w') as f:
                f.write(self.backup)
        elif os.path.exists(TASKS_FILE):
            os.remove(TASKS_FILE)

    def test_load_empty_tasks(self):
        """Should return empty list when no tasks file."""
        if os.path.exists(TASKS_FILE):
            os.remove(TASKS_FILE)
        tasks = TaskManager.load_tasks()
        self.assertEqual(tasks, [])

    def test_save_and_load_tasks(self):
        """Tasks should persist correctly."""
        tasks = [
            {"title": "Test", "category": "Work", "urgency": "ALTA", "deadline": "2026-03-01"}
        ]
        TaskManager.save_tasks(tasks)
        loaded = TaskManager.load_tasks()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]['title'], "Test")

    def test_smart_priority_no_tasks(self):
        """Should return None for empty task list."""
        result = TaskManager.get_smart_priority_color([])
        self.assertIsNone(result)

    def test_smart_priority_with_tasks(self):
        """Should return a color string for tasks with deadlines."""
        tasks = [
            {"title": "Future", "deadline": "2099-12-31"}
        ]
        result = TaskManager.get_smart_priority_color(tasks)
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("#"))

    def test_smart_priority_missing_deadline(self):
        """Should handle tasks without deadlines gracefully."""
        tasks = [
            {"title": "No date"},
            {"title": "Empty date", "deadline": ""},
            {"title": "None date", "deadline": None}
        ]
        result = TaskManager.get_smart_priority_color(tasks)
        self.assertIsNone(result)

    def test_sort_key_valid_deadline(self):
        """Sort key should return deadline string for valid dates."""
        task = {"title": "Test", "deadline": "2026-03-01"}
        self.assertEqual(TaskManager.sort_key(task), "2026-03-01")

    def test_sort_key_missing_deadline(self):
        """Sort key should return far future for missing deadlines."""
        task = {"title": "No date"}
        self.assertEqual(TaskManager.sort_key(task), "9999-12-31")

    def test_sort_key_empty_deadline(self):
        """Sort key should return far future for empty deadlines."""
        task = {"title": "Empty", "deadline": ""}
        self.assertEqual(TaskManager.sort_key(task), "9999-12-31")

    def test_sort_key_invalid_deadline(self):
        """Sort key should return far future for invalid dates."""
        task = {"title": "Bad", "deadline": "not-a-date"}
        self.assertEqual(TaskManager.sort_key(task), "9999-12-31")

    def test_sort_key_none_deadline(self):
        """Sort key should handle None deadline."""
        task = {"title": "None", "deadline": None}
        self.assertEqual(TaskManager.sort_key(task), "9999-12-31")

    def test_sorting_mixed_tasks(self):
        """Tasks with and without deadlines should sort correctly."""
        tasks = [
            {"title": "No date"},
            {"title": "Late", "deadline": "2026-12-01"},
            {"title": "Early", "deadline": "2026-01-01"},
            {"title": "Bad", "deadline": "invalid"},
        ]
        sorted_tasks = sorted(tasks, key=TaskManager.sort_key)
        self.assertEqual(sorted_tasks[0]['title'], "Early")
        self.assertEqual(sorted_tasks[1]['title'], "Late")
        # No date and invalid should be at the end
        self.assertIn(sorted_tasks[2]['title'], ["No date", "Bad"])
        self.assertIn(sorted_tasks[3]['title'], ["No date", "Bad"])


if __name__ == '__main__':
    unittest.main()
