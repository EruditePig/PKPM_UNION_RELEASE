# coding=utf-8 

from global_var import *
from global_setting import *
import dbwrapper
import urlparse
import sys
import json
import random
import hashlib
import file_manage

class upload_first_version:
    def GET(self):
        pass

    def POST(self):
        x = web.input()
        if 'input_files' in x:  # to check if the file-object is created
            md5 = hashlib.md5(x.input_files).hexdigest()
            filesize = len(x.input_files)
            filepath = x.filepath.replace('\\','/') # replaces the windows-style slashes with linux ones.
            filename = x.filename
            project_group_name = x.project_group_name
            filename = md5 + "-" + str(filesize) + "-"  + filename;     # 用hash,filesize和文件名拼出新文件名
            if not os.path.exists(temp_path):
                os.makedirs(temp_path)
            fout = open(temp_path +'/'+ filename,'wb') # creates the file where the uploaded file should be stored
            fout.write(x.input_files) # writes the uploaded file to the newly created file.
            fout.close() # closes the file, upload complete.
            g_new_version[ADD_FILES][filepath] = {FILENAME : filename, FILEHASH: md5, FILESIZE : filesize, ADD_FILES_PROJECT_GROUP_NAME : project_group_name}
            return json.dumps({})   # 成功则随意返回json对象
        else:
            data = web.data()
            parsed_data = urlparse.parse_qs(data)
            request_type = parsed_data.get('action')[0]
            if request_type == 'upload_complete':
                # fm = file_manage.file_manage()
                # fm.arrange_file_from_temp_path(g_new_version[ADD_FILES])
                # 创建新版本
                db = dbwrapper.DBWrapper(dbpath)
                db.create_new_version_from_file_list(None, None, g_new_version[ADD_FILES], None, 1, "第一次用界面创建版本")
                g_new_version[ADD_FILES].clear()
            else:
                return json.dumps({"state" : "fail", "info" : "unknown request"})