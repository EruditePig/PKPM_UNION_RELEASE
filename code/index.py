# coding=utf-8 

from global_var import *
from global_setting import *
import dbwrapper


class index:
    def GET(self):
        db = dbwrapper.DBWrapper(dbpath)
        return g_render.upload_first_version()

if __name__ == "__main__":
    ii = index()
    ii.GET()