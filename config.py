# файл конфигурации приложения
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # настройка ссылки на базу данных, в которой хранятся данные пользователей и посты, написанные на сайте
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # количество постов, которые будут отображаться на страницах
    POSTS_PER_PAGE = 25