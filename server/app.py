#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

@app.post('/signup')
def signup():
    pass

@app.get('/check_session')
def check_session():
    # get user_id from cookies
    user_id = session.get('user_id')
    # query db for that user
    user = User.query.filter(
        User.id == user_id
    ).first()

    if not user:
        return {'error': 'Not authorized'}, 401
    
    return user.to_dict(), 200

@app.post('/login')
def login():
    # get username/pass from request
    data = request.get_json()
    # query db for user
    user = User.query.filter(
        User.username == data.get('username')
    ).first()

    # check user exists and password matches
    if not user or not user.authenticate(data.get('password')):
        return {'error': 'Invalid login'}, 401
    
    # save user id as browser cookie
    session['user_id'] = user.id
    return user.to_dict(), 201

@app.delete('/logout')
def logout():
    pass


if __name__ == '__main__':
    app.run(port=5555, debug=True)
