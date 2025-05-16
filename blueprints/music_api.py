import flask

from flask import jsonify, make_response, request
from data import db_session
from data.music import Audio

blueprint = flask.Blueprint(
    'music_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/music')
def get_music():
    db_sess = db_session.create_session()
    music = db_sess.query(Audio).all()
    return jsonify(
        {
            'music':
                [item.to_dict(only=('title', 'content', 'user.name'))
                 for item in music]
        }
    )


@blueprint.route('/api/music/<int:music_id>', methods=['GET'])
def get_one_news(music_id):
    db_sess = db_session.create_session()
    music = db_sess.query(Audio).get(music_id)
    if not music:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'music': music.to_dict(only=(
                'title', 'content', 'user_id'))
        }
    )


@blueprint.route('/api/music', methods=['POST'])
def add_music():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['title', 'content', 'user_id']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    music = Audio(
        title=request.json['title'],
        content=request.json['content'],
        user_id=request.json['user_id']
    )
    db_sess.add(music)
    db_sess.commit()
    return jsonify({'id': music.id})