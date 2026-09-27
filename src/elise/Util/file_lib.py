import glob
import os


#   in  dir_path: path of directory
#       ext     : extension to search
#   out [files] : list of file's full path
def files_in_dir(dir_path, ext):
    if not os.path.isdir(dir_path):
        return None
    files = [file for file in glob.glob(os.path.join(dir_path, '*.' + ext))]
    return files


#   in  dir_path: path of directory
#       ext     : extension to search
#   out [files] : list of file's full path or dir_path if it is file with ext
def files_in_dir_or_file(dir_path, ext):
    files = files_in_dir(dir_path, ext)
    if len(files) == 0:
        _, files_ext = os.path.splitext(dir_path)
        if files_ext[1:] == ext:
            files.append(dir_path)
    return files


#   in  dir_path: path of directory to make dirName.ext filename
#       ext     : extension to create file
#   out         : filename from directory name and extension
def create_dir_name_ext_file(dir_path, ext):
    if os.path.isfile(dir_path):
        dir_path = os.path.basename(dir_path)
    dir_name = os.path.basename(dir_path)
    file_name = dir_name + '.' + ext
    return os.path.join(dir_path, file_name)


#   in  files   : full path list to change extension
#       ext     : extension to change
#       dir_in      : directory name to add below file's directory
#       zipped  : whether output contain original or not. default is False
#   out [files] : list of file's full path
def change_files_ext_to(files, new_ext, dir_in=None, zipped=False):
    ext_files = []
    for file in files:
        changed_file = change_file_ext(file, new_ext, dir_in)
        if zipped:
            ext_files.append((file, changed_file))
        else:
            ext_files.append(changed_file)
    return ext_files


#   in  in_file     : filename to change extension
#       new_ext     : change to this extension
#       dir_in      : directory name to add below file's directory
#   out out_file    : extension changed (and insert directory) file name
def change_file_ext(in_file, new_ext, dir_in=None):
    if os.path.isdir(in_file):
        return None
    file_dir = os.path.dirname(in_file)
    file_body, ext = os.path.splitext(os.path.basename(in_file))
    if dir_in is None:
        parsed_file = os.path.join(file_dir, file_body + '.' + new_ext)
    else:
        parsed_file = os.path.join(file_dir, dir_in, file_body + '.' + new_ext)
    return parsed_file
