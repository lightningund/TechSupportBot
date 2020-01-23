"""Module for plugin functions.
"""

import glob
import logging
import os
from os.path import basename, dirname, isfile, join

from discord.ext import commands


class PluginLoader:
    """Wrapper for plugin loading.

    parameters:
        bot (BasementBot): the bot object to which plugins are loading
    """

    def __init__(self, bot):
        self.bot = bot

    def load_plugins(self):
        """Adds functions as commands from the plugins directory.
        """
        for plugin in self._get_modules():
            logging.info(f"Loading plugin module {plugin}")

            try:
                self.bot.load_extension(plugin)

            except Exception as e:
                logging.exception(f"Failed to load {plugin}: {str(e)}")

    @staticmethod
    def _get_modules():
        """Gets the list of plugin modules.
        """
        files = glob.glob(f"{join(dirname(__file__))}/plugins/*.py")
        return [
            f"plugins.{basename(f)[:-3]}"
            for f in files
            if isfile(f) and not f.endswith("__init__.py")
        ]
