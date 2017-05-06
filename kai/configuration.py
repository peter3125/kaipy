import configparser


# turn a config map into a dictionary
def get_section_dict(filename, section):

    config = configparser.ConfigParser()
    config.read(filename)

    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
        except:
            dict1[option] = None
    return dict1
