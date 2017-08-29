# coding=utf-8 
# pylint: diable=C0103

import sqlite3
import sys
import os

class DBWrapper(object):
    """数据库Wrapper"""
    FILE_ADD = "ADD"
    FILE_DEL = "DEL"
    FILE_MOD = "MOD"
    STAFF_DEL = "DEL"
    STAFF_NORMAL = "NORMAL"

    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row     # row获取的时候为字典

    def __del__(self):
        self.conn.close()

    def create_version_list_table(self):
        """创建版本列表"""
        c = self.conn.cursor()
        stmt = ("CREATE TABLE IF NOT EXISTS VERSION_LIST"
                "(ID INTEGER PRIMARY KEY AUTOINCREMENT    NOT NULL,"      # 版本ID
                "CONFIG_TABLE    TEXT    NOT NULL,"                       # 该版本对应的配置表
                "CHILD_VER_CONFIG_TABLE   TEXT,"                          # 该版本的子版本对应的配置表，若不为，则子版本必须用该配置表；若为空，则子版本使用和该版本相同的配置表
                "PARENT_VER_ID  TEXT     ,"                               # 该版本的父版本ID，转为TEXT
                "CHILD_VER_ID   TEXT     ,"                               # 该版本的子版本ID，可以有多个子版本，分号分隔
                "VER_NAME       TEXT    ,"                                # 该版本别名
                "VER_TYPE       TEXT    NOT NULL);")                      # 该版本类型
        c.execute(stmt)        
        self.conn.commit()

    def insert_to_verion_list_table(self, config_table_name, parent_ver_id, \
                                child_ver_id, ver_name, ver_type):
        """插入一个版本到版本列表
            parent_id如果为0,child_id如果为[]，则表示为NULL
            child_id如果有多个，用分号分隔
        """
        c = self.conn.cursor()
        stmt = "REPLACE INTO VERSION_LIST VALUES (NULL, "
        stmt += " '" + config_table_name + "', "
        stmt += " NULL , "
        stmt += (" '" + str(parent_ver_id) + "' " if parent_ver_id != 0 else "NULL")  + ", "
        stmt += (" '" + ';'.join(str(x) for x in child_ver_id) + "' " if child_ver_id else "NULL") + ", "
        stmt += " '" + ver_name + "', "
        stmt += " '" + ver_type + "');"
        c.execute(stmt)
        self.conn.commit()
    
    def get_version_list(self):
        """
        获得版本列表
        [OUT]
        version_tree - {ver_id, [child_ver_id]}
        """
        c = self.conn.cursor()
        c.execute("SELECT * FROM VERSION_LIST;")
        version_tree = {}
        fetch = c.fetchmany
        while True:
            rows = fetch(1000)
            if not rows: break
            for row in rows:
                if row["CHILD_VER_ID"]:
                    child_id = [int(x) for x in row["CHILD_VER_ID"].split(';')]      # child_id
                else:
                    child_id = []
                version_tree[row["ID"]] = child_id
        return version_tree

    def get_child_version_config_table(self, version_id):
        """
        返回子版本的配置表名，如果子版本配置表不为空，则返回之；否则返回该版本的配置表，让子版本继承
        [IN]
        version_id - 父版本id
        [OUT]
        config_table - 配置表名
        """
        version_info = self.get_version_info(version_id)
        if version_info:
            if version_info["CHILD_VER_CONFIG_TABLE"]:
                return version_info["CHILD_VER_CONFIG_TABLE"]
            else:
                return version_info["CONFIG_TABLE"]
        else:
            return None


    def get_version_info(self, version_id):
        """
        获得版本信息
        [IN]
        version_id
        [OUT]
        {}具体key参见Create Table时列的指定
        """
        c = self.conn.cursor()
        stmt = "SELECT * FROM VERSION_LIST WHERE ID == " + str(version_id)+ ";"
        c.execute(stmt)
        row = c.fetchone()
        c.close()
        if row:
            return row
        else:
            return None

    def create_project_group_permission_table(self):
        """创建各项目组权限列表"""
        c = self.conn.cursor()
        stmt = ("CREATE TABLE IF NOT EXISTS PROJECT_GROUP_PERMISSION"
                "(NAME TEXT PRIMARY KEY     NOT NULL,"        # 项目组名
                "CAN_UPLOAD    BOOLEAN    NOT NULL,"          # 是否能上传
                "CAN_EDIT_CONFIG  BOOLEAN    NOT NULL);") # 是否能编辑项目表
        c.execute(stmt) 
        self.conn.commit()
        
    def insert_to_project_group_permission_table(self, group_name, can_upload, can_edit_config):
        """插入各项目组权限列表"""
        c = self.conn.cursor()
        stmt = "REPLACE INTO PROJECT_GROUP_PERMISSION VALUES ("
        stmt += " '" + group_name + "', "
        stmt += " " + ("1" if can_upload else "0")  + ", "
        stmt += " " + ("1" if can_edit_config else "0") + ");"
        c.execute(stmt)
        self.conn.commit()

    def create_staff_table(self):
        """创建人员列表"""
        c = self.conn.cursor()
        stmt = ("CREATE TABLE IF NOT EXISTS STAFF"
                "(ID INTEGER PRIMARY KEY     NOT NULL,"       # 人员ID
                "NAME    TEXT    NOT NULL,"                   # 人员名
                "PROJECT_GROUP_NAME  TEXT    NOT NULL,"       # 人员所属项目组
                "STATE  TEXT    NOT NULL);")
        c.execute(stmt)
        self.conn.commit()

    def insert_to_staff_table(self, name, project_group_name, state):
        """创建人员列表
        project_group_name可以是数组，一个人可以属于多个项目组，用分号分隔
        """
        c = self.conn.cursor()
        stmt = "REPLACE INTO STAFF VALUES (NULL, "
        stmt += " '" + name + "', "
        stmt += " '" + ";".join(project_group_name)  + "', "
        stmt += " '" + state + "');"
        c.execute(stmt)
        self.conn.commit()

    def create_config_create_log_table(self):
        """创建配置表的创建记录表"""
        c = self.conn.cursor()
        stmt = ("CREATE TABLE IF NOT EXISTS CONFIG_CREATE_LOG"
                "(CONFIG_NAME TEXT PRIMARY KEY     NOT NULL,"     # 配置表名
                "TIMESTAMP    DATATIME    NOT NULL,"              # 创建时间
                "STAFF_ID  INTEGER    NOT NULL,"                  # 谁创建的
                "DESCRIPTION  TEXT    NOT NULL);")
        c.execute(stmt)             # 描述
        self.conn.commit()

    def insert_to_config_create_log_table(self, config_name, datetime, staff, description):
        """插入配置文件创建记录表"""
        c = self.conn.cursor()
        stmt = "REPLACE INTO CONFIG_CREATE_LOG VALUES ("
        stmt += " '" + config_name + "', "
        stmt += " '" + datetime  + "', "
        stmt += " '" + staff  + "', "
        stmt += " '" + description + "');"
        c.execute(stmt)
        self.conn.commit()

    def create_config_table(self, config_name):
        """创建配置文件"""
        c = self.conn.cursor()
        stmt = "CREATE TABLE IF NOT EXISTS " + config_name
        stmt += ("(PATH TEXT PRIMARY KEY     NOT NULL,"          # 文件路径
                 " PROJECT_GROUP_NAME    TEXT    NOT NULL);")     # 所属项目组
        c.execute(stmt)
        self.conn.commit()

    def insert_to_config_table(self, config_name, path, project_group_name):
        """插入配置文件"""
        c = self.conn.cursor()
        stmt = "REPLACE INTO "
        stmt += config_name + " VALUES ("
        stmt += " '" + path + "', "
        stmt += " '" + project_group_name  + "');"
        c.execute(stmt)
        self.conn.commit()

    def create_version_table(self, version_id):
        """创建版本（仅记录相对上个版本的改动）"""
        c = self.conn.cursor()
        stmt = "CREATE TABLE IF NOT EXISTS VERSION_" + str(version_id)
        stmt += ("(PATH TEXT PRIMARY KEY     NOT NULL,"     # 路径
                 "HASH TEXT    NOT NULL,"                   # 哈希值
                 "FILESIZE INTEGER NOT NULL,"               # 文件大小
                 "STATE TEXT NOT NULL);")                   # 文件状态
        c.execute(stmt)
        self.conn.commit()

    def insert_version_table(self, version_id, path, hashvalue, filesize, state):
        """插入版本（仅记录相对上个版本的改动）"""
        c = self.conn.cursor()
        stmt = "REPLACE INTO VERSION_"
        stmt += str(version_id) + " VALUES ("
        stmt += " '" + path + "', "
        stmt += " '" + hashvalue + "', "
        stmt += " " + str(filesize) + ", "
        stmt += " '" + state  + "');"
        c.execute(stmt)
        self.conn.commit()

    def get_version_table(self, version_id):
        """
        获得某版本文件列表
        [IN]
        version_id
        [OUT]
        {filepath, {//HASH,FILESIZE,STATE}}
        """
        c = self.conn.cursor()
        stmt = "SELECT * FROM VERSION_"
        stmt += str(version_id) + ";"
        c.execute(stmt)

        version_file_list = []
        fetch = c.fetchmany
        while True:
            rows = fetch(1000)
            if not rows: break
            for row in rows:
                version_file_list[row["PATH"]] = {}
                version_file_list[row["PATH"]]["HASH"] = row["HASH"]
                version_file_list[row["PATH"]]["FILESIZE"] = row["FILESIZE"]
                version_file_list[row["PATH"]]["STATE"] = row["STATE"]
        c.close()
        return version_file_list

    def get_file_paths_from_config_table_filter_staff_id(self, config_table, staff_id):
        """
        根据staff_id查询其在配置文件列表中负责的文件
        """
        file_paths = []

        c = self.conn.cursor()
        stmt = "SELECT PROJECT_GROUP_NAME FROM STAFF WHERE ID == " + str(staff_id)+ ";"
        c.execute(stmt)
        row = c.fetchone()
        if row:
            ss = ','.join("'" + x + "'" for x in row[0].split(";"))
            stmt = "SELECT * FROM " + config_table + " WHERE PROJECT_GROUP_NAME IN (" + ss + ");"
            c.execute(stmt)
            fetch = c.fetchmany
            while True:
                rows = fetch(1000)
                if not rows: break
                for row in rows:
                    file_paths.append(row[0])
        c.close()
        return file_paths
    
    def get_version_file_list(self, version_id):
        """
        获取某版本的所有文件及其hash值
        [IN]
        version_id
        [OUT]
        version_file_list - {filepath, {//HASH,FILESIZE,STATE}}
        """
        version_file_list = []
        (version_path, root_version_id) = self.get_version_tree_to_root(version_id)
        current_version_id = root_version_id
        
        while True:
            if current_version_id != version_id:
                current_version_file_list = self.get_version_table(current_version_id)
                self.combine_version_file_list(version_file_list, current_version_file_list)
                current_version_id = version_path[current_version_id]
            else:
                current_version_file_list = self.get_version_table(current_version_id)
                self.combine_version_file_list(version_file_list, current_version_file_list)
                return version_file_list
        return None

    def combine_version_file_list(self, file_list1, file_list2):
        """
        合并filelist2到filelist1中
        [INOUT]
        filelist1 - {filepath, {//HASH,FILESIZE,STATE}}
        [IN]
        filelist2
        """
        for key in file_list2:
            if key in file_list1:
                if file_list2[key]["STATE"] == DBWrapper.FILE_MOD:
                    file_list1[key]["HASH"] = file_list2[key]["HASH"]
                    file_list1[key]["FILESIZE"] = file_list2[key]["FILESIZE"]
                elif file_list2[key]["STATE"] == DBWrapper.FILE_DEL:
                    file_list1.pop(key)
            else:
                if file_list2[key]["STATE"] == DBWrapper.FILE_ADD:
                    file_list1[key] = file_list2[key]

    def get_version_tree_to_root(self, version_id):
        """
        给定版本号，返回从最开始的根节点到该版本节点的路径
        [IN]
        版本号
        [OUT]
        从根节点到该版本节点的路径{parent_verison,child_version}
        根节点 root_version
        """
        version_path = {}
        version_info = self.get_version_info(version_id)
        while version_info:
            if version_info["PARENT_VER_ID"]:
                parent_id = int(version_info["PARENT_VER_ID"])
                version_path[parent_id] = version_id
                version_id = parent_id
                version_info = self.get_version_info(version_id)
            else:       # 当parent_id为空的时候，表示找到根节点了
                return (version_path, version_id)
        return None     # 如果某个版本的version_info找不到，则表示出错了，返回None


