import json
import os


class Config:

    def __init__(self):
        with open('config.json', 'r') as f:
            self.values: dict = json.load(f)

    def get(self, path: str):
        keys = path.split('.')

        value = self.values
        for key in keys:
            value = value[key]

        if isinstance(value, str) and value[0] == '$':
            value = os.getenv(value[1:])

        return value
