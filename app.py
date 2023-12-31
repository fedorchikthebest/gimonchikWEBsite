from flask import Flask, render_template, request, redirect, abort, flash
from data import db_session
from functions import *
from data.posts import Post
from data.data_api import SaveData
import json
import os
import logging
from flask import make_response
from datetime import datetime
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

logging.basicConfig(filename='logs/logs.log', level=logging.DEBUG)

loggined_ip = load_ip()
UPLOAD_TEMPLATES = './templates/loaded_templates'
UPLOAD_AVATARS = './static/loaded_avatars'
app.config['SECRET_KEY'] = 'awfawfawfawf4a34DWDefsae'
bad_list = {}


@app.errorhandler(404)
def handle_exception(e):
    if request.remote_addr in bad_list.keys():
        print(bad_list.keys())
        if bad_list[request.remote_addr][1] != 1:
            bad_list[request.remote_addr][1] += 1
            return f'Ошибка {e}'
        req_date = datetime.now()
        if (req_date - bad_list[request.remote_addr][0]).total_seconds() < 1:
            res = make_response(redirect('/'))
            res.set_cookie('gimonchiks/banned', 'yes', max_age=60 * 60 * 24 * 365 * 2)
            with open('banned_ips.json') as f:
                ips = json.load(f)
            ips['ips'].append(request.remote_addr)
            with open('banned_ips.json', 'w') as f:
                json.dump(ips, f)
            del bad_list[request.remote_addr]
            app.logger.info(f'{request.remote_addr} забанен!')
            return res
        bad_list[request.remote_addr] = [datetime.now(), 0]
    bad_list.update({request.remote_addr: [datetime.now(), 0]})
    return f'Ошибка {e}'


@app.before_request
def before_request():
    if request.remote_addr == loggined_ip:
        return
    if not request.cookies.get('test'):
        res = make_response(redirect(request.path))
        res.set_cookie('test', 'yes', max_age=60 * 60 * 24 * 365 * 2)
        return res
    with open('banned_ips.json') as f:
        bans = json.load(f)
    if request.cookies.get('gimonchiks/banned') == 'yes' or request.remote_addr in bans['ips']:
        res = make_response(render_template('ban_page.html'))
        res.set_cookie('gimonchiks/banned', 'yes', max_age=60 * 60 * 24 * 365 * 2)
        if request.remote_addr not in bans['ips']:
            with open('banned_ips.json', 'w') as f:
                print(bans)
                bans['ips'].append(request.remote_addr)
                json.dump(bans, f)
        return res


@app.route('/', methods=['GET', 'POST'])
def index():
    db_sess = db_session.create_session()
    posts = db_sess.query(Post)
    db_sess.close()
    return render_template("index.html", title="Главная",
                           loggined=loggined_ip == request.remote_addr, posts=posts[::-1])


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST' and loggined_ip == request.remote_addr:

        files = request.files.getlist("file")

        for file in files:
            file.save(f'./static/loaded_sources/{file.filename}')
        return redirect('/')


@app.route('/login', methods=['POST', 'GET'])
def login():
    global loggined_ip
    if request.method == 'POST':
        if check_key(request.form.get('key')):
            update_ip(request.remote_addr)
            loggined_ip = request.remote_addr
            return redirect('/')
    return render_template('login.html', title="login", autorised=loggined_ip == request.remote_addr)


@app.route('/add_post', methods=['POST', 'GET'])
def add_post():
    global loggined_ip
    if request.remote_addr != loggined_ip:
        return redirect('/')
    if request.method == 'POST':
        avatar = request.files.get('avatar')
        html = request.files.get('html')
        if not avatar.filename or not html.filename or not request.form.get('title'):
            flash('Не все поля заполнены')
            return redirect(request.url)
        avatar_name = gen_filename(request, 'avatar')
        html_name = gen_filename(request, 'html')
        avatar.save(os.path.join(UPLOAD_AVATARS, avatar_name))
        html.save(os.path.join(UPLOAD_TEMPLATES, html_name))
        post = Post(
            title=request.form.get('title'),
            content=html_name,
            avatar=avatar_name
        )
        db_sess = db_session.create_session()
        db_sess.add(post)
        db_sess.commit()
        db_sess.close()
        return redirect('/')
    return render_template('add_post.html', title="Добавление поста", loggined=loggined_ip == request.remote_addr)


@app.route('/post/<string:id>', methods=['GET', 'POST'])
def render_post(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == id).first()
    db_sess.close()
    if not post:
        return abort(404)
    return render_template(f'./loaded_templates/{post.content}', title=post.title, loggined=loggined_ip == request.remote_addr)


@app.route('/delete_post/<string:id>', methods=['GET', 'POST'])
def delete_post(id):
    if loggined_ip != request.remote_addr:
        return abort(404)
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == id).first()
    if post:
        os.remove(os.path.join(UPLOAD_TEMPLATES, post.content))
        os.remove(os.path.join(UPLOAD_AVATARS, post.avatar))
        db_sess.delete(post)
        db_sess.commit()
    db_sess.close()
    return redirect('/')


@app.route('/api/data_saving/<string:id>', methods=['POST', 'GET'])
def api_data(id):
    db_sess = db_session.create_session()
    if request.method == 'POST':
        req = request.get_json()
        print(req)
        if not check_key(req.get('key')) and loggined_ip != request.remote_addr:
            return 'ERROR'
        if req.get('type') == 'write_data':
            if db_sess.query(SaveData).filter(SaveData.id == id).first() is None:
                api_data = SaveData(
                    id=id,
                    data=str(req.get('data'))
                )
                db_sess.add(api_data)
            else:
                api_data = db_sess.query(SaveData).filter(SaveData.id == id).first()
                api_data.data = str(req.get('data'))
            db_sess.commit()
            db_sess.close()
        if req.get('type') == 'delete_data':
            api_data = db_sess.query(SaveData).filter(SaveData.id == id).first()
            db_sess.delete(api_data)
            db_sess.commit()
            db_sess.close()
        return "OK"
    api_data = db_sess.query(SaveData).filter(SaveData.id == id).first()
    db_sess.close()
    return api_data.data if api_data is not None else abort(404)


@app.route('/edit_post/<string:id>', methods=['GET', 'POST'])
def edit_post(id):
    if loggined_ip != request.remote_addr:
        return abort(404)
    if request.method == 'POST':
        db_sess = db_session.create_session()
        post = db_sess.query(Post).filter(Post.id == id).first()
        if post:
            avatar = request.files.get('avatar')
            html = request.files.get('html')
            if avatar.filename:
                avatar_name = gen_filename(request, 'avatar')
                os.remove(os.path.join(UPLOAD_AVATARS, post.avatar))
                avatar.save(os.path.join(UPLOAD_AVATARS, avatar_name))
                post.avatar = avatar_name
            if html.filename:
                html_name = gen_filename(request, 'html')
                os.remove(os.path.join(UPLOAD_TEMPLATES, post.content))
                html.save(os.path.join(UPLOAD_TEMPLATES, html_name))
                post.content = html_name
            if request.form.get('title'):
                post.title = request.form.get('title')
            db_sess.commit()
        db_sess.close()
        return redirect('/')
    return render_template('add_post.html', title=f'Редактировать пост №{id}')


@app.route('/about')
def render_about():
    return render_template('about.html', title="О сайте", loggined=loggined_ip == request.remote_addr)


if __name__ == '__main__':
    db_session.global_init("db/posts.db")
    app.run(host='0.0.0.0', port=80)
