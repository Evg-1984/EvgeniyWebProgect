import flask

from flask import jsonify
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