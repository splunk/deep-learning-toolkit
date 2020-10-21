import sys
sys.path.insert(0,'/dltk/.jupyter')

def post_save(model, os_path, contents_manager):
    import jupyter_notebook_conversion
    jupyter_notebook_conversion.convert(model, os_path)


c.FileContentsManager.post_save_hook = post_save

# TODO change PW to your own secret
# generate your own PW in python:
# from notebook.auth import passwd
# passwd()
c.NotebookApp.password = 'sha1:f7432152c71d:e8520c26b9d960e838d562768c1d24ef5b9b76c7'
# "Splunk4DeepLearning"
