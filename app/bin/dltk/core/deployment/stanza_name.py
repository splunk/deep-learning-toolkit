

def format(algorithm_name, environment_name):
    return "%s:%s" % (algorithm_name, environment_name)


def parse(stanza_name):
    i = stanza_name.find(":")
    return stanza_name[:i], stanza_name[i + 1:]
