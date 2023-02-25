from flask_restful import Resource, reqparse
import utils
import sqlite3

from utils import rand_hex, hash

def initDB():
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, login STRING, password STRING, auth_key STRING)")
    cur.close()
    con.close()

def generate_auth_key():
    return rand_hex(10)

def check_auth(login, password):
    con = sqlite3.connect("users.db")
    hashed = utils.hash(password)
    cur = con.cursor()
    result = cur.execute("SELECT id FROM users WHERE login='" + login + "' AND password='" + hashed + "'").fetchall()
    if len(result) == 0:
        return -1
    
    id = result[0][0]
    auth_key = generate_auth_key()
    cur.execute("UPDATE users SET auth_key='" + auth_key + "' WHERE id=" + str(id))

    cur.close()
    con.close()

    return {"id":id, "key":auth_key}

def is_login_registered(login):
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    result = cur.execute("SELECT id FROM users WHERE login='" + login + "'").fetchall()
    cur.close()
    con.close()
    if len(result) != 0:
        return True
    return False

def create_user(login, name, password):
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    auth_key = generate_auth_key()
    hashed = utils.hash(password)
    cur.execute("INSERT INTO users VALUES(NULL, '" + name + "', '" + login + "', '" + hashed + "', '" + auth_key + "')")
    id = cur.lastrowid
    con.commit()
    cur.close()
    con.close()

    return {"key": auth_key, "id": id}

def get_name(id):
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    result = cur.execute("SELECT name FROM users WHERE id=" + str(id)).fetchall()
    
    cur.close()
    con.close()

    if(len(result) == 0): return -1
    return result[0][0]

def get_user_by_auth(auth):
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    result = cur.execute("SELECT id FROM users WHERE auth_key='" + auth + "'").fetchall()
    
    cur.close()
    con.close()

    if(len(result) == 0): return -1
    return result[0][0]

class Auth(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('login', type=str, required=True)
        parser.add_argument('password', type=str, required=True)

        args = parser.parse_args()

        auth_res = check_auth(args['login'], args['password'])

        if(auth_res == -1):
            return {"ok": 0}
        
        return {"ok" : 1, "user_id" : auth_res["id"], "auth_key": auth_res["key"]}

class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('login', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('name', type=str, required=True)

        args = parser.parse_args()

        login = args["login"]

        if(is_login_registered(login)):
            return {"ok": 0}
        
        reg = create_user(args["login"], args["name"], args["password"])

        return {"ok": 1, "auth_key": reg["key"], "user_id" : reg["id"]}

class Users(Resource):
    def get(self, id):
        name = get_name(id)
        if(name == -1):
            return {"ok": 0}
        return {"ok": 1, "name": name}