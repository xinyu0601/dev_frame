# -*- coding: utf-8 -*-
from flask import render_template, session, redirect, url_for, jsonify, request, current_app

from . import main
from app.models import App, Developer


# 开发者用户登陆
@main.route('/signin', methods=['GET', 'POST'])
def signin():

    if request.method == 'GET':
        return render_template('signin.html')

    email = request.form['email']
    password = request.form['password']

    if email.strip() == '' \
            or password.strip() == '':
        return jsonify({'status':401})

    if email.find("@") == -1:
        developer = Developer.query.filter_by(username=email).first()
    else:
        developer = Developer.query.filter_by(email=email).first()

    if developer is not None:
        if developer.verify_password(password):
            return jsonify({'status':200})
        else:
            return jsonify({'status':402})
    else:
        return jsonify({'status':403})


# 开发者用户注册
@main.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'GET':
        return render_template('signup.html')

    username    = request.form['username']
    password    = request.form['password']
    email       = request.form['email']
    repassword  = request.form['repassword']

    if username.strip() == '' or repassword.strip() == '' \
            or password.strip() == '' or email.strip() == '':
        return jsonify({'status':401})

    if repassword != password:
        return jsonify({'status':402})

    developer = Developer(username=username, password=password, email=email)

    try:
        developer.save()
    except Exception, e:
        print e

    return jsonify({'status' : 200})



# 获取用户创建的APP列表
@main.route('/app/list', methods=['GET'])
def apps():

    # 数据进行分页处理
    page = request.args.get('page', 1, type=int)
    pagination = App.query.order_by(App.create_time.desc()).paginate(page,
                            per_page=current_app.config['APP_LIST_PER_PAGE'], error_out=False)
    apps = pagination.items

    return render_template('app-list.html',
                           apps=apps, pagination=pagination, pageNum=pagination.pages)


# 用户创建APP
@main.route('/app/create', methods=['GET', 'POST'])
def new_app():

    if request.method == 'GET':
        return render_template('new-app.html')

    app_name = request.form['app_name']
    platform = request.form.get('app_usage', 1, type=int)
    description = request.form['description']
    company = request.form.get('company', '', type=str)

    if description.strip() == '' or app_name.strip() == '':
        return render_template('new-app.html', warning='')

    app = App(app_name=app_name, description=description,
              platform=platform, company=company)

    try:
        app.save()
    except Exception, e:
        print e

    return jsonify({'status':200, 'app':app.to_json()})


@main.route('/user/edit')
def edit_user():
    return render_template('edit-user.html')


@main.route('/user/modify')
def modify_password():
    return render_template('modify-password.html')


@main.route('/user/find-password')
def find_password():
    return render_template('find-password.html')


@main.route('/index')
def index():
    return render_template('index.html')