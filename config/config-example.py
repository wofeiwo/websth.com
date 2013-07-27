#coding=utf-8

class Config:
    # app config
    DEBUG                       = False
    SECRET_KEY                  = 'sfjoweoc!@#$0g2@#23x23'
    SESSION_COOKIE_NAME         = 'websth'
    SESSION_COOKIE_HTTPONLY     = True
    PAGE_SIZE                   = 20
    CACHE_PATH                  = './temp/'
    SQL_CACHE_TIMEOUT           = 60 # 1分钟

    # db config
    SQLALCHEMY_DATABASE_URI     = 'mysql://root:@127.0.0.1:3306/websth?charset=utf8'
    SQLALCHEMY_ECHO             = False
    SQLALCHEMY_POOL_SIZE        = 10
    SQLALCHEMY_POOL_TIMEOUT     = 10

class DevelopmentConfig(Config):
    DEBUG                       = True
    SQLALCHEMY_ECHO             = True
    SQLALCHEMY_POOL_SIZE        = 2
    PAGE_SIZE                   = 20

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI     = 'mysql://root:root_password@127.0.0.1:3306/websth?charset=utf8'
    SQLALCHEMY_ECHO             = False
    SQLALCHEMY_POOL_RECYCLE     = 60 * 60 * 3 # 3小时
    USE_X_SENDFILE              = True
    SQL_CACHE_TIMEOUT           = 60 * 60 * 3 # 3小时