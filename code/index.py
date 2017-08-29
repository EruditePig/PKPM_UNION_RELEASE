# coding=utf-8 

from global_var import *
from global_setting import *

def version_table_is_empty():
    return True

def config_table_is_empty():
    return True

class index:
    def GET(self):
        if version_table_is_empty():
            if config_table_is_empty():
                return render.empty(url)
        return render.index()