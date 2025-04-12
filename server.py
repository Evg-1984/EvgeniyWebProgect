from flask import Flask, render_template, request, make_response, session, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import redirect
from flask import make_response
from flask_restful import reqparse, abort, Api, Resource

from data import db_session
from data.music import Audio

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('is_published', required=True, type=bool)
parser.add_argument('album_id', required=True, type=int)
parser.add_argument('user_id', required=True, type=int)


def abort_if_audiofile_not_found(file_id):
    session = db_session.create_session()
    audio = session.query(Audio).get(file_id)
    if not audio:
        abort(404, message=f"Audiofile {file_id} not found")


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


if __name__ == '__main__':
    # для списка объектов
    api.add_resource(news_resources.AudioListResource, '/api/v2/news')
    # для одного объекта
    api.add_resource(audio_resources.AudioResource, '/api/v2/news/<int:news_id>')
    main()