def populate_db(dbname):
    """
    生成一个数据库
    """
    db = DBWrapper(dbname)
    # 先创建需要的表格
    db.create_version_list_table()
    db.create_project_group_permission_table()
    db.create_staff_table()
    db.create_config_create_log_table()
    db.create_config_table("config1")
    
    # 给config1填充
    db.insert_to_config_table("config1", "Graphviz\\share\\graphviz\\doc\\AUTHORS", "建模项目组")
    db.insert_to_config_table("config1", "Graphviz\\share\\graphviz\\doc\\ChangeLog", "建模项目组")
    db.insert_to_config_table("config1", "Graphviz\\share\\graphviz\\doc\\COPYING", "建模项目组")
    db.insert_to_config_table("config1", "Graphviz\\share\\man\\man1\\bcomps.1", "建模项目组")
    db.insert_to_config_table("config1", "Graphviz\\share\\man\\man1\\circo.1", "建模项目组")
    db.insert_to_config_table("config1", "Graphviz\\share\\man\\man1\\ccomps.1", "建模项目组")
    db.insert_to_config_table("config1", "Graphviz\\share\\man\\man1\\dijkstra.1", "建模项目组")
    db.insert_to_config_table("config1", "Graphviz\\bin\\config6", "建模项目组")
    db.insert_to_config_table("config1", "Graphviz\\gtk-2.0\\gtkrc", "建模项目组")
    

