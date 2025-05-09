import flask

from data import db_session
from data.music import Audio

blueprint = flask.Blueprint(
    'music_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/music')
def get_music():
    return "Обработчик в music_api"