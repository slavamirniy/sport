from flask import Flask
from flask_restful import Api
from posts import Post, PostsQuery
from users import Auth, Register, Users, initDB

app = Flask(__name__)
api = Api(app)
app.config['CORS_HEADERS'] = 'Content-Type'

api.add_resource(Auth, '/auth')
api.add_resource(Register, '/register')
api.add_resource(Users, '/users/<int:id>')
api.add_resource(PostsQuery, '/posts', endpoint = 'posts')

if __name__ == '__main__':
    initDB()
    app.run(debug=True, port = 30)
