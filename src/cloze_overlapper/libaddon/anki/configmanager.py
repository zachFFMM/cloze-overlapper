# -*- coding: utf-8 -*-

# Libaddon for Anki
#
# Copyright (C) 2018-2019  Aristotelis P. <https//glutanimate.com/>
# Updated for modern Anki (2.1.45+)

"""
Add-on configuration management
"""

import os
import io
import json

from aqt import gui_hooks

from .._vendor.packaging import version

from ..utils import deepMergeDicts
from ..platform import PATH_ADDON, MODULE_ADDON

DEFAULT_LOCAL_CONFIG_PATH = os.path.join(PATH_ADDON, "config.json")
DEFAULT_LOCAL_META_PATH = os.path.join(PATH_ADDON, "meta.json")


class ConfigError(Exception):
    pass


class ConfigManager(object):
    """
    Generic add-on configuration manager for Anki

    Supports the following configuration storages:
    - local: json files in add-on directory (all profiles)
    - synced: json string in collection (synced across devices)
    - profile: pickle object in prefs.db (local to profile)
    """

    _supported_storages = ("local", "synced", "profile")

    def __init__(self, mw, config_dict={"local": None},
                 conf_key=MODULE_ADDON, conf_action=None,
                 reset_req=False, preload=False):
        self.mw = mw
        self._reset_req = reset_req
        self._conf_key = conf_key
        self._storages = {
            name: {
                "default": (default if name != "local"
                            else self._getLocalDefaults()),
                "dirty": False,
                "loaded": False
            }
            for name, default in config_dict.items()
        }

        self.conf_action = self.conf_updated_action = None
        self._setupAnkiHooks(conf_action=conf_action)
        self._setupCustomHooks()

        self._config = {}

        if preload:
            self._maybeLoad()

    # Dictionary interface

    def __getitem__(self, name):
        self._checkStorage(name)
        try:
            config = self._config[name]
        except KeyError:
            self.load(storage_name=name)
            config = self._config[name]
        return config

    def __setitem__(self, name, value):
        self._checkStorage(name)
        self._config[name] = value
        self._storages[name]["dirty"] = True

    def __str__(self):
        return self._config.__str__()

    # Regular interface

    def load(self, storage_name=None):
        for name in ([storage_name] if storage_name else self._storages):
            self._checkStorage(name)
            getter = getattr(self, "_get" + name.capitalize())
            self._config[name] = getter()
            self._storages[name]["loaded"] = True

    def save(self, storage_name=None, profile_unload=False, reset=False):
        if storage_name:
            storages = [storage_name]
        else:
            storages = self._storages

        for name in storages:
            self._checkStorage(name)
            saver = getattr(self, "_save" + name.capitalize())
            saver(self._config[name])
            self._storages[name]["dirty"] = False

        self.afterSave(reset=reset, profile_unload=profile_unload)

    def afterSave(self, reset=False, profile_unload=False):
        if (self._reset_req or reset) and not profile_unload:
            self.mw.reset()

    @property
    def all(self):
        for storage in self._storages.values():
            if not storage["loaded"]:
                self.load()
                break
        return self._config

    @all.setter
    def all(self, config_dict):
        self._config = config_dict
        self._storages = {
            name: {"default": {}, "dirty": False, "loaded": False}
            for name in config_dict
        }

    @property
    def defaults(self):
        return {name: storage_dict["default"]
                for name, storage_dict in self._storages.items()}

    @defaults.setter
    def defaults(self, config_dict):
        for name in config_dict:
            self._storages[name]["default"] = config_dict[name]

    def restoreDefaults(self):
        for name in self._storages:
            self._config[name] = self._storages[name]["default"]
        self.save()

    def onProfileUnload(self):
        for name, storage_dict in self._storages.items():
            if not storage_dict["dirty"]:
                continue
            try:
                self.save(name, profile_unload=True)
            except FileNotFoundError as e:
                if name == "local":
                    print(e)
                else:
                    raise

    def setConfigAction(self, action):
        self.conf_action = action
        self.mw.addonManager.setConfigAction(
            MODULE_ADDON, action)

    def setConfigUpdatedAction(self, action):
        self.conf_updated_action = action
        self.mw.addonManager.setConfigUpdatedAction(
            MODULE_ADDON, action)

    # General helper methods

    def _maybeLoad(self):
        if (any(i in self._storages for i in ("synced", "profile")) and
                self.mw.col is None):
            gui_hooks.profile_did_open.append(self.load)
            return
        self.load()

    def _checkStorage(self, name):
        if name not in self._supported_storages:
            raise NotImplementedError(
                "Config storage type not implemented in libaddon: ", name)
        elif name not in self._storages:
            raise ConfigError(
                "Config storage type not available for this add-on: ", name)

    def _setupCustomHooks(self):
        gui_hooks.profile_will_close.append(
            lambda: self.onProfileUnload())

    def _setupAnkiHooks(self, conf_action):
        if "local" in self._storages:
            self.setConfigUpdatedAction(self.onLocalConfigUpdated)
        self.setConfigAction(conf_action)

    # Local storage

    def _getLocal(self):
        return self.mw.addonManager.getConfig(MODULE_ADDON)

    def _getLocalDefaults(self):
        return self.mw.addonManager.addonConfigDefaults(MODULE_ADDON)

    def _saveLocal(self, config):
        self.mw.addonManager.writeConfig(MODULE_ADDON, config)

    def onLocalConfigUpdated(self, new_config):
        self._config["local"] = new_config
        self.afterSave()

    # Synced storage

    def _getSynced(self):
        return self._getStorageObj("synced")[self._conf_key]

    def _saveSynced(self, config):
        self._getStorageObj("synced")[self._conf_key] = config
        self.mw.col.setMod()

    # Profile storage

    def _getProfile(self):
        return self._getStorageObj("profile")[self._conf_key]

    def _saveProfile(self, config):
        self._getStorageObj("profile")[self._conf_key] = config
        self.mw.col.setMod()

    # Helper methods for synced & profile storage

    def _getStorageObj(self, name):
        conf_key = self._conf_key
        try:
            if name == "synced":
                storage_obj = self.mw.col.conf
            elif name == "profile":
                storage_obj = self.mw.pm.profile
            else:
                raise NotImplementedError(
                    "Storage object not implemented: ", name)
        except AttributeError:
            raise ConfigError("Config object is not ready, yet: ", name)

        default_dict = self._storages[name]["default"]

        if conf_key not in storage_obj:
            storage_obj[conf_key] = default_dict

        storage_dict = storage_obj[conf_key]
        dict_version = str(storage_dict.get("version", "0.0.0"))
        default_version = str(default_dict["version"])

        if (version.parse(dict_version) < version.parse(default_version)):
            storage_obj[conf_key] = deepMergeDicts(
                default_dict, storage_dict, new=True)
            storage_obj[conf_key]["version"] = default_version
            self.mw.col.setMod()

        return storage_obj
