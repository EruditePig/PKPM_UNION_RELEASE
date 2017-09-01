# coding=utf-8 

from global_var import *
from global_setting import *
import dbwrapper


class index:
    def GET(self):
        return g_render.upload_new_version()
        db = dbwrapper.DBWrapper(dbpath)
        if db.is_table_empty(dbwrapper.DBWrapper.VERSION_LIST):
            if db.is_table_empty(dbwrapper.DBWrapper.CONFIG_CREATE_LOG):
                return g_render.empty()
            else:   # 有配置文件，但无版本，则上传第一个版本
                return g_render.upload_first_version()
        return g_render.index()

if __name__ == "__main__":
    ii = index()
    ii.GET()