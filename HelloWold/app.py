import os
import shutil
from os import listdir
from os.path import isfile, join


from flask import Flask, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['TESTING'] = True

engine = create_engine("postgres://postgres:KOTONARU16@localhost:5432/project1")
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/reports")
def reports():
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