if __name__ == '__main__':

    # 修改工作目录
    py_file_path = sys.path[0]
    work_path = os.path.abspath(os.path.join(py_file_path, '..//workdir'))
    os.chdir(work_path)

    # 生成数据库
    populate_db("test.db")
    
    # 连接数据库
    #db = DBWrapper("test.db")
    #db.create_version_list_table()
    #db.create_project_group_permission_table()
    #db.create_staff_table()
    #db.create_config_create_log_table()
    #db.create_config_table("abc")
    #db.create_version_table(1)

    # 插入数据库
    #db.insert_to_verion_list_table("abc", 0, [1,2], "V3.1.5", "测试版")
    #db.insert_to_verion_list_table("abc", 1, [], "V3.1.5", "测试版")
    #db.insert_to_project_group_permission_table("产品设计组", True, False)
    #db.insert_to_staff_table("史建鑫", ["产品设计部", "建模研发部"], "正常")
    #db.insert_to_config_create_log_table("abc", "2017-08-13 00:20:00", "史建鑫", "应***要求添加")
    #db.insert_to_config_table("abc", "CFG\\abc", "建模研发部")
    #db.insert_to_config_table("abc", "CFG\\1232", "结构研发部")
    #db.insert_version_table(1, "CFG\\abc", "231713", 12150, "添加")

    #version_tree = db.get_version_list() # 输出所有版本
    #print db.get_child_version_config_table(1)  # 输出某个版本
    #filepaths = db.get_file_paths_from_config_table_filter_staff_id("abc", 1);
    #print filepaths

    print "end"
