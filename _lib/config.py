import yaml


def get_bot_config() -> dict:
    with open("config.yaml", mode="r") as f:
        config = yaml.safe_load(f)

    return config


def get_owners() -> list:
    return get_bot_config()['owners']