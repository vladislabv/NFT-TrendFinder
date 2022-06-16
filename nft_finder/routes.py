from flask import render_template, url_for, redirect, request
from nft_finder import app

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route('/home')
def home():
    if request.method == 'GET':
        redirect(url_for('home'))
    return render_template('home.html')