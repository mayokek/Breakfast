import os
import configparser
import shutil

from util.logger import log

class Defaults:
    token = None
    owner_id = None
    prefix = "b$"

class Config:
    def __init__(self):

        if not os.path.isfile("config/config.ini"):
            if not os.path.isfile("config/config.ini.example"):
                log.critical("There is no \"config.ini.example\" file in the \"config\" folder! Please go to the github repo and download it and then put it in the \"config\" folder!")
                os._exit(1)
            else:
                shutil.copy("config/config.ini.example", "config/config.ini")
                log.warning("Created the \"config.ini\" file in the config folder! Please edit the config and then run the bot again!")
                os._exit(1)

        self.config_file = "config/config.ini"

        config = configparser.ConfigParser(interpolation=None)
        config.read(self.config_file, encoding="utf-8")

        sections = {"Credentials", "Bot"}.difference(config.sections())
        if sections:
            log.critical("Could not load a section in the config file, please obtain a new config file from the github repo if regenerating the config doesn't work!")
            os._exit(1)
        self._token = config.get("Credentials", "Token", fallback=Defaults.token)
        self.owner_id = config.get("Bot", "Owner_ID", fallback=Defaults.owner_id)
        self.command_prefix = config.get("Bot", "Command_Prefix", fallback=Defaults.prefix)

        self.check()

    def check(self):
        if not self._token:
            log.critical("No token was specified in the config, please put your bot's token in the config.")
            os._exit(1)

        if not self.owner_id:
            log.critical("No owner ID was specified in the config, please put your ID for the owner ID in the config")
            os._exit(1)
