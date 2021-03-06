import os
from os.path import join, dirname
from dotenv import load_dotenv

from flask import Flask, render_template, request, url_for, redirect, flash, session, request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import timedelta

import bcrypt

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")
app.config['MONGO_URI'] = os.environ.get("MONGO_URI")

mongo = PyMongo(app)

users = mongo.db.users
todos_collection = mongo.db.YouToDo


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('todo_index'))

    return render_template('index.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/login/', methods=['POST'])
def login():
    login_user = users.find_one({
        'name': request.form['username']
    })

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    if login_user:
        flash('Invalid password')
    else:
        flash('Invalid username')

    return redirect(url_for('index'))


@ app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({
            'name': request.form['username']
        })

        if existing_user is None:
            hashpass = bcrypt.hashpw(
                request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({
                'name': request.form['username'],
                'password': hashpass
            })
            flash('Your account has been registered!')
            return redirect(url_for('index'))

        flash('That username already exists!')
        return redirect(url_for('register'))
    else:
        flash('Input nonexisting user information to register.')

    # if method is a GET and not a POST
    return render_template('register.html')


@ app.route('/account/', methods=['GET', 'POST'])
def account():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({
            'name': request.form['username']
        })

        if existing_user:
            hashpass = bcrypt.hashpw(
                request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.update_one({
                '_id': ObjectId(existing_user['_id'])
            }, {
                "$set": {
                    'name': request.form['username'],
                    'password': hashpass
                }
            })
            flash('Your password has been updated!')
            return redirect(url_for('index'))

        flash('That username does not exist!')
        return redirect(url_for('account'))
    else:
        flash('Input existing username and new password.')

    # if method is a GET and not a POST
    return render_template('account.html')


@ app.route('/todo/')
def todo_index():
    saved_todos = todos_collection.find({
        'name': session['username']
    })
    return render_template('todo_index.html', todos=saved_todos)


@ app.route('/add_todo/', methods=['POST'])
def add_todo():
    todo_priority = request.form.get('priority')
    todo_item = request.form.get('todo')
    todo_link = request.form.get('link')
    todos_collection.insert_one({
                                'name': session['username'],
                                'priority': todo_priority,
                                'text': todo_item,
                                'link': todo_link,
                                'complete': False
                                })
    return redirect(url_for('todo_index'))


@ app.route('/edit_todo/', methods=['POST'])
def edit_todo():
    todo_priority = request.form.get('priority')
    todo_item = request.form.get('todo')
    todo_link = request.form.get('link')
    todos_collection.insert_one({
                                'name': session['username'],
                                'priority': todo_priority,
                                'text': todo_item,
                                'link': todo_link,
                                'complete': False
                                })
    return redirect(url_for('todo_index'))


@ app.route('/editform/<oid>/')
def editform(oid):
    todo_item = todos_collection.find_one({
        '_id': ObjectId(oid)
    })
    old_priority = todo_item['priority']
    old_text = todo_item['text']
    old_link = todo_item['link']
    return render_template('editform.html', old_priority=old_priority, old_text=old_text, old_link=old_link)


@ app.route('/complete_todo/<oid>/')
def complete_todo(oid):
    todo_item = todos_collection.find_one({
        '_id': ObjectId(oid)
    })
    todo_item['complete'] = True
    todos_collection.save(todo_item)
    return redirect(url_for('todo_index'))


@ app.route('/delete_completed/')
def delete_completed():
    todos_collection.delete_many({
        'name': session['username'],
        'complete': True
    })
    return redirect(url_for('todo_index'))


@ app.route('/delete_all/')
def delete_all():
    todos_collection.delete_many({
        'name': session['username']
    })
    return redirect(url_for('todo_index'))


if __name__ == '__main__':
    app.run(debug=True)
