# coding=utf-8 

from global_var import *
from global_setting import *
import dbwrapper
import urlparse
import sys
import json
import random

class upload_first_version:
    def GET(self):
        pass

    def POST(self):
        x = web.input()
        if 'input_files' in x:  # to check if the file-object is created
            filedir = r'd:/temp/2' # change this to the directory you want to store the file in.
            filepath=x.filepath.replace('\\','/') # replaces the windows-style slashes with linux ones.
            filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
            fout = open(filedir +'/'+ filename,'wb') # creates the file where the uploaded file should be stored
            fout.write(x.input_files) # writes the uploaded file to the newly created file.
            fout.close() # closes the file, upload complete.
        else:
            data = web.data()
            parsed_data = urlparse.parse_qs(data)
            request_type = parsed_data.get('action')[0]
            if request_type == 'request_config':
                try:
                    db = dbwrapper.DBWrapper(dbpath)
                    config_log = db.get_config_create_log_table()
                    first_config_name = config_log[0][dbwrapper.DBWrapper.CONFIG_CREATE_LOG_CONFIG_NAME]
                    config = db.get_config_table(first_config_name)
                    return json.dumps({"state" : "success", "config" : config})
                except:
                    return json.dumps({"state" : "fail", "info" : str(sys.exc_info()[0])})
            else:
                return json.dumps({"state" : "fail", "info" : "unknown request"})