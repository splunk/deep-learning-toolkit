import importlib


__all__ = [
    "get_class",
    "get_method",
    "is_truthy",
    "get_label_for_name"
]


def is_truthy(s):
    return str(s).lower() in ['1', 't', 'true', 'y', 'yes', 'enable', 'enabled']


def get_class(name):
    i = name.rfind(".")
    module_name, cls_name = name[:i], name[i + 1:]
    module = importlib.import_module(module_name)
    Class = getattr(module, cls_name)
    return Class


def get_method(name):
    i = name.rfind(".")
    module_name, cls_name = name[:i], name[i + 1:]
    module = importlib.import_module(module_name)
    Func = getattr(module, cls_name)
    return Func


def get_label_for_name(name):
    label = name.replace("_", " ")
    label = label.title()
    return label
