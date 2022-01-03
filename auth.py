import functools

from flask import (
    Blueprint,flash,g,redirect,render_template,request,session,url_for
)
from werkzeug.security import check_password_hash,generate_password_hash

from db import get_db
bp = Blueprint('auth',__name__,url_prefix='/auth')

@bp.route('/register',methods=('GET','POST'))
def register():
    if request.method == 'POST':
        username =request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = '请填写用户名'
        elif not password:
            error = '请填写密码'

        if error is None:
            try:
                db.execute(
                     "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
        flash(error)
    return render_template('auth/register.html')

@bp.route('/login',methods=('GET','POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?',(username,)
        ).fetchone()
        if user is None:
            error = '用户名不存在 '
        elif not check_password_hash(user['password'],password):
            error = '密码不对'
        if error is None:
            session.clear()
            session['user_id'] = user ['id']
            return  redirect(url_for('index'))
        flash(error)
    return render_template('auth/login.html')
#现在用户的 id 已被储存在 session 中，可以被后续的请求使用。
# 请每个请求的开头，如果用户已登录，那么其用户信息应当被载入，以使其可用于 其他视图。
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?',(user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#用户登录以后才能创建、编辑和删除博客帖子。在每个视图中可以使用 装饰器 来完成这个工作。
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view