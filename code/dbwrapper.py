# coding=utf-8
"""数据库Wrapper"""
# pylint: disable=C0103
# pylint: disable=C0301

from global_var import *
from global_setting import *
import sqlite3
import sys
import os
import time

class DBWrapper(object):
    """数据库Wrapper"""
    STAFF_DEL = "DEL"
    STAFF_NORMAL = "NORMAL"

    # 版本列表
    VERSION_LIST = "VERSION_LIST"
    VERSION_LIST_ID = "ID"                              # INTEGER AUTO INCREAMENT
    VERSION_LIST_CONFIG_TABLE_ID = "CONFIG_TABLE_ID"    # INTEGER
    VERSION_LIST_STAFF_ID = "STAFF_ID"                  # INTEGER
    VERSION_LIST_PARENT_VER_ID = "PARENT_VER_ID"        # TEXT
    VERSION_LIST_CHILD_VER_ID = "CHILD_VER_ID"          # TEXT
    VERSION_LIST_VER_NAME = "VER_NAME"                  # TEXT
    VERSION_LIST_VER_TYPE = "VER_TYPE"                  # TEXT
    VERSION_LIST_DESCRIPTION = "DESCRIPTION"            # TEXT

    # 项目组权限表
    PROJECT_GROUP_PERMISSION = "PROJECT_GROUP_PERMISSION"
    PROJECT_GROUP_PERMISSION_NAME = "NAME"              # TEXT PRIMARY KEY NOT NULL
    PROJECT_GROUP_PERMISSION_CAN_UPLOAD = "CAN_UPLOAD"  # BOOLEAN NOT NULL
    PROJECT_GROUP_PERMISSION_CAN_EDIT_CONFIG = "CAN_EDIT_CONFIG"    # BOOLEAN NOT NULL

    # 用户列表
    STAFF = "STAFF"
    STAFF_ID = "ID"                                     # INTEGER PRIMARY KEY NOT NULL
    STAFF_NAME = "NAME"                                 # TEXT NOT NULL
    STAFF_PROJECT_GROUP_NAME = "PROJECT_GROUP_NAME"     # TEXT NOT NULL
    STAFF_STATE = "STATE"                               # TEXT NOT NULL

    # 配置记录表
    CONFIG_CREATE_LOG = "CONFIG_CREATE_LOG"
    CONFIG_CREATE_LOG_CONFIG_ID = "CONFIG_ID"           # INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL
    CONFIG_CREATE_LOG_TIMESTAMP = "TIMESTAMP"           # DATATIME NOT NULL
    CONFIG_CREATE_LOG_STAFF_ID = "STAFF_ID"             # INTEGER NOT NULL
    CONFIG_CREATE_LOG_DESCRIPTION = "DESCRIPTION"       # TEXT NOT NULL

    # 具体配置
    CONFIG_DETAIL = "CONFIG_"
    CONFIG_PATH = "PATH"                                # TEXT PRIMARY KEY NOT NULL
    CONFIG_HASH = "HASH"                                # TEXT NOT NULL
    CONFIG_FILESIZE = "FILESIZE"                        # INTEGER NOT NULL
    CONFIG_PROJECT_GROUP_NAME = "PROJECT_GROUP_NAME"    # TEXT NOT NULL

    # 版本信息表
    VERSION_DETAIL = "VERSION_"
    VERSION_DETAIL_PATH = "PATH"                        # TEXT PRIMARY KEY NOT NULL
    VERSION_DETAIL_HASH = "HASH"                        # TEXT NOT NULL
    VERSION_DETAIL_FILESIZE = "FILESIZE"                # INTEGER NOT NULL
    VERSION_DETAIL_STATE = "STATE"                      # TEXT NOT NULL
    FILE_ADD = "ADD"
    FILE_DEL = "DEL"
    FILE_MOD = "MOD"
    VERSION_TYPE_ALPHA = "ALPHA"
    VERSION_TYPE_BETA = "BETA"
    VERSION_TYPE_GAMMA = "GAMMA"

    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row     # row获取的时候为字典

    def __del__(self):
        self.conn.close()

    def is_table_exist(self, table_name):
        """
        查找表格是否存在
        """
        stmt = "SELECT count(name) FROM sqlite_master WHERE type = 'table' AND name = '{0}';".format(table_name)
        c = self.conn.cursor()
        c.execute(stmt)
        row = c.fetchone()
        return row[0] == 1

    def is_table_empty(self, table_name):
        """
        判断表格是否为空，如果表格不存在或者存在但没有数据，那都算为空
        """
        if not self.is_table_exist(table_name):
            return True
        else:
            stmt = "SELECT count(*) FROM '{0}';".format(table_name)
            c = self.conn.cursor()
            c.execute(stmt)
            row = c.fetchone()
            return row[0] == 0

    def create_version_list_table(self):
        """创建版本列表"""
        c = self.conn.cursor()
        stmt = "CREATE TABLE IF NOT EXISTS {0} ({1} INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                                                {2} INTEGER NOT NULL,            \
                                                {3} INTEGER NOT NULL,            \
                                                {4} TEXT,                        \
                                                {5} TEXT,                        \
                                                {6} TEXT,                        \
                                                {7} TEXT NOT NULL,               \
                                                {8} TEXT NOT NULL                \
                                                );".format(DBWrapper.VERSION_LIST, DBWrapper.VERSION_LIST_ID,
                                                DBWrapper.VERSION_LIST_CONFIG_TABLE_ID, # {2}配置表ID
                                                DBWrapper.VERSION_LIST_STAFF_ID,        # {3}创建版本的用户ID
                                                DBWrapper.VERSION_LIST_PARENT_VER_ID,   # {4}父版本ID，如果没有父版本，则为NULL
                                                DBWrapper.VERSION_LIST_CHILD_VER_ID,    # {5}该版本的子版本ID，可以有多个子版本，分号分隔
                                                DBWrapper.VERSION_LIST_VER_NAME,        # {6}该版本别名
                                                DBWrapper.VERSION_LIST_VER_TYPE,        # {7}该版本类型
                                                DBWrapper.VERSION_LIST_DESCRIPTION      # {8}版本描述信息
                                                )
        print stmt
        c.execute(stmt)
        self.conn.commit()

    def insert_to_verion_list_table(self, config_table_id, staff_id, parent_ver_id, description):
        """
        插入一个版本到版本列表
        [IN]
        config_table_id - int 配置表id
        staff_id - int 创建版本的用户ID
        parent_ver_id - int 父版本id，为None则为NULL
        description - str 版本描述信息
        [OUT]
        version_id - 新插入的版本id
        """
        # 先插入版本，获得版本号
        stmt = "INSERT INTO {0} VALUES (NULL, {1}, {2}, {3}, NULL, NULL, {4}, {5});".format(
            DBWrapper.VERSION_LIST, 
            str(config_table_id),       # {1}配置表ID
            str(staff_id),              # {2}创建版本的用户ID
            (("'" + str(parent_ver_id) + "'") if parent_ver_id else "NULL"),    # {3}父版本ID，如果没有父版本，则为NULL
            ("'" + DBWrapper.VERSION_TYPE_ALPHA + "'"),      # {4}版本类型
            ("'" + description + "'")                        # {5}版本描述信息
        )
        c = self.conn.cursor()
        c.execute(stmt)
        self.conn.commit()
        child_ver_id = c.lastrowid

        if not parent_ver_id:   # 父版本为空，则直接返回版本号
            return child_ver_id
        else:   # 更新父版本中的子版本信息
            parent_version_info = self.get_one_version_info(parent_ver_id)
            if parent_version_info:
                # 更新父版本记录中的子版本号
                if parent_version_info[DBWrapper.VERSION_LIST_CHILD_VER_ID]:
                    child_id_list = [int(x) for x in parent_version_info[DBWrapper.VERSION_LIST_CHILD_VER_ID].split(';')]
                    child_id_list.append(child_ver_id)
                else:
                    child_id_list = [child_ver_id]
                stmt = "REPLACE INTO {0} VALUES ({1}, {2}, {3}, {4}, {5}, {6}, {7}, {8});".format(
                    DBWrapper.VERSION_LIST,         # {0} VERSION_LIST
                    str(parent_version_info[DBWrapper.VERSION_LIST_ID]),  # {1} ID
                    str(parent_version_info[DBWrapper.VERSION_LIST_CONFIG_TABLE_ID]),  # {2} 配置表ID
                    str(parent_version_info[DBWrapper.VERSION_LIST_STAFF_ID]),  # {3} 用户ID
                    ("'" + parent_version_info[DBWrapper.VERSION_LIST_PARENT_VER_ID] + "'") if parent_version_info[DBWrapper.VERSION_LIST_PARENT_VER_ID] else "NULL",    # {4} 父版本ID
                    "'" + ';'.join(str(x) for x in child_id_list) + "'",     # {5} 子版本ID
                    ("'" + parent_version_info[DBWrapper.VERSION_LIST_VER_NAME] + "'") if parent_version_info[DBWrapper.VERSION_LIST_VER_NAME] else "NULL",     # {6} 版本别名
                    ("'" + parent_version_info[DBWrapper.VERSION_LIST_VER_TYPE]  + "'") if parent_version_info[DBWrapper.VERSION_LIST_VER_TYPE] else "NULL",    # {7} 版本类型
                    ("'" + parent_version_info[DBWrapper.VERSION_LIST_DESCRIPTION]  + "'") if parent_version_info[DBWrapper.VERSION_LIST_DESCRIPTION] else "NULL"    # {8} 版本描述
                )
                # 这里要是插入错误，可以throw一个error
                c = self.conn.cursor()
                c.execute(stmt)
                self.conn.commit()
                return child_ver_id
            else:
                return None

    def get_version_hierachy(self):
        """
        获得版本列表
        [OUT]
        version_tree - {ver_id, [child_ver_id]}
        """
        c = self.conn.cursor()
        stmt = "SELECT * FROM " + DBWrapper.VERSION_LIST + ";"
        c.execute(stmt)
        version_tree = {}
        fetch = c.fetchmany
        while True:
            rows = fetch(1000)
            if not rows:
                break
            for row in rows:
                if row[DBWrapper.VERSION_LIST_CHILD_VER_ID]:
                    child_id = [int(x) for x in row[DBWrapper.VERSION_LIST_CHILD_VER_ID].split(';')]      # child_id
                else:
                    child_id = []
                version_tree[row[DBWrapper.VERSION_LIST_ID]] = child_id
        return version_tree

    def get_one_version_info(self, version_id):
        """
        获得某个版本信息
        [IN]
        version_id
        [OUT]
        {}具体key参见Create Table时列的指定
        """
        c = self.conn.cursor()
        stmt = "SELECT * FROM " + DBWrapper.VERSION_LIST + " WHERE ID == " + str(version_id)+ ";"
        c.execute(stmt)
        row = c.fetchone()
        c.close()
        if row:
            ver_info = {DBWrapper.VERSION_LIST_ID : row[DBWrapper.VERSION_LIST_ID],
                        DBWrapper.VERSION_LIST_CONFIG_TABLE_ID : row[DBWrapper.VERSION_LIST_CONFIG_TABLE_ID],
                        DBWrapper.VERSION_LIST_STAFF_ID : row[DBWrapper.VERSION_LIST_STAFF_ID],
                        DBWrapper.VERSION_LIST_PARENT_VER_ID : row[DBWrapper.VERSION_LIST_PARENT_VER_ID],
                        DBWrapper.VERSION_LIST_CHILD_VER_ID : row[DBWrapper.VERSION_LIST_CHILD_VER_ID],
                        DBWrapper.VERSION_LIST_VER_NAME : row[DBWrapper.VERSION_LIST_VER_NAME],
                        DBWrapper.VERSION_LIST_VER_TYPE : row[DBWrapper.VERSION_LIST_VER_TYPE],
                        DBWrapper.VERSION_LIST_DESCRIPTION : row[DBWrapper.VERSION_LIST_DESCRIPTION],
                        }
            return ver_info
        else:
            return None

    def create_project_group_permission_table(self):
        """
        创建各项目组权限列表
        """
        c = self.conn.cursor()
        stmt = "CREATE TABLE IF NOT EXISTS {0} ({1} TEXT PRIMARY KEY NOT NULL, {2} BOOLEAN NOT NULL, {3} BOOLEAN NOT NULL)".format(
            DBWrapper.PROJECT_GROUP_PERMISSION,
            DBWrapper.PROJECT_GROUP_PERMISSION_NAME,        # 项目组名
            DBWrapper.PROJECT_GROUP_PERMISSION_CAN_UPLOAD,  # 是否能上传
            DBWrapper.PROJECT_GROUP_PERMISSION_CAN_EDIT_CONFIG, # 是否能编辑项目表
        )
        c.execute(stmt)
        self.conn.commit()

    def insert_to_project_group_permission_table(self, group_name, can_upload, can_edit_config):
        """
        插入各项目组权限列表
        """
        c = self.conn.cursor()
        stmt = "REPLACE INTO {0} VALUES ({1}, {2}, {3});".format(
            DBWrapper.PROJECT_GROUP_PERMISSION,
            "'" + group_name + "'",
            "1" if can_upload else "0",
            "1" if can_edit_config else "0"
        )
        c.execute(stmt)
        self.conn.commit()

    def create_staff_table(self):
        """
        创建人员列表
        """
        stmt = "CREATE TABLE IF NOT EXISTS {0} ({1} INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, {2} TEXT NOT NULL, {3} TEXT NOT NULL, {4} TEXT NOT NULL);".format(
            DBWrapper.STAFF,
            DBWrapper.STAFF_ID,
            DBWrapper.STAFF_NAME,
            DBWrapper.STAFF_PROJECT_GROUP_NAME,
            DBWrapper.STAFF_STATE
        )
        c = self.conn.cursor()
        c.execute(stmt)
        self.conn.commit()

    def insert_to_staff_table(self, name, project_group_name, state):
        """
        创建人员列表
        project_group_name可以是数组，一个人可以属于多个项目组，用分号分隔
        """
        stmt = "REPLACE INTO {0} VALUES (NULL, {1}, {2}, {3});".format(
            DBWrapper.STAFF,
            "'" + name + "'",
            "'" + ";".join(project_group_name) + "'",
            "'" + state + "'"
        )
        c = self.conn.cursor()
        c.execute(stmt)
        self.conn.commit()

    def create_config_create_log_table(self):
        """
        创建配置表的创建记录表
        """
        stmt = "CREATE TABLE IF NOT EXISTS {0} ({1} INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, {2} DATATIME NOT NULL, {3} INTEGER NOT NULL, {4} TEXT NOT NULL);".format(
            DBWrapper.CONFIG_CREATE_LOG,
            DBWrapper.CONFIG_CREATE_LOG_CONFIG_ID,
            DBWrapper.CONFIG_CREATE_LOG_TIMESTAMP,
            DBWrapper.CONFIG_CREATE_LOG_STAFF_ID,
            DBWrapper.CONFIG_CREATE_LOG_DESCRIPTION
        )
        c = self.conn.cursor()
        c.execute(stmt)             # 描述
        self.conn.commit()

    def insert_to_config_create_log_table(self, staff_id, description):
        """
        插入配置文件创建记录表
        [IN]
        staff_id - int
        description - str
        [OUT]
        config_id - int 配置表ID
        """
        stmt = "INSERT INTO {0} VALUES (NULL, {1}, {2}, {3});".format(
            DBWrapper.CONFIG_CREATE_LOG,
            "DATETIME(" + str(int(time.time())) + ", 'unixepoch', 'localtime')",
            str(staff_id),
            "'" + description + "'"
        )
        c = self.conn.cursor()
        c.execute(stmt)
        self.conn.commit()
        return c.lastrowid

    def get_config_create_log_table(self):
        """
        获取所有配置文件记录
        [OUT]
        config_log = {CONFIG_ID : {TIMESTAMP,STAFF_ID,DESCRIPTION}}
        """
        stmt = "SELECT * FROM " + DBWrapper.CONFIG_CREATE_LOG + ";"
        c = self.conn.cursor()
        c.execute(stmt)
        fetch = c.fetchmany
        config_log = {}
        while True:
            rows = fetch(1000)
            if not rows:
                break
            for row in rows:
                config_log[str(row[DBWrapper.CONFIG_CREATE_LOG_CONFIG_ID])] = {DBWrapper.CONFIG_CREATE_LOG_TIMESTAMP : row[DBWrapper.CONFIG_CREATE_LOG_TIMESTAMP],
                                                                            DBWrapper.CONFIG_CREATE_LOG_STAFF_ID : row[DBWrapper.CONFIG_CREATE_LOG_STAFF_ID],
                                                                            DBWrapper.CONFIG_CREATE_LOG_DESCRIPTION : row[DBWrapper.CONFIG_CREATE_LOG_DESCRIPTION]}
        return config_log

    def create_config_table(self, config_id):
        """
        创建配置表
        [IN]
        config_id - int 配置表id
        """
        stmt = "CREATE TABLE IF NOT EXISTS {0}{1} ({2} TEXT PRIMARY KEY NOT NULL, {3} TEXT NOT NULL, {4} INTEGER NOT NULL, {5} TEXT NOT NULL);".format(
            DBWrapper.CONFIG_DETAIL,
            str(config_id),
            DBWrapper.CONFIG_PATH,
            DBWrapper.CONFIG_HASH,
            DBWrapper.CONFIG_FILESIZE,
            DBWrapper.CONFIG_PROJECT_GROUP_NAME
        )
        c = self.conn.cursor()
        c.execute(stmt)
        self.conn.commit()

    def insert_to_config_table(self, config_id, path, hashstr, filesize, project_group_name):
        """
        插入配置文件
        [IN]
        config_id - int 配置表id
        path - str 文件路径
        hashstr - str 文件hash
        filesize _ int 文件大小
        project_group_name - str 所属团队
        """
        stmt = "REPLACE INTO {0}{1} VALUES ({2}, {3}, {4}, {5});".format(
            DBWrapper.CONFIG_DETAIL,
            str(config_id),
            "'" + path.replace('\\', '/') + "'",
            "'" + hashstr + "'",
            str(filesize),
            "'" + project_group_name  + "'"
        )
        c = self.conn.cursor()
        c.execute(stmt)
        self.conn.commit()

    def create_fill_config_table(self, staff_id, description, new_config_info):
        """
        创建并填充配置表
        [IN]
        staff_id - int 用户ID
        description - str 配置表描述
        new_config_info - {CONFIG_PATH : {CONFIG_HASH, CONFIG_FILESIZE, CONFIG_PROJECT_GROUP_NAME}}
        [OUT]
        config_id - int 新建的配置表ID
        """
        config_id = self.insert_to_config_create_log_table(staff_id, description)
        self.create_config_table(config_id)
        for filepath in new_config_info:
            self.insert_to_config_table(
                config_id,
                filepath,
                new_config_info[filepath][DBWrapper.CONFIG_HASH],
                new_config_info[filepath][DBWrapper.CONFIG_FILESIZE],
                new_config_info[filepath][DBWrapper.CONFIG_PROJECT_GROUP_NAME]
            )
        return config_id

    def get_config_table(self, config_id):
        """
        获取某个配置
        [OUT]
        config = {PATH, {HASH, FILESIZE, PROJECT_GROUP_NAME}}
        """
        stmt = "SELECT * FROM " + DBWrapper.CONFIG_DETAIL + str(config_id) + ";"
        c = self.conn.cursor()
        c.execute(stmt)
        fetch = c.fetchmany
        config = {}
        while True:
            rows = fetch(1000)
            if not rows:
                break
            for row in rows:
                config[row[DBWrapper.CONFIG_PATH]] = {DBWrapper.CONFIG_HASH : row[DBWrapper.CONFIG_HASH],
                                                    DBWrapper.CONFIG_FILESIZE : row[DBWrapper.CONFIG_FILESIZE],
                                                    DBWrapper.CONFIG_PROJECT_GROUP_NAME : row[DBWrapper.CONFIG_PROJECT_GROUP_NAME]}
        return config

    def create_version_detail_table(self, version_id):
        """
        创建版本（仅记录相对上个版本的改动）
        """
        stmt = "CREATE TABLE IF NOT EXISTS {0}{1} ({2} TEXT PRIMARY KEY NOT NULL, {3} TEXT NOT NULL, {4} INTEGER NOT NULL, {5} TEXT NOT NULL);".format(
            DBWrapper.VERSION_DETAIL,
            str(version_id),
            DBWrapper.VERSION_DETAIL_PATH,
            DBWrapper.VERSION_DETAIL_HASH,
            DBWrapper.VERSION_DETAIL_FILESIZE,
            DBWrapper.VERSION_DETAIL_STATE
        )
        c = self.conn.cursor()
        c.execute(stmt)
        self.conn.commit()

    def insert_version_table(self, version_id, path, hashvalue, filesize, state):
        """
        插入版本（仅记录相对上个版本的改动）
        """
        stmt = "REPLACE INTO {0}{1} VALUES ({2}, {3}, {4}, {5});".format(
            DBWrapper.VERSION_DETAIL,
            str(version_id),
            "'" + path + "'",
            "'" + hashvalue + "'",
            str(filesize),
            "'" + state + "'"
        )
        c = self.conn.cursor()
        c.execute(stmt)
        self.conn.commit()

    def create_fill_version_detail_table(self, version_id, version_detail):
        """
        创建并填充新的版本信息表
        [IN]
        version_id - int 版本号
        version_detail - {filepath : {HASH, FILESIZE, STATE}}
        """
        self.create_version_detail_table(version_id)
        for filepath in version_detail:
            self.insert_version_table(version_id, filepath, version_detail[filepath][DBWrapper.VERSION_DETAIL_HASH],
                                        version_detail[filepath][DBWrapper.VERSION_DETAIL_FILESIZE], 
                                        version_detail[filepath][DBWrapper.VERSION_DETAIL_STATE])

    def get_version_detail_table(self, version_id):
        """
        获得某版本文件列表
        [IN]
        version_id
        [OUT]
        version_file_list - {filepath, {HASH,FILESIZE,STATE}}
        """
        c = self.conn.cursor()
        stmt = "SELECT * FROM " + DBWrapper.VERSION_DETAIL + str(version_id) + ";"
        c.execute(stmt)

        version_file_list = {}
        fetch = c.fetchmany
        while True:
            rows = fetch(1000)
            if not rows:
                break
            for row in rows:
                version_file_list[row[DBWrapper.VERSION_DETAIL_PATH]] = {
                    DBWrapper.VERSION_DETAIL_HASH : row[DBWrapper.VERSION_DETAIL_HASH],
                    DBWrapper.VERSION_DETAIL_FILESIZE : row[DBWrapper.VERSION_DETAIL_FILESIZE],
                    DBWrapper.VERSION_DETAIL_STATE : row[DBWrapper.VERSION_DETAIL_STATE]
                }
        c.close()
        return version_file_list

    def get_file_paths_from_config_table_filter_staff_id(self, config_table, staff_id):
        """
        根据staff_id查询其在配置文件列表中负责的文件
        """
        file_paths = []

        c = self.conn.cursor()
        stmt = "SELECT PROJECT_GROUP_NAME FROM " + DBWrapper.STAFF + " WHERE ID == " + str(staff_id)+ ";"
        c.execute(stmt)
        row = c.fetchone()
        if row:
            ss = ','.join("'" + x + "'" for x in row[0].split(";"))
            stmt = "SELECT * FROM " + config_table + " WHERE PROJECT_GROUP_NAME IN (" + ss + ");"
            c.execute(stmt)
            fetch = c.fetchmany
            while True:
                rows = fetch(1000)
                if not rows:
                    break
                for row in rows:
                    file_paths.append(row[0])
        c.close()
        return file_paths

    def get_version_all_file_list(self, version_id):
        """
        获取某版本的所有文件及其hash值
        [IN]
        version_id
        [OUT]
        version_file_list - {filepath, {HASH,FILESIZE,STATE}}
        """
        version_file_list = []
        (version_path, root_version_id) = self.get_version_tree_to_root(version_id)
        current_version_id = root_version_id

        while True:
            if current_version_id != version_id:
                current_version_file_list = self.get_version_detail_table(current_version_id)
                self.combine_version_file_list(version_file_list, current_version_file_list)
                current_version_id = version_path[current_version_id]
            else:
                current_version_file_list = self.get_version_detail_table(current_version_id)
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
                if file_list2[key][DBWrapper.VERSION_DETAIL_STATE] == DBWrapper.FILE_MOD:  # 文件为修改，则替换之
                    file_list1[key][DBWrapper.VERSION_DETAIL_HASH] = file_list2[key][DBWrapper.VERSION_DETAIL_HASH]
                    file_list1[key][DBWrapper.VERSION_DETAIL_FILESIZE] = file_list2[key][DBWrapper.VERSION_DETAIL_FILESIZE]
                elif file_list2[key][DBWrapper.VERSION_DETAIL_STATE] == DBWrapper.FILE_DEL:  # 文件为删除，则删除之
                    file_list1.pop(key)
            else:   # 文件为新加，则添加之
                if file_list2[key][DBWrapper.VERSION_DETAIL_STATE] == DBWrapper.FILE_ADD:
                    file_list1[key] = file_list2[key]

    def get_version_tree_to_root(self, version_id):
        """
        给定版本号，返回从最开始的根节点到该版本节点的路径
        [IN]
        version_id - int 版本号
        [OUT]
        从根节点到该版本节点的路径{parent_verison,child_version}
        根节点 root_version
        """
        version_path = {}
        version_info = self.get_one_version_info(version_id)
        while version_info:
            if version_info[DBWrapper.VERSION_LIST_PARENT_VER_ID]:
                parent_id = int(version_info[DBWrapper.VERSION_LIST_PARENT_VER_ID])
                version_path[parent_id] = version_id
                version_id = parent_id
                version_info = self.get_one_version_info(version_id)
            else:       # 当parent_id为空的时候，表示找到根节点了
                return (version_path, version_id)
        return None     # 如果某个版本的version_info找不到，则表示出错了，返回None

    def create_new_version_from_file_list(self, parent_version_id, mod_file_list, add_file_list, del_file_list, staff_id, description):
        """
        创建父版本的子版本
        [IN]
        parent_version_id - int 父版本号
        mod_file_list - 被修改的文件列表{FILEPATH : {VERSION_DETAIL_HASH, VERSION_DETAIL_FILESIZE}}
        add_file_list - 被添加的文件列表{FILEPATH : {HASH, FILESIZE, PROJECT_GROUP_NAME}}
        del_file_list - 待删除文件列表[FILEPATH]
        staff_id - int 用户ID
        description - str 版本描述
        [OUT]
        new_config_id - 如果有必要形成新的配置表，则返回新的配置表ID
        """

        if parent_version_id:
            # 先获得父版本的版本表ID
            parent_version_info = self.get_one_version_info(parent_version_id)
            if parent_version_info:
                # 获得父版本配置表的文件列表
                config_id = parent_version_info[DBWrapper.VERSION_LIST_CONFIG_TABLE_ID]
                config_info = self.get_config_table(config_id)

                version_detail = {}     # 版本信息表
                for filepath in mod_file_list:
                    if filepath in config_info:
                        version_detail[filepath] = {
                            DBWrapper.VERSION_DETAIL_HASH : mod_file_list[filepath][DBWrapper.VERSION_DETAIL_HASH],
                            DBWrapper.VERSION_DETAIL_FILESIZE : mod_file_list[filepath][DBWrapper.VERSION_DETAIL_FILESIZE],
                            DBWrapper.VERSION_DETAIL_STATE : DBWrapper.FILE_MOD
                        }
                
                for filepath in add_file_list:
                    if filepath not in config_info:
                        version_detail[filepath] = {
                            DBWrapper.VERSION_DETAIL_HASH : add_file_list[filepath][DBWrapper.VERSION_DETAIL_HASH],
                            DBWrapper.VERSION_DETAIL_FILESIZE : add_file_list[filepath][DBWrapper.VERSION_DETAIL_FILESIZE],
                            DBWrapper.VERSION_DETAIL_STATE : DBWrapper.FILE_ADD
                        }

                for filepath in del_file_list:
                    if filepath in config_info:
                        version_detail[filepath] = {
                            DBWrapper.VERSION_DETAIL_HASH : del_file_list[filepath][DBWrapper.VERSION_DETAIL_HASH],
                            DBWrapper.VERSION_DETAIL_FILESIZE : del_file_list[filepath][DBWrapper.VERSION_DETAIL_FILESIZE],
                            DBWrapper.VERSION_DETAIL_STATE : DBWrapper.FILE_DEL
                        }

                # 如果存在添加文件和删除文件，就要新建配置文件了
                if add_file_list or del_file_list:
                    new_config_info = config_info

                    for filepath in add_file_list:
                        if filepath not in new_config_info:
                            new_config_info[filepath] = {
                                DBWrapper.CONFIG_HASH : add_file_list[filepath][DBWrapper.VERSION_DETAIL_HASH],
                                DBWrapper.CONFIG_FILESIZE : add_file_list[filepath][DBWrapper.VERSION_DETAIL_FILESIZE],
                                DBWrapper.CONFIG_PROJECT_GROUP_NAME : add_file_list[filepath][DBWrapper.CONFIG_PROJECT_GROUP_NAME]
                            }

                    for filepath in del_file_list:
                        if filepath in new_config_info:
                            new_config_info.pop(filepath)
                    
                    config_id = self.create_fill_config_table(staff_id, description, new_config_info)

                # 在版本列表中创建新的版本
                version_id = self.insert_to_verion_list_table(config_id, staff_id, parent_version_id, description)
                # 创建版本信息表
                self.create_fill_version_detail_table(version_id, version_detail)

                return (True, version_id)

            else:
                return (False, None)
        else:  # 没有父版本则全是添加文件
            version_detail = {}     # 版本信息表
            new_config_info = {}        # 配置表

            for filepath in add_file_list:
                version_detail[filepath] = {
                    DBWrapper.VERSION_DETAIL_HASH : add_file_list[filepath][DBWrapper.VERSION_DETAIL_HASH],
                    DBWrapper.VERSION_DETAIL_FILESIZE : add_file_list[filepath][DBWrapper.VERSION_DETAIL_FILESIZE],
                    DBWrapper.VERSION_DETAIL_STATE : DBWrapper.FILE_ADD
                }
                new_config_info[filepath] = {
                    DBWrapper.CONFIG_HASH : add_file_list[filepath][DBWrapper.VERSION_DETAIL_HASH],
                    DBWrapper.CONFIG_FILESIZE : add_file_list[filepath][DBWrapper.VERSION_DETAIL_FILESIZE],
                    DBWrapper.CONFIG_PROJECT_GROUP_NAME : add_file_list[filepath][DBWrapper.CONFIG_PROJECT_GROUP_NAME]
                }
            config_id = self.create_fill_config_table(staff_id, description, new_config_info)
            # 在版本列表中创建新的版本
            version_id = self.insert_to_verion_list_table(config_id, staff_id, parent_version_id, description)
            # 创建版本信息表
            self.create_fill_version_detail_table(version_id, version_detail)
            return (True, version_id)

