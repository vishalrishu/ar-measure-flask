from flask import Flask, render_template, request, jsonify, make_response,redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from  werkzeug.security import generate_password_hash, check_password_hash
# imports for PyJWT authentication
import jwt
from datetime import datetime, timedelta
from functools import wraps
  

app = Flask(__name__, template_folder='template')
app.config['SECRET_KEY'] = 'aaaa1111'
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:aaaa1111@localhost/flask_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
class Measure(db.Model):
    __tablename__='measures'

    id=db.Column(db.Integer, primary_key=True, unique=True)
    object_name=db.Column(db.String(120))
    object_width=db.Column(db.Numeric(12, 2))
    object_height=db.Column(db.Numeric(12, 2))
    object_area=db.Column(db.Numeric(12, 2))
    
    def __init__(self, object_name, object_height,object_width,object_area):
        self.object_name=object_name
        self.object_width=object_width
        self.object_height=object_height
        self.object_area=object_area

class User(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(80))
    email=db.Column(db.String(80), unique = True)
    password=db.Column(db.String(120))

    def __init__(self,name,email,password):
        self.name=name
        self.email=email
        self.password=password

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
        db.session.add(measure)
        db.session.commit()
  
        return make_response('Successfully Created.', 201)
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
def measure_delete():
    measure = Measure.query\
        .filter_by(id = request.form['id_to_delete'])\
        .first()
    db.session.delete(measure)
    db.session.commit()
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
        db.session.add(user)
        db.session.commit()
  
        return redirect(url_for('user_home'))
    else:
        # returns 202 if user already exists
        return make_response('User already exists. Please Log in.', 202)
  return render_template("signup.html")

    
if __name__ == "__main__":
    app.run(debug=True)
