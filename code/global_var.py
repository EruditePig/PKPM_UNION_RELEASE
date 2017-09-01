# coding=utf-8 
import web
import sys
import os

# 渲染html
g_render = web.template.render('templates/')

# 当前session上传文件新建版本所需存的数据
g_new_version = {"files" : []}