def populate_db(dbname):
    """
    生成一个数据库
    """
    db = DBWrapper(dbname)
    # 创建版本列表
    db.create_version_list_table()
    ver1_id = db.insert_to_verion_list_table(1, 1, None, "版本1：配置表ID=1，用户ID=1，父版本ID为空")
    ver2_id = db.insert_to_verion_list_table(1, 2, 1, "版本2：配置表ID=1，用户ID=2，父版本ID为1")
    ver3_id = db.insert_to_verion_list_table(2, 2, 2, "版本3：配置表ID=2，用户ID=2，父版本ID为2")
    ver4_id = db.insert_to_verion_list_table(2, 3, 2, "版本4：配置表ID=2，用户ID=3，父版本ID为2")
    print db.get_version_hierachy()
    print db.get_one_version_info(ver1_id)

    # 创建配置创建记录表
    db.create_config_create_log_table()
    config1_id = db.insert_to_config_create_log_table(1, "用户1创建的配置表1")
    config2_id = db.insert_to_config_create_log_table(2, "用户2创建的配置表2")
    print db.get_config_create_log_table()

    # 创建配置1
    db.create_config_table(config1_id)
    db.insert_to_config_table(config1_id, "1/1", "adssadsa", 4567, "建模项目组")
    db.insert_to_config_table(config1_id, "1/2", "hnjkhnjkadsa", 45679, "建模项目组")
    print db.get_config_table(config1_id)

    # 创建版本详细信息
    db.create_version_detail_table(ver1_id)
    db.insert_version_table(ver1_id, "1/1", "hashvalue", 123, DBWrapper.FILE_ADD)
    db.insert_version_table(ver1_id, "1/2", "hashvalue", 123, DBWrapper.FILE_ADD)
    print db.get_version_detail_table(ver1_id)

    # 快捷创建一个版本
    db.create_new_version_from_file_list(
        1,   # 父版本号是1
        {
            "1/1" : {
            DBWrapper.VERSION_DETAIL_HASH : "newhashvalue",
            DBWrapper.VERSION_DETAIL_FILESIZE : 432
            }
        },    # mod_file_list
        {
            "3/1" : {
                DBWrapper.VERSION_DETAIL_HASH : "newnewhashvalue",
                DBWrapper.VERSION_DETAIL_FILESIZE : 498765,
                DBWrapper.CONFIG_PROJECT_GROUP_NAME : "分析项目组"
            }
        },      # add_file_list
        [
            "1/2"
        ],   # del_file_list
        4, # staff_id
        "这是通用版本创建接口"        # description
    )
    
if __name__ == '__main__':

    # 生成数据库
    populate_db(dbpath)

    # 连接数据库
    # db = DBWrapper("test.db")
    # print db.get_config_table("1")
    #db.create_version_list_table()
    #db.create_project_group_permission_table()
    #db.create_staff_table()
    #db.create_config_create_log_table()
    #db.create_config_table("abc")
    #db.create_version_detail_table(1)

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
    #filepaths = db.get_file_paths_from_config_table_filter_staff_id("abc", 1);
    #print filepaths


    print "end"
