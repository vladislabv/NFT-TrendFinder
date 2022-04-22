# Import flask and template operators
import os

from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from celery import Celery

# Import MongoAlchemy
from flask_mongoengine import MongoEngine

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Define the WSGI application object
app = Flask(__name__)
# Configurations
app.config.from_object('config')
celery = make_celery(app)

# all variables from .env will be loaded into environment
load_dotenv(
    os.path.join(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)
        )), # get path of the current file
        "env\.env" # file name
        )
    )

# Define the database object which is imported
# by modules and controllers
db = MongoEngine(app)
#from .dashboard.models import User, me
#try:
#    User(name="Vlad", password="123", email="vv@gmail.com").save()
#except me.ValidationError as err:
#    print('The username or email already exist in the system, please try another combination.')

#db.init_app(app)

# Sample HTTP error handling
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

# Import a module / component using its blueprint handler variable (mod_auth)
from app.dashboard import dashboard_bp as dashboard_module
app.register_blueprint(dashboard_module)

# Register blueprint(s)
#app.register_blueprint(auth_module)
# app.register_blueprint(xyz_module)
# ..

@celery.task()
def add_together(a, b):
    return a + b

result = add_together.delay(2, 2)
#result.wait()  # 65