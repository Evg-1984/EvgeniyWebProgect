from flask import Flask, render_template, request, make_response, session, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import redirect
from flask import make_response
from flask_restful import reqparse, abort, Api, Resource

from data import db_session
from data.music import Audio

app = Flask(__name__)
api = Api(app)


def abort_if_audiofile_not_found(file_id):
    session = db_session.create_session()
    audio = session.query(Audio).get(file_id)
    if not audio:
        abort(404, message=f"Audiofile {file_id} not found")





def main():
    app.run()


if __name__ == '__main__':
    main()