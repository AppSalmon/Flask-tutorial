from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from os import path

app = Flask(__name__)
app.config["SECRET_KEY"] = "DXHTuan-top-1-viet-nam-datathon-2023" # Mã hóa session cookie để tránh bị hack - sử dụng pass càng khó càng tốt
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///user.db" # Nơi lưu database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Kiểm tra thay đổi
app.permanent_session_lifetime = timedelta(minutes = 1) # Set lifetime cho user (Phiên đăng nhập)

db = SQLAlchemy(app)

#Tạo bảng user
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email


@app.route('/') # Link trang web

def hello_world():
    return "<h1>Hoang Tuan</h1>"

@app.route('/home') # Link trang web
def home_page():
    return render_template("home.html")

@app.route('/login', methods = ["POST", "GET"]) # Link trang web
def login():
    if request.method == "POST":
        user_name = request.form["name"]
        session.permanent = True # Bắt đầu set lifetime
        session["user"] = user_name
        if user_name:
            # Check user in database
            found_user = User.query.filter_by(name = user_name).first()
            if found_user:
                session['email'] = found_user.email
            else:
                # Add database
                user = User(user_name, "temp@gmail.com")
                db.session.add(user)
                db.session.commit()
                flash("Created in DB!")
            flash("You logged in successfully!", "info")
            return redirect(url_for('user', name = user_name))
    if "user" in session:
        flash("You have already logged in!", "info")
        user_name = session["user"]
        return redirect(url_for('user', name = user_name))
        
    return render_template("login.html")

# Truyền số
@app.route('/blog/<int:blog_id>')
def blog(blog_id):
    return f"Blog {blog_id}"

@app.route('/admin')
def hello_admin():
    return "<h1>Hello admin</h1>"

# Truyền chữ
@app.route('/user', methods = ["POST", "GET"])
def user():
    email = None
    if "user" in session:
        name = session["user"]
        if request.method == "POST":
            if request.form['name']:
                User.query.filter_by(name = name).delete()
                db.session.commit()
                flash("Deleted user!")
                return redirect(url_for("log_out"))
            else:
                email = request.form['email']
                session['email'] = email
                found_user = User.query.filter_by(name = name).first()
                found_user.email = email
                db.session.commit()
                flash("Email updated!")
        elif "email" in session:
            email = session['email']
        return render_template('user.html', user = name, email = email)
    return redirect(url_for("login"))

@app.route('/logout')
def log_out():
    session.pop("user", None)
    flash("You haven't logged in", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    if not path.exists("user.db"):
        with app.app_context():
            db.create_all()
            # db.create_all(app = app)
            print("Created database")
    app.run(debug = True)
    