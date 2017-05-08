import os


# translate a filename relative to this resource folder
def filename(file):
    return os.path.join(os.path.dirname(__file__), file)


# get all files in a directory
def directory_content(folder):
    filename_list = []
    for file in os.scandir(os.path.join(os.path.dirname(__file__), folder)):
        filename_list.append(file.path)
    return filename_list

