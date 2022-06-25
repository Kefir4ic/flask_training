# скрипт валидации (проверки правильности заполненности) форм
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


# валидация формы входа в систему
class LoginForm(FlaskForm):
    # проверяем заполнены ли поля в форме
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


# валидация формы регистрации
class RegistrationForm(FlaskForm):
    # проверяем, что поля формы заполнены
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    # проверяем, что повторный ввод пароля совпадает с первоначальным
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # проверка, что пользователя с таким именем еще нет в базе данных
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    # проверка, что пользователя с такой почтой еще нет в базе данных
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


# создание формы для редактирования профиля пользователя
class EditProfileForm(FlaskForm):
    # можем поменять имя пользователя
    username = StringField('Username', validators=[DataRequired()])
    # можем поменять  нформацию о пользователе
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    # проверяется, изменил ли пользователь свое имя при редактировании профиля
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')