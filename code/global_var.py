# coding=utf-8 
import web

render = web.template.render('templates/')
host = "localhost"
port = "8080"
url = host + ":" + port
dbname = "../workdir/test.db"