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
        pass

if __name__=="__main__":

    pass