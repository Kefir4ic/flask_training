# -*- coding: utf-8 -*-
from app import app
from flask import render_template, flash, redirect, url_for

from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Максим Тихомиров'}
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
    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)


@app.route('/say_hello')
def say_hello():
    english_hello = "Hello, world!"
    russian_hello = "Привет, мир!"
    return render_template('say_hello.html', title='Say Hello', english_hello=english_hello, russian_hello=russian_hello)
