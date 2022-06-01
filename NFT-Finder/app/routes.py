from flask import render_template, url_for, redirect, request
from app import app

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route('/home')
def home():
    if request.method == 'GET':
        redirect(url_for('home'))
    return render_template('home.html')

@app.route('/login')
def login():
    if request.method == 'GET':
        redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    if request.method == 'GET':
        redirect(url_for('logout'))
    return render_template('logout.html')