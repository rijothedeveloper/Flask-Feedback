from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models.models import db, connect_db, User, Feedback
from forms.forms import UserForm, LoginForm, FeedbackForm

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
            flash(f"User registered", "success")
            return redirect(f"/users/{new_user.username}")
        
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
            session["user_id"] = user.id
            flash(f"welcom back {user.username}", "success")
            return redirect(f"/users/{user.username}")
        
    return render_template("login-form.html", form=form)

@app.route("/logout")
def logout():
    session.pop("user_id")
    flash("logged out successfully","info")
    return redirect("/")

@app.route("/secret")
def show_secret():
    if "user_id" not in session:
        flash("you must be logged in to view","danger")
        return redirect("/")
    return render_template("secret.html")

@app.route("/users/<username>")
def show_user_account(username):
    if "user_id" not in session:
        flash("you must be logged in to view","danger")
        return redirect("/")
    
    user = User.query.filter(User.username == username).first()
    if(user):
        feedbacks = Feedback.query.filter(Feedback.username == user.username).all()
        return render_template("user-info.html", user=user, feedbacks=feedbacks)
    
    flash("user is not available", "danger")
    return redirect("/")

@app.route("/users/<username>/delete", methods=["GET", "POST"])
def delete_user(username):
    if "user_id" not in session:
        flash("you must be logged in to delete yourself","danger")
        return redirect("/")
    
    user = User.query.filter(User.id == session["user_id"]).first()
    if user.username != username:
        flash(f"you are not permitted to delete {username}","danger")
        return redirect("/")
    
    username = user.username 
    Feedback.query.filter(Feedback.username == username).delete()
    db.session.commit()
    User.query.filter(User.id == session["user_id"]).delete()
    db.session.commit()
    session.pop("user_id")
    flash(username +" is deleted","warning")
    return redirect("/")
    
@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def handleAddFeedback(username):
    if "user_id" not in session:
        flash("you must be logged in to delete yourself","danger")
        return redirect("/")
    form = FeedbackForm()
    
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        user = User.query.filter(User.id == session["user_id"]).first()
        feedback = Feedback(title=title, content=content, username=user.username)
        db.session.add(feedback)
        db.session.commit()
        flash("feed back added successfully", "success")
        return redirect(f"/users/{user.username}")
        
    return render_template("feedback-form.html", form=form)

@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def edit_feedback(feedback_id):
    if "user_id" not in session:
        flash("you must be logged in to delete yourself","danger")
        return redirect("/")
    
    user = User.query.filter(User.id == session["user_id"]).first()
    feedback = Feedback.query.get_or_404(feedback_id)
    
    if user.username != feedback.username:
        flash(f"you are not permitted to update this feedback","danger")
        return redirect("/")
    
    if feedback:
        form = FeedbackForm(obj=feedback)
        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.commit()
            user = User.query.filter(User.id == session["user_id"]).first()
            flash("feedback updated", "info")
            return redirect(f"/users/{user.username}")
        else:
            return render_template("edit-feedback-form.html", form=form)
        
    else:
        flash("invalid url", "danger")
        return redirect("/")
        
@app.route("/feedback/<int:feedback_id>/delete")
def delete_feedback(feedback_id):
    if "user_id" not in session:
        flash("you must be logged in to delete yourself","danger")
        return redirect("/")
    
    user = User.query.filter(User.id == session["user_id"]).first()
    feedback = Feedback.query.get_or_404(feedback_id)
    if user.username != feedback.username:
        flash(f"you are not permitted to delete this feedback","danger")
        return redirect("/")
    
    Feedback.query.filter(Feedback.id == feedback_id).delete()
    db.session.commit()
    flash("feedback deleted", "info")
    return redirect(f"/users/{user.username}")