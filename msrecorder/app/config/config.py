import json


class Config:
    instance = None

    @staticmethod
    def get_instance():
        if Config.instance is None:
            Config.instance = Config()

        return Config.instance

    def __init__(self):
        self.config = None
        self.__load_config()

    def __load_config(self):
        with open('config.json') as json_data_file:
            self.config = json.load(json_data_file)
