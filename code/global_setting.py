# coding=utf-8 
import os
import sys
import web

# force stdout to stderr
# 把系统默认编码永久设置为utf8
reload(sys)
sys.setdefaultencoding('utf8')
sys.stdout = sys.stderr

# Add local directories to the system path
# include_dirs = [ 'lib', 'pages' ]
# for dirname in include_dirs:
#   sys.path.append( os.path.dirname(__file__) + '/' + dirname )

# Change to the directory this file is located in
os.chdir( os.path.dirname(__file__))

# Turn on/off debugging
web.config.debug = True



# 端口
port = "8080"

# 工作目录
module_path = sys.path[0]
work_path = os.path.abspath(os.path.join(module_path, '../workdir/'))

# 临时文件保存位置
temp_path = os.path.abspath(os.path.join(module_path, '../workdir/temp/'))

# 数据库路径
dbpath = work_path + "/test.db"

# 最终文件保存文件夹
save_file_path = os.path.abspath(os.path.join(module_path, '../workdir/index/'))