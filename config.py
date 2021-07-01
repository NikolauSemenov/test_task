from yaml import load, Loader


def read_config(is_test: bool = False) -> dict:
    data = load(open('config.yml', 'r'), Loader=Loader)
    if is_test:
        data["app"]["namedb"] = f'{data["app"]["namedb"]}_test'
    return data
