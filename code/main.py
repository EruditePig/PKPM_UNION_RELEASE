# coding=utf-8 
# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=C1001
# pylint: disable=W0232
# pylint: disable=R0903
import web

import global_setting
import global_var

# 具体分发类
from index import *
from save_first_config import *
from upload_first_version import *
from upload_new_version import * 
from upload_new_config import * 
from show_version_hierachy import *


urls = (
    '/','index',
    '/save_first_config','save_first_config',
    '/upload_first_version','upload_first_version',
    '/upload_new_version', 'upload_new_version',
    '/upload_new_config', 'upload_new_config',
    '/show_version_hierachy', 'show_version_hierachy',
)

class MyApplication(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

app = MyApplication(urls, globals())

if __name__=='__main__':
    # application = app.wsgifunc()
    # pywsgi.WSGIServer(("", 8080), application).serve_forever()
    app.run(port = 3744)