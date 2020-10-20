import os
from subprocess import check_call


def convert(model, os_path):
    """post-save hook for converting notebooks to .py scripts"""
    if model['type'] != 'notebook':
        return  # only do this for notebooks
    # split in directory and file name
    nb_path, nb_filename = os.path.split(os_path)
    # split out filename
    nb_name = os.path.splitext(nb_filename)[0]
    # add .py extension for target python module
    py_name = nb_name + ".py"
    # defined modules path in /srv (hardcoded to prevent notebooks subfolder relative problems)
    py_path = "/srv/app/model/"
    # notebook config path in /srv (hardcoded to prevent notebooks subfolder relative problems)
    nb_template = "/dltk/.jupyter/jupyter_notebook_conversion.tpl"
    print("Config path: " + nb_template)
    print("Source path: " + os_path)
    print("Destination: " + py_path)
    # convert notebook to python module using the provided template
    # jupyter nbconvert --to python /srv/notebooks/Splunk_MLTK_notebook.ipynb --output-dir /src/models --template=/srv/config/jupyter_notebook_conversion.tpl
    check_call(['jupyter', 'nbconvert', '--to', 'python', nb_filename, '--output-dir', py_path, '--template=' + nb_template], cwd=nb_path)

    if nb_filename == "algo.ipynb":
        notebook_version_file = os_path + ".version"
        try:
            with open(notebook_version_file, 'r') as f:
                version = int(f.read())
        except FileNotFoundError:
            version = 0
        version += 1
        with open(notebook_version_file, "w") as f:
            f.write("%s" % version)

        python_version_file = os.path.join(py_path, py_name) + ".version"
        with open(python_version_file, "w") as f:
            f.write("%s" % version)

        python_path = os.path.join(py_path, py_name)
        with open(python_path, 'r') as f:
            python_code = f.read()
        return python_code

        #print("increased source code version number to %s" % version)
