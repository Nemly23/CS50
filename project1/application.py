import os
import shutil
from os import listdir
from os.path import isfile, join

import bcrypt

from flask import Flask, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    pwhash = bcrypt.hashpw(plain_text_password, bcrypt.gensalt())
    return pwhash.decode('utf8')

def check_password(plain_text_password, hashed_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password, hashed_password)

app = Flask(__name__)

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['TESTING'] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

user = ""

@app.route("/", methods=['GET', 'POST'])
def index():
        global user
        sign = request.form.get("sign")
        if sign:
            user = ""
        return render_template("index.html", user = user)



@app.route("/reports")
def reports():
    user = request.form.get("User")
    return render_template("reports.html")

@app.route("/images")
def images():
    images = db.execute("SELECT name FROM images").fetchall()
    for i, image in enumerate(images):
        images[i]=f"/static/images/{image.name}.jpg"
    barro = db.execute("SELECT name FROM images WHERE tag1_id = 1 OR tag2_id = 1 OR tag3_id = 1").fetchall()
    rodas = db.execute("SELECT name FROM images WHERE tag1_id = 2 OR tag2_id = 2 OR tag3_id = 2").fetchall()
    outros = db.execute("SELECT name FROM images WHERE tag1_id = 3 OR tag2_id = 3 OR tag3_id = 3").fetchall()
    return render_template("images.html", images=images, barro=barro, rodas=rodas, outros=outros)

@app.route("/videos")
def videos():
    return render_template("videos.html")

@app.route("/search", methods=["POST"])
def search():
    search = request.form.get("search")
    return render_template(f"{search}.html")

@app.route("/addimages")
def addimages():
    files = [f for f in listdir("static/new_images") if isfile(join("static/new_images", f))]
    if not files:
        return render_template("erro.html", mensage="No image to be added")
    #else:
        #for file in files:
            #p = rf"static/new_images/{file}"
            #t = rf"static/images/{file}"
            #shutil.move(p,t)
    return render_template("addimages.html", files=files)

@app.route("/addedimages", methods=["POST"])
def addedimages():
    files = [f for f in listdir("static/new_images") if isfile(join("static/new_images", f))]
    if not files:
        return render_template("erro.html", mensage="No image to be added")
    else:
        for file in files:
            tag = []
            for i in range(3):
                if request.form.get(f"tag{i+1}_{file}") == '0':
                    tag.append(None)
                else:
                    tag.append(request.form.get(f"tag{i+1}_{file}"))
            db.execute("INSERT INTO images (name, tag1_id, tag2_id, tag3_id) VALUES (:name, :tag1_id, :tag2_id, :tag3_id)",
                    {"name": file[:-4], "tag1_id": tag[0], "tag2_id": tag[1], "tag3_id": tag[2]})
            db.commit()
            p = rf"static/new_images/{file}"
            t = rf"static/images/{file}"
            shutil.move(p,t)
    return render_template("erro.html", mensage="Images added")

@app.route("/login", methods=["POST"])
def login():
    global user
    user = request.form.get("User")
    password = request.form.get("Password")
    actual = db.execute("SELECT password FROM login WHERE username = (:User)", {"User": user}).fetchone()
    if actual == None:
        return render_template("erro.html", mensage="No user found or wrong password", user= user)
    if check_password (password.encode(), actual.password.encode()):
        return render_template("erro.html", mensage= f"Successful login of {user}", user= user)
    else:
        return render_template("erro.html", mensage="No user found or wrong password", user= user)

@app.route("/signup")
def signup():
    global user
    return render_template("signup.html", user= user)

@app.route("/signin", methods=['GET', 'POST'])
def signin():
    global user
    if user:
        return render_template("signin.html", logged = True, user = user)
    else:
        return render_template("signin.html", logged = False, user = user)

@app.route("/sign", methods=["POST"])
def sign():
    user = request.form.get("User")
    password = request.form.get("Password")
    hash = get_hashed_password(password.encode('utf-8'))
    actual = db.execute("SELECT user FROM login WHERE username = (:User)", {"User": user}).fetchone()
    if actual == None:
        db.execute("INSERT INTO login (username, password) VALUES (:user, :password)",
                {"user": user, "password": hash})
        db.commit()
        return render_template("erro.html", mensage="User add")
    else:
        return render_template("erro.html", mensage="User already exist")
