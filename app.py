import sqlite3
from flask import Flask
from flask import abort, redirect, render_template, request, session
import config
import db
import messages
import re
import users
import forum
import secrets

app = Flask(__name__)
app.secret_key = config.secret_key

def check_csrf():
    if request.form.get("csrf_token") != session.get("csrf_token"):
        abort(403)

def require_login():
    if "user_id" not in session:
        abort(403)
        
@app.route("/")
def index():
    all_messages = messages.get_messages()
    return render_template("index.html", messages=all_messages)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
       abort(404)
    user_messages = users.get_messages(user_id)
    return render_template("show_user.html", user=user, messages=user_messages)
    
@app.route("/find_message")
def find_message():
    query = request.args.get("query")
    if query:
       results = messages.find_messages(query)
    else:
       query = ""
       results = []
    return render_template("find_message.html", query=query, results=results)
    
@app.route("/message/<int:message_id>")
def show_message(message_id):
    message = messages.get_message(message_id)
    if not message:
        abort(404)

    classes = messages.get_classes(message_id)
    forum_messages = []
    user_id = session.get("user_id")

    if user_id:
        all_forum_messages = forum.get_forum_messages(message_id)

        authorized_users = {message["user_id"]}
        authorized_users.update([f["user_id"] for f in all_forum_messages])
        
        if user_id in authorized_users:
            forum_messages = all_forum_messages

    return render_template(
        "show_message.html",
        message=message,
        classes=classes,
        forum=forum_messages
    )

@app.route("/new_message")
def new_message():
    require_login()
    classes = messages.get_all_classes()
    return render_template("new_message.html", classes=classes)
        
@app.route("/create_message", methods=["POST"])
def create_message():
    require_login()
    check_csrf()
    
    title = request.form["title"]
    if not title or len(title) > 50:
       abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
       abort(403)
    age = request.form["age"]
    if not re.search("^[1-9][0-9]{0,2}$", age):
       abort(403)
    user_id = session["user_id"]
    
    all_classes = messages.get_all_classes()
     
    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
           class_title, class_value = entry.split(":")
           if class_title not in all_classes:
              abort(403)
           if class_value not in all_classes[class_title]:
              abort(403)
           classes.append((class_title, class_value))
    
    messages.add_message(title, description, age, user_id, classes)
    
    return redirect("/")

@app.route("/edit_message/<int:message_id>")
def edit_message(message_id):
    require_login()
    message = messages.get_message(message_id)
    if not message:
       abort(404)
    if message["user_id"] != session["user_id"]:
       abort(403)
       
    all_classes = messages.get_all_classes()
    classes = {}
    for my_class in all_classes:
        classes[my_class] = ""
    for entry in messages.get_classes(message_id):
        classes[entry["title"]] = entry["value"]
        
    return render_template("edit_message.html", message=message, classes=classes, all_classes=all_classes)
    
@app.route("/update_message", methods=["POST"])
def update_message():
    require_login()
    check_csrf()
    message_id = request.form["message_id"]
    message = messages.get_message(message_id)
    if not message:
       abort(404)
    if message["user_id"] != session["user_id"]:
       abort(403)
    
    title = request.form["title"]
    if not title or len(title) > 50:
       abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
       abort(403)

    all_classes = messages.get_all_classes()
    
    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
           class_title, class_value = entry.split(":")
           if class_title not in all_classes:
              abort(403)
           if class_value not in all_classes[class_title]:
              abort(403)
           classes.append((class_title, class_value))
           
    messages.update_message(message_id, title, description, classes)
    
    return redirect("/message/" + str(message_id))
    
@app.route("/remove_message/<int:message_id>",  methods=["GET", "POST"])
def remove_message(message_id):
    require_login()
    message = messages.get_message(message_id)
    if not message:
       abort(404)
    if message["user_id"] != session["user_id"]:
       abort(403)
       
    if request.method == "GET": 
       return render_template("remove_message.html", message=message)
       
    if request.method == "POST":
       check_csrf()
       if "remove" in request.form:
           messages.remove_message(message_id)
           return redirect("/")
       else:
           return redirect("/message/" + str(message_id)) 
        
@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
            
    try:
       users.create_user(username, password1)
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"
        
    return "Tunnus luotu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
        
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
    user_id = users.check_login(username, password)
    if user_id:
        session["user_id"] = user_id
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")
    else:
        return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")

