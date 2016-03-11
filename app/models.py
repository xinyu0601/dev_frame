# -*- coding: utf-8 -*-

'''
 基本模型类
'''
from app import db
from . import login_manager
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

# 用户角色
class Role(db.Model):

    __tablename__ = 'tb_roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return '<Role %r>' % self.name


# 基本用户类
class User(db.Model):

    __tablename__ = 'tb_user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('tb_roles.id'))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


# 开发者类
class Developer(db.Model):

    __tablename__ = 'tb_developer'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(20), default='')
    password = db.Column(db.String(20), default='')

    nickname = db.Column(db.String(20), default='')
    confirmed = db.Column(db.Boolean, default=False)

    sex = db.Column(db.Integer, default=1)
    qq = db.Column(db.String(60), default='')
    weibo = db.Column(db.String(60), default='')
    github = db.Column(db.String(200), default='')

    school = db.Column(db.String(30), default='')
    phone = db.Column(db.String(11), default='')
    email = db.Column(db.String(60), default='')
    description = db.Column(db.String(200), default='')
    hobby = db.Column(db.String(200), default='')
    info = db.Column(db.String(200), default='')
    degree = db.Column(db.String(10), default='')

    register_time = db.Column(db.DateTime, default=datetime.now())

    apps = db.relationship('App', backref='developer', lazy='dynamic')


    def __init__(self, **kwargs):
        super(Developer, self).__init__(**kwargs)


    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'confirm' : self.id})


    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True


    def verify_password(self, password):
        if self.password == password:
            return True
        else:
            return False


    def save(self):
        self.register_time = datetime.now()
        db.session.add(self)
        db.session.commit()


    def update(self, info):
        print info
        db.session.query(Developer).\
            filter_by(username=self.username).update(info)


     # 将数据转化为json格式
    def to_json(self):
        json_post = dict(username=self.username, nickname=self.nickname,
                         sex=self.sex, qq=self.qq, weibo=self.weibo, github=self.github,
                         school=self.school, phone=self.phone, hobby=self.hobby, info=self.info)
        return json_post


# App类
class App(db.Model):

    __tablename__ = 'tb_app'

    id = db.Column(db.Integer, primary_key=True)

    app_name = db.Column(db.String(20), unique=True)
    company = db.Column(db.String(20), default='')
    description = db.Column(db.String(200), default='')
    status = db.Column(db.Integer, default=0)
    platform = db.Column(db.Integer, default=0)
    developer_id = db.Column(db.Integer, db.ForeignKey('tb_developer.id'))
    create_time = db.Column(db.DateTime, default=datetime.now())


    def __init__(self, **kwargs):
        super(App, self).__init__(**kwargs)


    # 保存APP对象
    def save(self):
        self.create_time = datetime.now()
        # 默认设置为未审核
        self.status = 0;

        db.session.add(self)
        db.session.commit()


    def find(self, content):

        return db.session.query(content).filter(App.app_name.like(content)).\
            order_by(self.create_time.desc).all()


    # 将数据转化为json格式
    def to_json(self):
        json_post = dict(app_name=self.app_name, description=self.description,
                         status=self.status, company=self.company, create_time=self.create_time)
        return json_post
