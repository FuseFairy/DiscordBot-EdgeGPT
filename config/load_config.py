import yaml

with open('./config.yml', encoding='utf-8') as file:
    config = yaml.safe_load(file)