from flask import Flask, render_template, request, make_response, session, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import redirect
from flask import make_response
from flask_restful import reqparse, abort, Api, Resource
import datetime
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired

from data import db_session
from data.music import Audio
from data.user import User

app = Flask(__name__)
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('is_published', required=True, type=bool)
parser.add_argument('album_id', required=True, type=int)
parser.add_argument('user_id', required=True, type=int)

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)

def abort_if_audiofile_not_found(file_id):
    session = db_session.create_session()
    audio = session.query(Audio).get(file_id)
    if not audio:
        abort(404, message=f"Audiofile {file_id} not found")


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class AudioResource(Resource):
    def get(self, file_id):
        abort_if_audiofile_not_found(file_id)
        session = db_session.create_session()
        audio = session.query(Audio).get(file_id)
        return jsonify({'news': audio.to_dict(
            only=('title', 'content', 'user_id', 'album_id', 'is_published'))})

    def delete(self, file_id):
        abort_if_audiofile_not_found(file_id)
        session = db_session.create_session()
        audio = session.query(Audio).get(file_id)
        session.delete(audio)
        session.commit()
        return jsonify({'success': 'OK'})


class AudioListResource(Resource):
    def get(self):
        session = db_session.create_session()
        audio = session.query(Audio).all()
        return jsonify({'news': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in audio]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        audio = Audio(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            is_published=args['is_published'],
            album_id=args['album_id']
        )
        session.add(audio)
        session.commit()
        return jsonify({'id': audio.id})


def main():
    app.run()


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


if __name__ == '__main__':
    main()