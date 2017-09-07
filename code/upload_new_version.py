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

class upload_new_version:
    def GET(self):
        pass

    def POST(self):
        x = web.input()
        if 'input_files' in x:  # to check if the file-object is created
            md5 = hashlib.md5(x.input_files).hexdigest()
            size = len(x.input_files)
            filepath = x.filepath.replace('\\','/') # replaces the windows-style slashes with linux ones.
            filename = filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
            filename = md5 + "-" + str(size) + "-"  + filename;
            if not os.path.exists(temp_path):
                os.makedirs(temp_path)
            fout = open(temp_path +'/'+ filename,'wb') # creates the file where the uploaded file should be stored
            fout.write(x.input_files) # writes the uploaded file to the newly created file.
            fout.close() # closes the file, upload complete.
            g_new_version[ADD_FILES].append({
                ADD_FILES_FILEPATH : filepath,
                ADD_FILES_FILENAME : filename,
                ADD_FILES_FILEHASH : md5,
                ADD_FILES_FILESIZE : size
            })
            return json.dumps({})
        else:
            data = web.data()
            parsed_data = urlparse.parse_qs(data)
            request_type = parsed_data.get('action')[0]
            if request_type == 'request_config':
                parent_version_id = parsed_data.get('parent_version_id')[0]
                db = dbwrapper.DBWrapper(dbpath)
                staff_id = 1
                filelist = db.get_filelist(parent_version_id, staff_id)
                return json.dumps({"state" : "success", "filelist" : filelist})
                try:
                    db = dbwrapper.DBWrapper(dbpath)
                    config_log = db.get_config_create_log_table()
                    first_config_name = config_log[0][dbwrapper.DBWrapper.CONFIG_CREATE_LOG_CONFIG_NAME]
                    config = db.get_config_table(first_config_name)
                    return json.dumps({"state" : "success", "config" : config})
                except:
                    return json.dumps({"state" : "fail", "info" : str(sys.exc_info()[0])})
            elif request_type == 'upload_complete':
                fm = file_manage.file_manage()
                fm.arrange_file_from_temp_path(g_new_version["files"])
                g_new_version[ADD_FILES] = []
            else:
                return json.dumps({"state" : "fail", "info" : "unknown request"})

if __name__=="__main__":

    os.makedirs("d:/work2/PKPM_UNION_RELEASE/workdir/temp")