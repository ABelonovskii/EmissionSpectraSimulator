import yaml


class ConfigManager:
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self.config_data = {}

    def load_config(self):
        try:
            with open(self.config_path, 'r') as file:
                self.config_data = yaml.safe_load(file)
        except FileNotFoundError:
            self.config_data = {}

    def save_config(self):
        with open(self.config_path, 'w') as file:
            yaml.dump(self.config_data, file, default_flow_style=False)

    def get_value(self, path, default=None):
        keys = path.split('/')
        value = self.config_data
        try:
            for key in keys:
                value = value[key]
            return value
        except KeyError:
            return default

    def set_value(self, path, value):
        keys = path.split('/')
        data = self.config_data
        for key in keys[:-1]:
            if key not in data:
                data[key] = {}
            data = data[key]
        data[keys[-1]] = value
