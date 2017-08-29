# coding=utf-8 


class version_manage(object):
    
    ADD = "增加"
    DEL = "删除"
    MOD = "修改"

    def diff_version(self, parent_ver_file_list, file_list):
        """ 传入父版本文件列表（包括哈希值）和待比较的文件列表（包括哈希值），返回待比较文件列表的状态
            [in]
                parent_ver_file_list - map[path]=(hash,filesize)
                file_list - map[path]=(hash,filesize)
            [out]
                change - map[path]=change
        """
        change = map()

        for key in file_list:
            if key in parent_ver_file_list:
                if file_list[key][0] != parent_ver_file_list[key][0] or file_list[key][1] != parent_ver_file_list[key][1]:
                    # 不等则为更新
                    change[key] = version_manage.MOD
            else:
                # 文件为增加
                change[key] = version_manage.ADD

        for key in parent_ver_file_list:
            if key not in file_list:
                # 不存在则为删除
                change[key] = version_manage.DEL
        
        return change

    def diff_two_version(self, oldver, newver):
        """
            根据新旧两个版本号，生成更新文件列表（增、删、改）
        """
        pass


if __name__ == '__main__':

    vm = version_manage()

