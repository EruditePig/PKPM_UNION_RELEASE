# coding=utf-8 

from global_var import *
from global_setting import *
import dbwrapper


class index:
    def GET(self):
        return g_render.show_version_hierachy()
        #return g_render.upload_new_config()
        
if __name__ == "__main__":
    ii = index()
    ii.GET()