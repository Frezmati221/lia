import yaml

def read_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

def write_config(config):
    with open('config.yaml', 'w') as file:
        yaml.safe_dump(config, file) 