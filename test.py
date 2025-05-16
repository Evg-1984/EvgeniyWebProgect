from requests import get

print(get('http://localhost:5000/api/music').json())

print(get('http://localhost:5000/api/music/1').json())

print(get('http://localhost:5000/api/music/999').json())
# новости с id = 999 нет в базе