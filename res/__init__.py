import os


# translate a filename relative to this resource folder
def filename(file):
    return os.path.join(os.path.dirname(__file__), file)
