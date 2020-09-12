import json


class Config:
    def __init__(self):
        self.config = None
        self.load_config()

    def load_config(self):
        with open('config.json') as json_data_file:
            self.config = json.load(json_data_file)
