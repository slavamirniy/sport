from flask import abort, request
from flask_restful import Resource, reqparse
from marshmallow import Schema, fields
from db import get_database
from users import get_name, get_user_by_auth

class GetPostsQuerySchema(Schema):
    page = fields.Number(required=True)
    auth_key = fields.Str(required=False)
    userid = fields.Str(required=False)

class ExerciseSchema(Schema):
    exercise_id = fields.Number(required=True)
    repeats = fields.Number()
    time = fields.Number()

class PostPostsQuerySchema(Schema):
    title = fields.Str(required=True)
    training = fields.List(fields.Nested(ExerciseSchema))
    auth_key = fields.Str(required=True)

class PostsQuery(Resource):
    get_schema = GetPostsQuerySchema()
    post_schema = PostPostsQuerySchema()

    def get(self):
        errors = self.get_schema.validate(request.args)
        if errors:
            abort(400, str(errors))
        page_num = int(request.args["page"])
        page_posts = Post.get_page(page_num, 3)
        return [o.to_object(get_name) for o in page_posts]
    
    def post(self):
        errors = self.post_schema.validate(request.json)
        if errors:
            abort(400, str(errors))
        
        r = request.json
        auth_key = r["auth_key"]

        user_id = get_user_by_auth(auth_key)
        if user_id == -1:
            return {"ok": 0}
        
        r["creator_id"] = user_id
        p = Post.to_post(r)
        p.save()

        return {"ok": 1, "post_id": p.post_id}
    
class Exercise():
    def __init__(self, exercise_id, repeats = None, time = None) -> None:
        self.exercise_id = exercise_id
        self.repeats = repeats
        self.time = time

    def to_object(self):
        return {
            "exercise_id": self.exercise_id,
            "repeats": self.repeats,
            "time": self.time
        }

class Post():
    def __init__(self, post_id: int, creator_id: int, title, training: list[Exercise], likes: int = 0, is_liked: bool = False, **args) -> None:
        self.creator = creator_id
        self.post_id = post_id
        self.title = title
        self.training = training
        self.likes = likes
        self.is_liked = is_liked
    
    def save(self):
        collection = get_database()["posts"]
        if self.post_id is None:
            last_id = collection.find_one({}, limit = 1, sort = [["post_id", -1]])
            self.post_id = last_id["post_id"] + 1 if last_id is not None else 1
        collection.update_one({
            "post_id": self.post_id
        }, {
            "$set": {
                "creator_id": self.creator,
                "title": self.title,
                "training": [e.to_object() for e in self.training]
            }
        }, True)
    
    def get_page(page: int, size: int):
        collection = get_database()["posts"]
        results = collection.find({}, limit = size, skip = size * page)
        return [Post.to_post(r) for r in results]
    
    def to_post(object):
        object["training"] = [Exercise(**e) for e in object["training"]]
        object["post_id"] = object["post_id"] if "post_id" in object else None 
        return Post(**object)
    
    def get_by_id(id):
        result = get_database()["posts"].find_one({"post_id": id}, limit = 1)
        return None if result is None else Post(**result)

    def to_object(self, getusername):
        return {
            "creator": {"id": self.creator, "name": getusername(self.creator)},
            "post_id": self.post_id,
            "title": self.title,
            "training": [o.to_object() for o in self.training],
            "likes": self.likes,
            "is_liked": self.is_liked
        }
