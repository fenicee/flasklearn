import sqlite3

import click
#g 是一个特殊对象，独立于每一个请求。在处理请求过程中，它可以用于储存 可能多个函数都会用到的数据。
# 把连接储存于其中，可以多次使用，而不用在同一个 请求中每次调用 get_db 时都创建一个新的连接。
#current_app 是另一个特殊对象，该对象指向处理请求的 Flask 应用。
# 这里 使用了应用工厂，那么在其余的代码中就不会出现应用对象。
# 当应用创建后，在处理 一个请求时， get_db 会被调用。这样就需要使用 current_app 。
from flask import current_app,g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db =sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e = None):
    db = g.pop('db',None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# click.command() 定义一个名为 init-db 命令行，它调用 init_db 函数，并为用户显示一个成功的消息。
# 更多关于如何写命令行的内容请参阅 doc:/cli 。
@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database')

# close_db 和 init_dbit_db_command 函数需要在应用实例中注册，否则无法使用。
# 然而，既然我们使用了工厂函数，那么在写函数的时候应用实例还无法使用。
# 代替地， 我们写一个函数，把应用作为参数，在函数中进行注册。
def init_app(app):
    #app.teardown_appcontext() 告诉 Flask 在返回响应后进行清理的时候调用此函数
    app.teardown_appcontext(close_db)
    #app.cli.add_command() 添加一个新的 可以与 flask 一起工作的命令。
    # 在工厂中导入并调用这个函数。在工厂函数中把新的代码放到 函数的尾部，返回应用代码的前面。
    app.cli.add_command(init_db_command)
