#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from flask import jsonify

from config import app, db, api
from models import User, Recipe

# ensure tables exist (tests expect DB tables to be present)
with app.app_context():
    db.create_all()

class Signup(Resource):
    def post(self):
        json = request.get_json()
        username = json.get('username')
        password = json.get('password')
        bio = json.get('bio')
        image_url = json.get('image_url')

        if not username or not password:
            return {'error': 'username and password required'}, 422

        user = User(username=username, bio=bio, image_url=image_url)
        user.password_hash = password

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'error': 'username must be unique'}, 422

        session['user_id'] = user.id
        return user.to_dict(), 201

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Not authorized'}, 401

        user = User.query.get(user_id)
        if not user:
            return {'error': 'Not authorized'}, 401

        return user.to_dict(), 200

class Login(Resource):
    def post(self):
        json = request.get_json()
        username = json.get('username')
        password = json.get('password')

        user = User.query.filter(User.username == username).first()
        if not user or not user.authenticate(password):
            return {'error': 'Invalid username or password'}, 401

        session['user_id'] = user.id
        return user.to_dict(), 200

class Logout(Resource):
    def delete(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Not authorized'}, 401

        session['user_id'] = None
        return {}, 204

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Not authorized'}, 401

        recipes = Recipe.query.filter(Recipe.user_id == user_id).all()
        return [r.to_dict() for r in recipes], 200

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Not authorized'}, 401

        json = request.get_json()
        title = json.get('title')
        instructions = json.get('instructions')
        minutes = json.get('minutes_to_complete')

        try:
            recipe = Recipe(title=title, instructions=instructions, minutes_to_complete=minutes)
        except ValueError:
            return {'error': 'Invalid recipe'}, 422

        recipe.user_id = user_id

        try:
            db.session.add(recipe)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Invalid recipe'}, 422

        return recipe.to_dict(), 201

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)