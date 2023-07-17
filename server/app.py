#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

excluded_endpoints = ['signup', 'check_session', 'login', 'logout']

@app.before_request
def check_is_logged_in():
    if request.endpoint not in excluded_endpoints:
        user_id = session.get('user_id')
        user = User.query.filter(User.id == user_id).first()

        if not user:
            return {'error': 'User is not logged in'}, 401


@app.post('/signup')
def signup():
    # get json from request
    data = request.get_json()

    try:
        # create new user using json data
        new_user = User(
            username=data['username'],
            bio=data.get('bio'),
            image_url=data.get('image_url')
        )
        new_user.password_hash = data['password']
        # add user to db
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        print(e)
        return {'error': 'Error creating user'}, 422

    # add user_id cookie
    session['user_id'] = new_user.id

    # return user as JSON, status code 201
    return new_user.to_dict(), 201

@app.get('/check_session')
def check_session():
    # get user_id from browser cookies
    user_id = session.get('user_id')
    # check for user in db
    user = User.query.filter(User.id == user_id).first()

    if not user:
        # user doesn't exist, return 401 (unauthorized)
        return {'error': 'Unauthorized'}, 401
    
    # user exists, return user as JSON, status code 200
    return user.to_dict(), 200

@app.post('/login')
def login():
    # get JSON from request
    data = request.get_json()
    # query db by username
    user = User.query.filter(
        User.username == data['username']
    ).first()
    
    if not user or not user.authenticate(data['password']):
        # user doesn't exist or password doesn't match, return 401
        return {'error': 'Login failed'}, 401
    
    # login success, add cookie to broswer
    session['user_id'] = user.id
    return user.to_dict(), 201

@app.delete('/logout')
def logout():
    # check if user_id cookie is set
    user_id = session.get('user_id')

    if not user_id:
        # no cookie is set, return 401
        return {'error': 'User is not logged in'}, 401
    
    # delete the cookie
    session.pop('user_id')
    # return 204 (no content)
    return {}, 204

@app.get('/recipes')
def get_all_recipes():
    recipes = Recipe.query.all()
    data = [r.to_dict() for r in recipes]
    return data, 200


if __name__ == '__main__':
    app.run(port=5555, debug=True)
