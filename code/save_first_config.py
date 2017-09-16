# coding=utf-8 
from global_var import *
import urlparse
from dbwrapper import DBWrapper
import sys

class save_first_config:
    def GET(self):
        pass

    def POST(self):
        data = web.data()
        parsed_data = urlparse.parse_qs(data)
        request_type = parsed_data.get('action')[0]
        if request_type == 'save_config':
            config = eval(parsed_data.get('config')[0])
            if config:
                try:
                    db = DBWrapper(dbpath)
                    db.create_config_table("abcsd")
                    for item in config:
                        db.insert_to_config_table("abcsd", item["Path"], item["Group"])
                    return "success"
                except:
                    return "插入数据库失败" + str(sys.exc_info()[0])
            else:
                return "无法解析配置"
        else:
            return '不明确的请求'