# 一个 Flask 应用是一个 Flask 类的实例。应用的所有东西（例如配置 和 URL ）都会和这个实例一起注册。
# 创建一个 Flask 应用最粗暴直接的方法是在代码的最开始创建一个全局 Flask 实例。前面的 “Hello, World!”
# 示例就是这样做的。有的情况 下这样做是简单和有效的，但是当项目越来越大的时候就会有些力不从心了。
# 可以在一个函数内部创建 Flask 实例来代替创建全局实例。这个函数被 称为 应用工厂 。
# 所有应用相关的配置、注册和其他设置都会在函数内部完成， 然后返回这个应用。
# 创建 flaskr 文件夹并且文件夹内添加 __init__.py 文件。
# __init__.py 有两个作用：一是包含应用工厂；
# 二 是告诉 Python flaskr 文件夹应当视作为一个包。
import os
from flask import Flask

import blog
import db
import auth


def create_app(test_config=None):
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE= 'identifier.sqlite',
    )
    @app.route('/hello')
    def hello():
        return 'Hello,World!'


    db.init_app(app)
    #使用 app.register_blueprint() 导入并注册 蓝图。新的代码放在工厂函数的尾部返回应用之前。
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.add_url_rule('/',endpoint='index')
    return app

