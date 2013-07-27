#coding=utf-8
import os

def numCPUs():
    if not hasattr(os, "sysconf"):
        raise RuntimeError("No sysconf detected.")
    return os.sysconf("SC_NPROCESSORS_ONLN")

# 常规
bind                    = "127.0.0.1:5000"
user                    = 'www'
group                   = 'www'
#debug                  = True
daemon                  = True
pidfile                 = "/home/www/run/gunicorn.pid"
# accesslog               = "/home/www/logs/www.websth.com.access.log"
errorlog                = "/home/www/logs/www.websth.com.error.log"

# 性能
preload_app             = True
workers                 = numCPUs() * 2 + 1
backlog                 = 2048
#worker_class           ="sync"
worker_class            = "gevent"
limit_request_fields    = 200
keepalive               = 5
max_requests            = 10240 # 处理了这么多请求之后worker进程就会重启
