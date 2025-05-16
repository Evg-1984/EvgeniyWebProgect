from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField, FileField
from wtforms.validators import DataRequired
from sqlalchemy_serializer import SerializerMixin


class AddForm(FlaskForm, SerializerMixin):
    title = StringField('Название песни', validators=[DataRequired()])
    artist = StringField("Исполнитель(если поле пустое: Неизвестен)")
    album = StringField("Альбом(если поле пустое: Сингл)")
    audio_file = FileField("Файл с песней", validators=[DataRequired()])
    submit = SubmitField('Загрузить')