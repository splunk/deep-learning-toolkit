import os
from . import dltk_api


def exists(name):
    connectors = dltk_api.call("GET", "connectors")
    filtered = list(filter(lambda c: c["name"] == name, connectors))
    return len(filtered)


def create(name, delete_if_already_exists=False):
    if delete_if_already_exists:
        if exists(name):
            delete(name, skip_if_not_exists=True)
    dltk_api.call("POST", "connectors", {
        "name": name,
    }, return_entries=False)


def delete(name, skip_if_not_exists=False):
    if skip_if_not_exists:
        if not exists(name):
            return
    dltk_api.call("DELETE", "connectors", {
        "name": name,
    }, return_entries=False)
