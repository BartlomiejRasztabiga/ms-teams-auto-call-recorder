import json
from msrecorder.app.config.config import Config


class ConfigService:
    instance = None

    @staticmethod
    def get_instance():
        if ConfigService.instance is None:
            ConfigService.instance = ConfigService()

        return ConfigService.instance

    def __init__(self):
        self.config = None
        self.__load_config()

    def __load_config(self):
        with open('config.json') as json_data_file:
            self.config = Config(json.load(json_data_file))
