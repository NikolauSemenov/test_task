from yaml import load, Loader


def read_config():
    return load(open('config.yml', 'r'), Loader=Loader)
