# скрипт моделей, которые присутствуют в приложении
from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5

# создаем новую таблицу в бд, в которой будут храниться ассоциации подписанных пользователей
# (id пользователя -> id на кого подписан)
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


# класс, описывающий модель Пользователь
class User(UserMixin, db.Model):
    # описание полей в таблице базы данных
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    # вместо пароля в чистом виде храним его хэш, который потом декодируется. Так безопаснее.
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # добавлены 2 новых поля в базе данных
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    # обьявляем вид отношения в таблице
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

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

    # реализация метода "подписки" на другого пользователя
    def follow(self, user):
        # если не подписаны, то подписываемся
        if not self.is_following(user):
            self.followed.append(user)

    # реализация метода "отписки" от пользователя
    def unfollow(self, user):
        # если подписаны, то отписываемся
        if self.is_following(user):
            self.followed.remove(user)

    # проверяем, подписаны ли на пользователя
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    # возвращаем список сообщений отслеживаемых пользователей
    def followed_posts(self):
        # создаем временную таблицу(join) со списком всех сообщений всех отслеживаемых пользователей;
        # сортируем временную таблицу, сохраняя в ней только записи пользователей, на которых мы подписаны
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        # создаем список наших постов
        own = Post.query.filter_by(user_id=self.id)
        # обьединяем временную таблицу сообщений и список наших постов, а потом сортируем его по времени
        return followed.union(own).order_by(Post.timestamp.desc())


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
