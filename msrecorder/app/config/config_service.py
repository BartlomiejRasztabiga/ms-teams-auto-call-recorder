import json


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
            self.config = json.load(json_data_file)
