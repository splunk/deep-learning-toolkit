

def is_method(name):
    i = name.find(":")
    return i >= 0


def format(algorithm_name, method_name):
    return "%s:%s" % (algorithm_name, method_name)


def parse(name):
    i = name.find(":")
    return name[:i], name[i + 1:]


def parse_algorithm_name(name):
    algorithm_name, _ = parse(name)
    return algorithm_name


def parse_method_name(name):
    _, method_name = parse(name)
    return method_name
