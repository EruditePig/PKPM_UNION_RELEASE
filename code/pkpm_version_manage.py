# coding=utf-8 

import dbwrapper

class pkpm_version_manage(object):

    def __init__(self):
        self.db = DBWrapper()

    def get_version_list(self):
        """
        获取版本列表，就是版本树
        [OUT]
        version_tree - {ver_id, [child_ver_id]}
        """
        return self.db.get_version_list()

    def get_next_version_config(self, parameter_list):
        """
        基于父版本，获得新版本的配置文件
        """
        pass

    def filter_upload_file(self, parameter_list):
        """
        根据用户账户、配置文件，过滤上传文件，只保留有效的，并验证本次上传是否有效，
        比如新增的文件是否上传
        """
        pass

    def calc_change(self, parameter_list):
        """
        根据过滤后的文件列表，计算新版本的变动
        """
        pass

    def save_change(self, parameter_list):
        """
        保存新版本的变动到数据库
        """
        pass

if __name__ == "__main__":
    pass