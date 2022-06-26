# основной скрипт, организующий логику переходов по страницам, а также саму логику страниц
# -*- coding: utf-8 -*-
from app import app, db
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User, Post
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
# описываем основную страницу приложения
@app.route('/index', methods=['GET', 'POST'])
# делаем страницу недоступной, для невошедших пользовтелей
@login_required
def index():
    # создаем экземпляр формы для написания поста
    form = PostForm()
    # записываем информацию из формы в таблицу Post базы данных
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    # разбиваем домашнюю страницу на несколько, чтобы удобнее было просматривать большое кол-во соббщений в блоге
    page = request.args.get('page', 1, type=int)
    # список сообщений отслеживаемых пользователей, которые есть в блоге
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    # создание ссылки на следующие сообщения в блоге, если они есть
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    # создание ссылки на предыдущие сообщения в блоге, если они есть
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    # рендерим страницу
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


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
    return render_template('say_hello.html', title='Say Hello', english_hello=english_hello,
                           russian_hello=russian_hello)


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
    page = request.args.get('page', 1, type=int)
    # список всех постов владельца этой страницы
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    # ссылка на следующие сообщения владельца старинцы, если они есть
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    # ссылка на предыдущие посты владельца страницы, если они есть
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


# функция, которая записывает время последнего входа в систему пользователя
@app.before_request
def before_request():
    # проверяем, зарегистрирован ли текущий пользователь
    if current_user.is_authenticated:
        # устанавливаем текущее время в нужное поле
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


# функция для доступа к форме редактирования пользователя
@app.route('/edit_profile', methods=['GET', 'POST'])
# доступ только у вошедшего пользователя
@login_required
def edit_profile():
    # создает экземпляр формы
    form = EditProfileForm(current_user.username)
    # проверяем, нажата ли кнопка
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        # сохраняем изменения, выводим сообщение пользователю,
        # возвращаем пользователя на страницу редактирования профиля
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    # если метод нажатия кнопки вернул нам false,
    # на то могут быть 2 причины:
    # 1)браузер отправил GET запрос и нужно что-то ответить(вернуть исходную версию шаблона)
    # 2)Браузер отправил POST запрос с данными формы, но что-то в них не так
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


# функция для доступа к добавлению пользователя в подписки
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))


# функция для доступа у удалению пользователя из подписок
@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))


# функция для доступа к странице с поиском новых пользователей
@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    # создание ссылки на следующие сообщения в блоге, если они есть
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    # создание ссылки на предыдущие сообщения в блоге, если они есть
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    # рендерим страницу
    return render_template('index.html', title='Home',
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)