
from flask import Flask, flash, render_template, redirect, url_for, request, session, abort
from httpx import StatusCode
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from sqlalchemy import null
from werkzeug.security import generate_password_hash, check_password_hash
from form_data import RegisterForm, LoginForm, EditForm
from flask_wtf.csrf import CSRFProtect
from flask_session import Session

API_KEY = "NLGp3hN-WBLlHLuBoNGYlWqa39IbdaOPPulyELXSzZ5v5ns4JyCatNhyPDSr1fSxvJDGPCEapGBj-x-V1Q9eJtjG02prc6NlDS2LnoYunPz6ilAo2lhXGJhSNdTVYnYx"
ENDPOINT = "https://api.yelp.com/v3/businesses/search"
ID_SEARCH_ENDPOINT = "https://api.yelp.com/v3/businesses/"
HEADERS = {
    "Authorization": 'bearer %s' %API_KEY
}

#Use another python file to import the stuff below instead of having it here
app = Flask(__name__)
csrf = CSRFProtect(app)
csrf.init_app(app)
app.secret_key = 'j872fh#hq87fjh9aw@'
app.config['SECRET_KEY'] = 'super secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
db = SQLAlchemy(app)

#SESSION_TYPE = 'redis'
#app.config.from_object(__name__)
#Session(app)

#sess = Session()
#sess.init_app(app)

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(500))
    stores = db.relationship('Stores', backref='users')

class Stores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(500))
    visit_date = db.Column(db.String(500), nullable=True)
    time = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(500))
    rating = db.Column(db.String(500))
    store_url = db.Column(db.String(500))
    img_url = db.Column(db.String(500))
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))

#db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


def miles_to_meters(miles):
    return miles * 1609


def generate_response(search_location, search_term, radius, limit):
   params = {
    'term': search_term,
    'limit': limit,
    'radius': radius,
    'location': search_location
}

   response = requests.get(url=ENDPOINT, params=params, headers=HEADERS)
   response_data = response.json()
   return response_data

@app.route("/")
def home_page():
    return render_template("index.html")


@app.route("/search", methods=['GET', 'POST'])
#@csrf.exempt
def search():
    if request.method == 'POST':
        radius = miles_to_meters(int(request.form.get('radius')))
        user_limit = str(request.form.get('number'))
        user_response = generate_response(request.form.get('location'), request.form.get('user_query'), radius, user_limit)
        #print(user_response)
        return render_template("results.html", data=user_response)
    return render_template("search.html")


@app.route("/add")
@login_required
def add():
    business_id = request.args.get('store_id')
    response = requests.get(f"{ID_SEARCH_ENDPOINT}{business_id}", headers=HEADERS)
    data = response.json()
    print(data['url'])
    if Stores.query.filter_by(store_url=data['url']).first():
        print("Test")
        return redirect(url_for('home_page'))
    else:
        new_store = Stores(store_name=data['name'], 
                       location=data['location']['address1'], 
                       rating=data['rating'], 
                       store_url=data['url'], img_url=data['image_url'], 
                       users=current_user)

        db.session.add(new_store)
        db.session.commit()      
        return redirect(url_for('profile'))


@app.route("/delete")
@login_required
def delete():
    item = request.args.get("store_del")
    item_to_delete = Stores.query.filter_by(id=item).first()
    db.session.delete(item_to_delete)
    db.session.commit()
    return redirect(url_for("profile"))


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        if Users.query.filter_by(email=form.email.data).first():
            flash("Email already in use.")
            return redirect(url_for('register'))
        else:
            enc_pass = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
            new_user = Users(email=form.email.data, password=enc_pass, name=form.name.data)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('search'))
    return render_template("register.html", form=form)



@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = Users.query.filter_by(email=email).first()
        if not user:
            flash("No user with that email")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash("Incorrect password")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('profile'))
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home_page'))


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)



@app.route("/edit", methods=['POST', 'GET'])
@login_required
def edit():
    form = EditForm()
    item_id = request.args.get("store_edit")
    item_to_edit = Stores.query.filter_by(id=item_id).first()
    if form.validate_on_submit():
        item_to_edit.time = form.time.data
        item_to_edit.visit_date = form.date.data
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template("edit.html", form=form)


@app.errorhandler(401)
def unauthorized(error):
    return f"<h1>You need to login to use this feature. (401)</h1>"
    #return render_template("unauthorized_error.html")


if __name__ == "__main__":
    app.run(debug=True)