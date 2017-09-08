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
            filesize = len(x.input_files)
            filepath = x.filepath.replace('\\','/') # replaces the windows-style slashes with linux ones.
            filename = filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
            filename = md5 + "-" + str(filesize) + "-"  + filename;
            if not os.path.exists(temp_path):
                os.makedirs(temp_path)
            fout = open(temp_path +'/'+ filename,'wb') # creates the file where the uploaded file should be stored
            fout.write(x.input_files) # writes the uploaded file to the newly created file.
            fout.close() # closes the file, upload complete.
            g_new_version[MOD_FILES][filepath] = {MOD_FILES_FILENAME : filename, MOD_FILES_FILEHASH: md5, MOD_FILES_FILESIZE : filesize}
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
                g_new_version[PARENT_VERSION_ID] = parent_version_id
                return json.dumps({"state" : "success", "filelist" : filelist})
            elif request_type == 'upload_complete':
                print g_new_version[MOD_FILES]
                fm = file_manage.file_manage()
                fm.arrange_file_from_temp_path(g_new_version[MOD_FILES])
                db = dbwrapper.DBWrapper(dbpath)
                db.create_new_version_from_file_list(g_new_version[PARENT_VERSION_ID], g_new_version[MOD_FILES], None, None, 1, "第一次用界面修改版本")
                g_new_version[MOD_FILES].clear()
            else:
                return json.dumps({"state" : "fail", "info" : "unknown request"})

if __name__=="__main__":

    os.makedirs("d:/work2/PKPM_UNION_RELEASE/workdir/temp")