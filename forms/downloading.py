from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired
from sqlalchemy_serializer import SerializerMixin


class AddForm(FlaskForm, SerializerMixin):
    title = StringField('Название песни', validators=[DataRequired()])
    artist = StringField("Исполнитель(если поле пустое: Неизвестен)")
    album = StringField("Альбом(если поле пустое: Сингл)")
    path = FileField("Файл с песней", validators=[FileRequired()])
    submit = SubmitField('Загрузить')