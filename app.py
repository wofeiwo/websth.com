#!/usr/bin/python
#coding=utf-8

# imports
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.contrib.cache import FileSystemCache

app = Flask(__name__)
app.config.from_object('config.config.DevelopmentConfig') # 导入所有配置，后续都需要用app.config['key']获取。
# app.config.from_object('config.config.ProductionConfig') # 导入所有配置，后续都需要用app.config['key']获取。
app.config.from_envvar('WEBSTH_CONFIG', silent = True) # 如果有环境变量，就导入此文件覆盖相应设置。
db = SQLAlchemy(app)
cache = FileSystemCache(app.config['CACHE_PATH'])

# import views
from views import *

# 开发环境运行部分，开始运行程序
if __name__ == '__main__':
    app.run()