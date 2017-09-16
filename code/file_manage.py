# coding=utf-8 

from global_var import *
from global_setting import *
import os
import shutil

class file_manage(object):
    """
    基于FILEHASH的前两位做文件管理（硬盘）
    """
    def arrange_file_from_temp_path(self, files):
        """
        将文件列表(files)中的文件从临时目录整理到保存目录
        [IN]
        files - {FILEPATH : {FILEHASH, FILENAME}}
        """
        if not os.path.exists(save_file_path):
            os.makedirs(save_file_path)

        file_success = []       # 操作成功的文件
        for filepath in files:
            from_path = os.path.abspath(os.path.join(temp_path, files[filepath][FILENAME]))
            if not os.path.exists(from_path):
                continue
            else:
                save_file_folder = os.path.abspath(os.path.join(save_file_path, files[filepath][FILEHASH][0:2]))
                if not os.path.exists(save_file_folder):
                    os.makedirs(save_file_folder)
                shutil.move(from_path, save_file_folder)
                file_success.append(file)
        return file_success

if __name__ == "__main__":
    pass