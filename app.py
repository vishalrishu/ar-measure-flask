from flask import Flask, render_template, request, jsonify, make_response,redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from  werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps

import os
from flask_cors import CORS
from models import setup_db, User, Measure, db_drop_and_create_all

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, template_folder='template')
    setup_db(app)
    CORS(app)    
    """ uncomment at the first time running the app """
    # db_drop_and_create_all()

# decorator for verifying the JWT
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            # jwt is passed in the request header
            if 'x-access-token' in request.cookies:
                token = request.cookies.get('x-access-token')
            # return 401 if token is not passed
            if not token:
                return jsonify({'message' : 'Token is missing !!'}), 401
    
            try:
                # decoding the payload to fetch the stored details
                data = jwt.decode(token, app.config['SECRET_KEY'])
                current_user = User.query\
                    .filter_by(id = data['id'])\
                    .first()
            except:
                return jsonify({
                    'message' : 'Token is invalid !!'
                }), 401
            # returns the current logged in users contex to the routes
            return  f(current_user, *args, **kwargs)
    
        return decorated

    @app.route("/user/home", methods =['GET'])
    @token_required
    def user_home(current_user):
        print(current_user)
        return render_template("user/home.html")


    @app.route("/measure/new", methods =['POST', 'GET'])
    @token_required
    def measure_create(current_user):
        if request.method == 'POST':
            data = request.form
            object_name, object_width, object_height, object_area = data.get('object_name'), data.get('object_width'), data.get('object_height'),data.get('object_area')
    
            measure = Measure(
                object_name = object_name,
                object_width = object_width,
                object_height=object_height,
                object_area=object_area
            )
            # insert user
            Measure.insert(measure)
            resp = make_response('Successfully created', 201)
            resp = redirect(url_for('user_home'))
            return resp
        return render_template("measure/new.html")

    @app.route("/measure/show", methods =['GET'])
    @token_required
    def measure_list(current_user):
        measures = Measure.query.all()
        return render_template("measure/show.html",
                            title="Measures",
                            measures=measures)

    @app.route("/measure/edit", methods =['PUT', 'GET'])
    @token_required
    def measure_update():
        return   

    @app.route("/measure/delete", methods =['POST', 'GET'])
    @token_required
    def measure_delete(current_user):
        measure = Measure.query\
            .filter_by(id = request.form['id_to_delete'])\
            .first()
        Measure.delete(measure)
        return redirect(url_for('measure_list'))


    @app.route("/")
    def home():
        return render_template("index.html")
        
    # route for logging user in
    @app.route('/login', methods =['POST', 'GET'])
    def login():
        if request.method == 'POST':
            auth = request.form
        
            if not auth or not auth.get('email') or not auth.get('password'):
                return make_response(
                    'Could not verify',
                    401,
                    {'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
                )
        
            user = User.query\
                .filter_by(email = auth.get('email'))\
                .first()

            if not user:
                return make_response(
                    'Could not verify',
                    401,
                    {'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
                )
        
            if check_password_hash(user.password, auth.get('password')):
                token = jwt.encode({
                    'id'  : user.id,
                    'exp' : datetime.utcnow() + timedelta(minutes = 30)
                }, app.config['SECRET_KEY'])
                response = redirect(url_for('user_home'))
                # response.headers['X-Access-Token'] = token.decode('UTF-8')
                
                response.set_cookie('x-access-token', token.decode('UTF-8'))
                print(token.decode('UTF-8'))
                return response
                # return redirect(url_for('user_home'), token = token.decode('UTF-8'))
            return make_response(
                'Could not verify',
                403,
                {'WWW-Authenticate' : 'Basic realm ="Wrong Password !!"'}
            )
        return render_template("login.html")
    
    @app.route('/signup', methods =['GET','POST'])
    def signup():
        if request.method == 'POST':
            data = request.form
            name, email = data.get('name'), data.get('email')
            password = data.get('password')
        
            user = User.query\
                .filter_by(email = email)\
                .first()
            if not user:
                user = User(
                    name = name,
                    email = email,
                    password = generate_password_hash(password)
                )
                # insert user
                User.insert(user)
        
                return redirect(url_for('home'))
            else:
                # returns 202 if user already exists
                return make_response('User already exists. Please Log in.', 202)
        return render_template("signup.html")

    return app

app = create_app()
if __name__ == '__main__':
    port = int(os.environ.get("PORT",5000))
    app.run(host='127.0.0.1',port=port,debug=True)