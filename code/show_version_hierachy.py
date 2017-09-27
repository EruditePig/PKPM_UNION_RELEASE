# coding=utf-8 

from global_var import *
from global_setting import *
import dbwrapper
import urlparse
import sys
import json

class show_version_hierachy:

    def GET(self):
        pass

    def POST(self):
        data = web.data()
        print web.input()
        parsed_data = urlparse.parse_qs(data)
        if parsed_data:
            request_type = parsed_data.get('action')[0]
            if request_type == 'request_version_hierachy':
                db = dbwrapper.DBWrapper(dbpath)
                version_hierachy = db.get_version_hierachy()
                return json.dumps({"state" : "success", "version_hierachy" : version_hierachy})
        else:
            print data

if __name__=="__main__":
    pass