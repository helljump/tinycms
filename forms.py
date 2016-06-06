from datetime import datetime

from flask_wtf import Form, RecaptchaField
from wtforms import StringField, TextAreaField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, Length


class ContactForm(Form):
    name = StringField('Имя', validators=[DataRequired()])
    text = TextAreaField('Сообщение', validators=[Length(min=2, max=2000)])
    recaptcha = RecaptchaField('А Вы не робот?')


class LoginForm(Form):
    name = StringField('user', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])


class EditForm(Form):
    title = StringField('Заголовок', validators=[DataRequired()])
    intro = TextAreaField('Интро', validators=[DataRequired()])
    text = TextAreaField('Текст')
    date = DateTimeField('Дата', default=datetime.now, validators=[DataRequired()])
    published = BooleanField('Опубликовано', default=True)
    description = StringField('Описание')
    keywords = StringField('Ключевые слова')
