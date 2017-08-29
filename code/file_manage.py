# coding=utf-8 


class file_manage(object):
    """
    基于(hash,filesize)做文件管理（硬盘）
    """
    SAVE_FOLDER_NAME = "index"      # 文件存储目录（相对工作目录）
    
    def get_file_path(self,filename, hashvalue, filesize):
        """
        [in]
        filename - 文件名
        hashvalue - hash值
        filesize - 文件大小（字节）
        [out]
        filepath - 文件相对工作目录的路径
        """