import urllib
import logging
import tornado.web
import jupyterlab_server
from notebook.services.contents.largefilemanager import LargeFileManager
import os
import sys
import json

sys.path.insert(0, os.getenv('DLTK_LIB_DIR'))


# parameters: #https://github.com/jupyter/notebook/blob/master/notebook/notebookapp.py

base_url_path = os.getenv("JUPYTER_BASE_URL_PATH", "/")


notebook_name = "Algo.ipynb"
notebook_version_name = "Algo.version"
notebook_dir = os.getenv('NOTEBOOK_PATH', "/notebooks")
notebook_file_path = os.path.join(notebook_dir, notebook_name)
notebook_version_file = os.path.join(notebook_dir, notebook_version_name)


class NotebookHandler(tornado.web.RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def get(self):
        try:
            with open(notebook_file_path, 'r') as f:
                source = f.read()
        except FileNotFoundError:
            source = None
        try:
            with open(notebook_version_file, 'r') as f:
                version = int(f.read())
        except FileNotFoundError:
            version = -1
        if source is None:
            logging.info("no algo source code found")
            self.set_status(404)
            return
        self.set_header('X-Notebook-Version', version)
        self.write(source)

    def put(self):
        version = self.request.headers['X-Notebook-Version']
        source = self.request.body.decode()
        logging.info("received new source code (version %s)" % version)
        try:
            json.loads(source)
        except Exception as e:
            logging.warning("error parsing source as json (%s): %s" % (e, source))
            self.set_status(400, reason="invalid source code json")
            return
        with open(notebook_file_path, "w") as f:
            f.write(source)
        with open(notebook_version_file, "w") as f:
            f.write(version)


class PingHandler(tornado.web.RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def get(self):
        self.set_status(200)


class DeploymentHandler(tornado.web.RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def get(self):
        if not os.path.exists(notebook_file_path):
            logging.info("cannot generate deployment code as source file doesn exists: %s" % notebook_file_path)
            self.set_status(404)
            return
        with open(notebook_file_path, 'r') as f:
            model_content = json.load(f)
        model = {
            "type": "notebook",
            "content": model_content,
        }
        try:
            deployment_code = generate_deployment_code(model)
        except Exception as e:
            logging.info("source model: %s" % model)
            logging.warning("error generating deployment code from model: %s" % e)
            self.set_status(500, reason="error generating deployment code: %s" % e)
            pass
        self.write(deployment_code)


def generate_deployment_code(model):
    # https://jupyter-notebook.readthedocs.io/en/stable/extending/savehooks.html
    if model['type'] != 'notebook':
        return
    # only run on nbformat v4
    if model['content']['nbformat'] != 4:
        return
    source = ""
    for cell in model['content']['cells']:
        if cell['cell_type'] != 'code':
            continue
        cell_source = cell['source']
        if isinstance(cell_source, str):
            source += cell_source + "\r\n"
        else:
            for cs in cell_source:
                source += cs + "\r\n"
    return source


class DaskFileManager(LargeFileManager):
    def save(self, model, path):
        absolute_path = os.path.join(notebook_dir, path.strip("/"))
        is_algo = absolute_path == notebook_file_path
        if is_algo:
            if os.path.exists(absolute_path):
                with open(notebook_file_path, 'r') as f:
                    old_algo_source = f.read()
            else:
                old_algo_source = ""
        result = super().save(model, path)
        if is_algo:
            with open(notebook_file_path, 'r') as f:
                new_algo_source = f.read()
            if new_algo_source != old_algo_source:
                try:
                    with open(notebook_version_file, 'r') as f:
                        version = int(f.read())
                except FileNotFoundError:
                    version = 0
                version += 1
                with open(notebook_version_file, "w") as f:
                    f.write("%s" % version)
                print("increased source code version number to %s" % version)
                generate_deployment_code(model)
        return result


class App(jupyterlab_server.LabServerApp):
    def start(self):
        self.web_app.add_handlers('.*$', [
            (r".*/_dltk/ping", PingHandler),
            (r".*/_dltk/notebook", NotebookHandler),
            (r".*/_dltk/algo_code", DeploymentHandler),
            (r".*/_dltk/algo_code\.py", DeploymentHandler),
        ])
        super().start()


if __name__ == "__main__":
    logging.basicConfig(
        level=os.environ.get("LOGLEVEL", "INFO"),
        format='%(asctime)s %(levelname)-8s %(message)s',
    )

    App.launch_instance(
        port=os.getenv('PORT', 8888),
        open_browser=False,
        root_dir=notebook_dir,
        allow_root=True,
        default_url=base_url_path + "notebooks/%s" % notebook_name,
        base_url=base_url_path,
        # debug=False,
        token="",
        # password=os.environ.get('HASHED_PWD'),
        ip="0.0.0.0",
        disable_check_xsrf=True,
        contents_manager_class=DaskFileManager
    )
