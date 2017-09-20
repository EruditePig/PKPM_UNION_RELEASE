# coding=utf-8 

from global_var import *
from global_setting import *
import dbwrapper
import urlparse
import sys
import json
import random
import os
import hashlib
import file_manage

class upload_new_config:
    def GET(self):
        return g_render.upload_new_config()

    def POST(self):
        data = web.data()
        parsed_data = urlparse.parse_qs(data)
        request_type = parsed_data.get('action')[0]
        if request_type == 'request_config':
            parent_version_id = parsed_data.get('parent_version_id')[0]
            db = dbwrapper.DBWrapper(dbpath)
            config_info = db.get_version_config_info(parent_version_id)
            return json.dumps({"state" : "success", "config_info" : config_info})
        else:
            return json.dumps({"state" : "fail", "info" : "unknown request"})

if __name__=="__main__":

    pass