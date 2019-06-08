# -*- coding: utf-8 -*-

import os.path
import json


class SettingsStore:
    """
    Key value settings storage. Basically a wrapper around dict 
    featuring JSON persistence, (re)loading from file and restoring to defaults.
    """
    def __init__(self, file_path='', defaults={}):
        self._file_path = file_path
        self._defaults = defaults
        self._settings = {}

        if os.path.exists(self._file_path):
            self.reload()
        else:
            self.restore_defaults()
            self.persist()

    def reload(self):
        """Reload settings"""
        self.restore_defaults()
        with open(self._file_path, 'rt') as settings_file:
            self._settings.update(json.load(settings_file))

    def persist(self):
        """Persist settings"""
        with open(self._file_path, 'wt') as settings_file:
            json.dump(self._settings, settings_file)

    def restore_defaults(self):
        """Resture settings to default"""

        if not self._defaults:
            return

        self._settings = dict(self._defaults)

    def __getitem__(self, key):
        """Get item"""
        return self._settings[key]

    def __setitem__(self, key, val):
        """Set item"""
        self._settings[key] = val
