import configparser

def readConfig(filename):
    cfg = {}		# dictionary of configuration values, available to all functions

    parser = configparser.ConfigParser()
    parser.read(filename)
    defaults = parser.defaults()

    for key in defaults:
        cfg[key] = to_number(defaults[key])
    return cfg



def to_number(s):
    """
    Casts s to a float if possible, otherwise returns s
    """
    try:
        n = float(s)
        return n
    except ValueError:
        return s


# print(readConfig('cafstar.cfg'))