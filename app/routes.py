# основной скрипт, организующий логику переходов по страницам, а также саму логику страниц
# -*- coding: utf-8 -*-
from app import app
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app.models import User
from app.forms import LoginForm
from app.forms import RegistrationForm
from app import db


@app.route('/')
# описываем основную страницу приложения
@app.route('/index')
# делаем страницу недоступной, для невошедших пользовтелей
@login_required
def index():
    # список сообщений, которые есть в блоге. В дальнейшем будет изменено на список сообщений из бд
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        },
        {
            'author': {'username': 'Ипполит'},
            'body': 'Какая гадость эта ваша заливная рыба!!'
        }
    ]
    # рендерим страницу
    return render_template('index.html', title='Home', posts=posts)


# описание страницы входа в систему
# указываем, что используются GET, POST методы для работы страницы
@app.route('/login', methods=['GET', 'POST'])
def login():
    # проверка, вошел ли текущий пользователь в приложение
    # если да, то ему становится доступна основная старница /index и он туда перенаправляется
    if current_user.is_authenticated:
        return redirect('/index')
    # создаем экземпляр формы входа в систему из app.forms
    form = LoginForm()
    # проверка, была ли нажата кнопка подтверждения на форме
    if form.validate_on_submit():
        # проверяем, существует ли такой пользователь в базе данных
        user = User.query.filter_by(username=form.username.data).first()
        # если проверка провалилась или пароль введен неверно, то снова просим ввести данные для входа в систему
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect('/login')
        # если проверка на имя пользователя и пароль прошла, то позволяем пользователю войти в систему
        login_user(user, remember=form.remember_me.data)
        # не очень понятный момент, тк не работает правильно метод url_for('/index')
        # данный метод должен был автоматически подставлять ссылку на страницу
        # соответственно, next_page должен был автоматически подставлять ссылку для перехода на слдующую страницу
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = '/index'
        return redirect(next_page)
    # рендерим страницу входа в систему
    return render_template('login.html', title='Sign In', form=form)


# описание страницы для приветствия на разных языках
@app.route('/say_hello')
def say_hello():
    english_hello = "Hello, world!"
    russian_hello = "Привет, мир!"
    return render_template('say_hello.html', title='Say Hello', english_hello=english_hello, russian_hello=russian_hello)


# описание ссылки на выход пользователя из системы
@app.route('/logout')
def logout():
    # данная страница становится доступна, если пользователь уже вошел в систему
    # в шапке страницы появляется кнопка выхода
    logout_user()
    return redirect('/index')


# описание ссылки на старницу регистарции нового пользователя
# также используюся методы GET, POST
@app.route('/register', methods=['GET', 'POST'])
def register():
    # проверка, что текущий пользователь вошел в систему
    if current_user.is_authenticated:
        return redirect('/index')
    # создание экземпляра формы регистрации из app.forms
    form = RegistrationForm()
    # проверяем, что была нажата кнопка подтверждения на формк
    if form.validate_on_submit():
        # создаем нового пользователя, используя данные из полей формы
        user = User(username=form.username.data, email=form.email.data)
        # задаем пользователю пароль, который он указал
        user.set_password(form.password.data)
        # добавляем нового пользователя в базу данных
        db.session.add(user)
        # подтверждаем изменения в базе данных
        db.session.commit()
        # показываем сообщение пользователю, что он зарегистрирован в системе
        flash('Congratulations, you are now a registered user!')
        # возвращам пользователя на страницу входа, чтобы он вошел в систему
        return redirect('/login')
    # рендерим страницу с решистрационной формой
    return render_template('register.html', title='Register', form=form)


# описание сссылки на страницу профиля пользователя
@app.route('/user/<username>')
# страница доступна только для авторизированных пользователей
@login_required
def user(username):
    # загрудаем пользователя из базы данных с помощью запроса по имени пользователя
    # метод first_or_404() работает также, как метод first(), когда есть результаты
    # но в случае их отстуствия возвращает ошибку 404
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)