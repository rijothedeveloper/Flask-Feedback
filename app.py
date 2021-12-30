from flask import Flask, render_template, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from models.models import db, connect_db, User
from forms.forms import UserForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = "oh-so-secret"
debug = DebugToolbarExtension(app)

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
connect_db(app)
# db.create_all()

@app.route("/")
def show_home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register_user():
    form = UserForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username=username, pwd=password, email=email, first_name=first_name, last_name=last_name)
        if new_user:
            db.session.add(new_user)
            db.session.commit()
            session["user_id"] = new_user.id
            return redirect("/secret")
        
    return render_template("register-form.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login_user():
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # authenticate will return a user or False
        user = User.authenticate(username, password)
        
        if user:
            session["user-id"] = user.id
            return redirect("/secret")
        
    return render_template("login-form.html", form=form)

@app.route("/secret")
def show_secret():
    return render_template("secret.html")