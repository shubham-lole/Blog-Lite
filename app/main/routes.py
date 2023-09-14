from app.main import bp 
from flask import render_template, request, url_for, redirect
from app.extensions import db
from app.extensions import login_manager
from app.models.models import *
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, validators
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os, time 
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Login(FlaskForm):
    email = StringField(label = "Email", validators=[DataRequired()])
    password = PasswordField(label = "Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField(label = "Log In")

class Signup(FlaskForm):
    username = StringField(label = "Username", validators=[DataRequired()])
    email = StringField(label = "Email", validators=[DataRequired()])
    password = PasswordField(label = "Password", validators=[DataRequired(), Length(min=8)])
    confirm = PasswordField('Confirm Password', [
        validators.DataRequired(),
        validators.EqualTo('password', message='Passwords must match')])
    submit = SubmitField(label = "Sign Up")

@bp.route('/')
def index():
    return redirect(url_for('main.signup'))

@bp.route("/login", methods=["GET","POST"])
def login():
    login_form = Login()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email = email).first()
        
        if not user:
            flash("email doesn't exist")
            return redirect(url_for('main.login'))
        elif not check_password_hash(user.password, password):
            flash("Incorrect Passsword")
            return redirect(url_for('main.login'))
        else:
            login_user(user)
            print(login_form.validate_on_submit())
            if login_form.validate_on_submit():
                return redirect(url_for('main.home'))
    return render_template("login.html",form = login_form)

@bp.route("/signup", methods=["GET","POST"])
def signup():
    signup_form = Signup()
    if request.method == "POST":

         if User.query.filter_by(email=request.form.get('email')).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('main.login'))

         new_user = User(
            email=request.form.get('email'),
            username=request.form.get('username'),
            password=generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)
        )
         if signup_form.validate_on_submit():
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            
            return redirect(url_for("main.login"))
    return render_template("signup.html",form = signup_form)


@bp.route("/home", methods=["GET","POST"])
@login_required
def home():
    users = User.query.all()
    posts = Post.query.all()
    followers = Follower.query.with_entities(Follower.follower_id).filter_by(user_id = current_user.id).all()
    return render_template("home.html",users = users,posts = posts, follower = followers)


@bp.route("/profile/<user_id>")
@login_required
def profile1(user_id):
    posts = Post.query.filter_by(user_id = user_id).all()
    user = User.query.filter_by(id = user_id).first()
    followers = Follower.query.filter_by(follower_id = user_id).all()
    following = Follower.query.filter_by(user_id = current_user.id).all()
    return render_template("my_profile.html",user_id = user_id, posts = posts, followers = followers, user = user,following = following)


@bp.route("/edit_profile", methods=["GET","POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        username = request.form.get("inputUsername")
        bio = request.form.get("Bio")
        f = request.files['file']
        f.save("app/static/profile/"+secure_filename(str((current_user.id)))+".jpeg")

        record = db.session.query(User).filter_by(id=current_user.id).first()
        record.username = username
        record.bio = bio
        db.session.commit()

        return redirect('profile/'+str(current_user.id))
    return render_template("edit_profile.html")

@bp.route("/followers", methods=["GET","POST"])
@login_required
def followers():
    users = User.query.all()
    followers = Follower.query.with_entities(Follower.user_id).filter_by(follower_id = current_user.id).all()
    return render_template("followers.html", follower = followers, users = users)

@bp.route("/following",methods=["GET","POST"])
@login_required
def following():
    users = User.query.all()
    followers = Follower.query.with_entities(Follower.follower_id).filter_by(user_id = current_user.id).all()
    return render_template("following.html", follower = followers, users = users)


@bp.route("/create_post", methods=["GET","POST"])
def create_post():
    if request.method == "POST":
        localtime = time.asctime( time.localtime(time.time()) )
        f = request.files['post_photo']
        #path="/static/posts/"+str(current_user.id)
        #os.makedirs(path)
        f.save("app/static/posts/"+str(current_user.id)+"."+secure_filename(str((localtime)))+".jpeg")
        caption = request.form.get("caption")
        path = "/static/posts/"+str(current_user.id)+"."+str((localtime)+".jpeg")
        path = path.replace(" ","_")
        path = path.replace(":","")

        new_post = Post(
            photo_url = path,
            caption = caption,
            user_id = current_user.id,
            created_at = localtime
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect('profile/'+str(current_user.id))
    return render_template("create_post.html")

@bp.route("/edit_post",methods=["GET","POST"])
@login_required
def edit_post():
    post_id = request.args.get('id')
    e = request.args.get('e')
    post = Post.query.filter_by(post_id = post_id).first()
    if request.method == "POST":
        if e == '1' :
            if os._exists("app"+post.photo_url):
                os.remove("app"+post.photo_url)
            db.session.delete(post)
            db.session.commit()
            return redirect('/profile/'+str(current_user.id))
        else:
            record = db.session.query(Post).filter_by(post_id = post_id).first()
            caption = request.form.get("caption")
            record.caption = caption
            db.session.commit()
            return redirect('/profile/'+str(current_user.id))
    return render_template("edit_post.html",post = post)

@bp.route("/follow/<user_id>")
@login_required
def follow(user_id):
    new_follow = Follower(user_id = current_user.id, follower_id =  user_id)
    db.session.add(new_follow)
    db.session.commit()
    return redirect(url_for('main.home'))

@bp.route("/unfollow/<user_id>")
@login_required
def unfollow(user_id):
    user = Follower.query.filter_by(user_id = current_user.id, follower_id = user_id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('main.following'))

@bp.route("/remove/<user_id>")
@login_required
def remove(user_id):
    user = Follower.query.filter_by(follower_id = current_user.id, user_id = user_id).first ()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('main.followers'))

@bp.route("/search",methods=["GET","POST"])
@login_required
def search():
    if request.method == "POST":
        inp = request.form.get('search')
        search = "%{}%".format(inp)
        users = User.query.filter(User.username.like(search)).all()
        print(users)
        return render_template("search.html", usr = users)
    return render_template("search.html")
    

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))
