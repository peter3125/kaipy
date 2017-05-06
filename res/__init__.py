import os


# translate a filename relative to this resource folder
def filename(file):
    return os.path.join(os.path.dirname(__file__), file)


# get all files in a directory
def directory_content(folder):
    return os.scandir(os.path.join(os.path.dirname(__file__), folder))
