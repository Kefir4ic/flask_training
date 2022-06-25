# скрипт моделей, которые присутствуют в приложении
from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5


# класс, описывающий модель Пользователь
class User(UserMixin, db.Model):
    # описание полей в таблице базы данных
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    # реализация метода для добавления аватаров на сайт с помощью инструмента Gravatar
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    # установление пароля пользователя
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # проверка пароля пользователя
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# класс, описывающий модель Пост
class Post(db.Model):
    # описание полей в таблице базы данных
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


# декоратор, позволяющий войти зарегистрированному(находящемуся в бд) пользователю в систему
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
