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

class upload_new_version:
    def GET(self):
        pass

    def POST(self):
        x = web.input()
        if 'input_files' in x:  # to check if the file-object is created
            filepath = x.filepath.replace('\\','/') # replaces the windows-style slashes with linux ones.
            filename = filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
            if not os.path.exists(temp_path):
                os.makedirs(temp_path)
            fout = open(temp_path +'/'+ filename,'wb') # creates the file where the uploaded file should be stored
            fout.write(x.input_files) # writes the uploaded file to the newly created file.
            fout.close() # closes the file, upload complete.
            md5 = hashlib.md5(x.input_files).hexdigest()
            size = len(x.input_files)
            g_new_version["files"].append({"filepath" : filepath, "filename" : filename, "hash": md5, "size" : size})
            return json.dumps({})
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
            elif request_type == 'upload_complete':
                print g_new_version
            else:
                return json.dumps({"state" : "fail", "info" : "unknown request"})

if __name__=="__main__":

    os.makedirs("d:/work2/PKPM_UNION_RELEASE/workdir/temp")