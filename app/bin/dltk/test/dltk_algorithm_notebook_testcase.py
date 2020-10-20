from . import dltk_algorithm
import inspect
import json
import sys
import copy


def notebook_method(f, metadata={}):
    f.is_notebook_method = True
    f.notebook_cell_metadata = metadata
    return f


class NotebookAlgorithmTestCase(dltk_algorithm.AlgorithmTestCase):

    @classmethod
    def trim(cls, docstring):
        if not docstring:
            return ''
        # Convert tabs to spaces (following the normal Python rules)
        # and split into a list of lines:
        lines = docstring.expandtabs().splitlines()
        # Determine minimum indentation (first line doesn't count):
        indent = 10000
        for line in lines[1:]:
            stripped = line.lstrip()
            if stripped:
                indent = min(indent, len(line) - len(stripped))
        # Remove indentation (first line is special):
        trimmed = [lines[0].strip()]
        if indent < 10000:
            for line in lines[1:]:
                trimmed.append(line[indent:].rstrip())
        # Strip off trailing and leading blank lines:
        while trimmed and not trimmed[-1]:
            trimmed.pop()
        while trimmed and not trimmed[0]:
            trimmed.pop(0)
        # Return a single string:
        return '\n'.join(trimmed)

    @classmethod
    def get_default_cell_metadata(cls):
        return {}

    @classmethod
    def get_source_code(cls):

        cells = []

        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if hasattr(attr, "is_notebook_method"):
                default_cell_metadata = cls.get_default_cell_metadata()
                method_cell_metadata = copy.deepcopy(getattr(attr, "notebook_cell_metadata"))
                method_cell_metadata.update(default_cell_metadata)
                source = inspect.getsource(attr)
                source = cls.trim(source)
                lines = []
                for line in source.split("\n"):
                    if line.find("@dltk_algorithm_notebook_testcase.notebook_method") >= 0:
                        continue
                    if line.find("@notebook_method") >= 0:
                        continue
                    lines.append(line+"\n")
                cells.append({
                    "cell_type": "code",
                    "execution_count": 0,
                    "metadata": method_cell_metadata,
                    "outputs": [],
                    "source": lines
                })

        source_code = {
            "cells": cells,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "codemirror_mode": {
                        "name": "ipython",
                        "version": 3
                    },
                    "file_extension": ".py",
                    "mimetype": "text/x-python",
                    "name": "python",
                    "nbconvert_exporter": "python",
                    "pygments_lexer": "ipython3",
                    "version": "3.7.3"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 1
        }

        #raise Exception(source_code)
        return json.dumps(source_code)

    @classmethod
    def get_algorithm_methods(cls):
        methods = {}
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if hasattr(attr, "is_notebook_method"):
                methods[attr_name] = {}
        return methods
