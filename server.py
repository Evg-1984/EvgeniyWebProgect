from flask import Flask, render_template, make_response, request, session, redirect, jsonify, send_file
from data import db_session
from data.users import User
from data.music import Audio
from forms.user import RegisterForm, LoginForm
import datetime
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_restful import reqparse, abort, Api, Resource
from blueprints import music_api
from io import BytesIO


app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


from flask import make_response


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


class AudioResource(Resource):
    def get(self, file_id):
        abort_if_file_not_found(file_id)
        session = db_session.create_session()
        music = session.query(Audio).get(file_id)
        return jsonify({'music': music.to_dict(
            only=('title', 'content', 'user_id', 'is_private'))})


class AudioListResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('title', required=True)
        self.parser.add_argument('content', required=True)
        self.parser.add_argument('is_published', required=True, type=bool)
        self.parser.add_argument('user_id', required=True, type=int)

    def post(self):
        args = self.parser.parse_args()
        session = db_session.create_session()
        music = Audio(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            is_published=args['is_published']
        )
        session.add(music)
        session.commit()
        return jsonify({'id': music.id})


def abort_if_file_not_found(file_id):
    session = db_session.create_session()
    music = session.query(Audio).get(file_id)
    if not music:
        abort(404, message=f"File {file_id} not found")


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


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(Audio)
    return render_template("index.html", news=news)


@app.route("/play/<int:audio_id>")
def play(audio_id):
    db_sess = db_session.create_session()
    audio = db_sess.query(Audio).get(audio_id)
    return send_file(
        BytesIO(audio.audio_data),
        mimetype="audio/mpeg",
        as_attachment=False
    )



def main():
    db_session.global_init("db/blogs.db")
    db_sess = db_session.create_session()
    # user = db_sess.query(User).filter(User.id == 1).first()
    # with open('Finntroll_-_Bakom_Varje_Fura_47889511.mp3', 'rb') as f:
    #     mp3_data = f.read()
    #
    # audio = Audio(
    #     title="Bakom Varje Fura",
    #     content=mp3_data,
    #     album="Bakom Varje Fura",
    #     artist="Fintroll",
    #     user=user
    # )
    # db_sess.add(audio)
    # db_sess.commit()
    api.add_resource(AudioListResource, '/api/v2/music')
    api.add_resource(AudioResource, '/api/v2/music/<int:news_id>')
    app.register_blueprint(music_api.blueprint)
    app.run()


if __name__ == '__main__':
    main()