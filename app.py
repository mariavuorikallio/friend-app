"""
This module contains the main logic of the Friend App application.
"""

import re
import secrets
import sqlite3
from flask import Flask, abort, redirect, render_template, request, session, make_response, flash

import config
import messages
import users
import threads

app = Flask(__name__)
app.secret_key = config.secret_key


@app.before_request
def ensure_csrf_token():
    """Ensures that a CSRF token exists in the session."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)


def check_csrf():
    """Checks the CSRF token."""
    if request.method == "POST":
        if request.form.get("csrf_token") != session.get("csrf_token"):
            abort(403)


def require_login():
    """Ensures that the user is logged in."""
    if "user_id" not in session:
        abort(403)


@app.route("/")
def index():
    """Displays the homepage messages and unread messages for logged-in users."""
    user_id = session.get("user_id")
    unread_msgs = threads.get_unread_messages(user_id) if user_id else []

    all_messages = messages.get_messages()
    return render_template("index.html", messages=all_messages, unread_msgs=unread_msgs)


@app.route("/user/<int:user_id>")
def show_user(user_id):
    """Displays the user's profile and messages."""
    user = users.get_user(user_id)
    if not user:
        abort(404)

    user_messages = users.get_messages(user_id)
    back_to = request.args.get("from", "/")
    return render_template(
        "show_user.html",
        user=user,
        messages=user_messages,
        previous_page=back_to
    )


@app.route("/add_image", methods=["GET", "POST"])
def add_image():
    """Allows the user to add a profile image."""
    require_login()
    if request.method == "GET":
        return render_template("add_image.html")

    check_csrf()
    file = request.files["image"]
    if not file.filename.endswith(".jpg"):
        return "ERROR: wrong file format"

    image = file.read()
    if len(image) > 100 * 1024:
        return "ERROR: image too large"

    user_id = session["user_id"]
    users.update_image(user_id, image)
    return redirect(f"/user/{user_id}")


@app.route("/image/<int:user_id>")
def show_image(user_id):
    """Displays the user's profile image."""
    image = users.get_image(user_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response


@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    """Allows a logged-in user to update their profile info and image."""
    require_login()
    user_id = session["user_id"]
    user = users.get_user(user_id)
    if not user:
        abort(404)

    if request.method == "GET":
        return render_template("edit_profile.html", user=user)

    check_csrf()
    age = request.form.get("age")
    bio = request.form.get("bio")
    if not age or not bio:
        flash("Ikä ja bio ovat pakollisia kenttiä!")
        return redirect("/edit_profile")

    try:
        age = int(age)
    except ValueError:
        flash("Ikä tulee olla numero.")
        return redirect("/edit_profile")

    file = request.files.get("image")
    if file and file.filename.endswith(".jpg"):
        image = file.read()
        if len(image) <= 100 * 1024:
            users.update_image(user_id, image)
        else:
            flash("Profiilikuva on liian suuri (max 100kb).")
            return redirect("/edit_profile")

    users.update_profile(user_id, age, bio)
    flash("Profiili päivitetty onnistuneesti!")
    return redirect(f"/user/{user_id}")


@app.route("/find_message")
def find_message():
    """Searches messages by a query string."""
    query = request.args.get("query")
    results = messages.find_messages(query) if query else []
    return render_template("find_message.html", query=query or "", results=results)


@app.route("/message/<int:message_id>")
def show_message(message_id):
    """Displays a single message and its related threads."""
    message = messages.get_message(message_id)
    if not message:
        abort(404)
        
    user = users.get_user(message["user_id"])
    if not user:
        abort(404)

    classes_list = messages.get_classes(message_id)
    user_id = session.get("user_id")
    threads_list = threads.get_threads_by_message(message_id) if user_id and user_id == message["user_id"] else []

    return render_template(
        "show_message.html",
        message=message,
        classes=classes_list,
        threads=threads_list,
        user=user
    )


@app.route("/new_message")
def new_message():
    """Displays the form to create a new message."""
    require_login()
    classes_list = messages.get_all_classes()
    return render_template("new_message.html", classes=classes_list)


@app.route("/create_message", methods=["POST"])
def create_message():
    """Creates a new message."""
    require_login()
    check_csrf()

    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)

    description = request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
        
    user_id = session["user_id"]
    user = users.get_user(user_id)
    if not user:
        abort(403)
    age = user["age"] 

    all_classes = messages.get_all_classes()
    classes_selected = []

    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes or class_value not in all_classes[class_title]:
                abort(403)
            classes_selected.append((class_title, class_value))

    messages.add_message(title, description, age, user_id, classes_selected)
    return redirect("/")


@app.route("/edit_message/<int:message_id>")
def edit_message(message_id):
    """Displays the edit form for a message."""
    require_login()
    message = messages.get_message(message_id)
    if not message or message["user_id"] != session["user_id"]:
        abort(403)

    all_classes = messages.get_all_classes()
    classes_dict = {my_class: "" for my_class in all_classes}
    for entry in messages.get_classes(message_id):
        classes_dict[entry["title"]] = entry["value"]

    return render_template(
        "edit_message.html",
        message=message,
        classes=classes_dict,
        all_classes=all_classes,
    )


@app.route("/update_message", methods=["POST"])
def update_message():
    """Updates an existing message."""
    require_login()
    check_csrf()

    message_id = request.form["message_id"]
    message = messages.get_message(message_id)
    if not message or message["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    description = request.form["description"]
    if not title or len(title) > 50 or not description or len(description) > 1000:
        abort(403)

    all_classes = messages.get_all_classes()
    classes_selected = []

    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes or class_value not in all_classes[class_title]:
                abort(403)
            classes_selected.append((class_title, class_value))

    user_id = session["user_id"]
    messages.update_message(message_id, user_id, title, description, classes_selected)
    return redirect(f"/message/{message_id}")


@app.route("/remove_message/<int:message_id>", methods=["GET", "POST"])
def remove_message(message_id):
    """Deletes a message or displays a confirmation form."""
    require_login()
    user_id = session["user_id"]
    message = messages.get_message(message_id)
    if not message or message["user_id"] != user_id:
        abort(403)

    if request.method == "GET":
        return render_template("remove_message.html", message=message)

    check_csrf()

    if "back" in request.form:
        return redirect(f"/message/{message_id}")

    if "remove" in request.form:
        messages.remove_message(message_id, user_id)
        return redirect("/")

    return redirect(f"/message/{message_id}")


@app.route("/register")
def register():
    """Displays the registration form."""
    return render_template("register.html")


@app.route("/create", methods=["POST"])
def create():
    """Creates a new user with required age, bio, and optional profile image."""
    check_csrf()

    username = request.form.get("username")
    password1 = request.form.get("password1")
    password2 = request.form.get("password2")
    age = request.form.get("age")
    bio = request.form.get("bio")

    if not username or not password1 or not password2 or not age or not bio:
        flash("Kaikki kentät ovat pakollisia!")
        return redirect("/register")

    if password1 != password2:
        flash("Salasanat eivät täsmää!")
        return redirect("/register")

    try:
        age = int(age)
    except ValueError:
        flash("Ikä tulee olla numero.")
        return redirect("/register")

    bio = bio.strip()

    try:
        user_id = users.create_user(username, password1, age, bio)
    except sqlite3.IntegrityError:
        flash("Käyttäjänimi on jo käytössä.")
        return redirect("/register")

    file = request.files.get("image")
    if file and file.filename.endswith(".jpg"):
        image = file.read()
        if len(image) <= 100 * 1024:
            users.update_image(user_id, image)
        else:
            flash("Profiilikuva on liian suuri (max 100kb).")

    session["user_id"] = user_id
    session["username"] = username
    session["csrf_token"] = secrets.token_hex(16)

    return redirect(f"/user/{user_id}")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Logs in a user."""
    if request.method == "GET":
        return render_template("login.html")

    check_csrf()
    username = request.form["username"]
    password = request.form["password"]
    user_id = users.check_login(username, password)

    if user_id:
        session["user_id"] = user_id
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")
    return "ERROR: invalid username or password"


@app.route("/logout")
def logout():
    """Logs out the user."""
    session.clear()
    return redirect("/")


@app.route("/start_thread/<int:message_id>")
def start_thread(message_id):
    """Starts a conversation with the ad/message owner."""
    require_login()
    user_id = session["user_id"]
    msg = messages.get_message(message_id)
    if not msg:
        abort(404)

    owner_id = msg["user_id"]
    if owner_id == user_id:
        return "You cannot start a thread with yourself", 403

    thread_id = threads.get_or_create_thread(message_id, user_id, owner_id)
    return redirect(f"/thread/{thread_id}")


@app.route("/thread/<int:thread_id>")
def show_thread(thread_id):
    """Displays the messages of a thread and marks them as read."""
    require_login()
    user_id = session["user_id"]
    thread_info = threads.get_thread(thread_id)
    if not thread_info:
        abort(404)

    threads.mark_thread_as_read(thread_id, user_id)
    msgs = threads.get_messages(thread_id, user_id)
    message_id = thread_info["ad_id"]

    return render_template(
        "thread.html",
        messages=msgs,
        thread_id=thread_id,
        user_id=user_id,
        message_id=message_id
    )


@app.route("/send_message", methods=["POST"])
def send_message():
    """Sends a message in a thread."""
    require_login()
    check_csrf()
    thread_id = request.form["thread_id"]
    content = request.form["content"]
    if not content.strip():
        return redirect(f"/thread/{thread_id}")

    threads.send_message(thread_id, session["user_id"], content)
    return redirect(f"/thread/{thread_id}")


@app.route("/threads")
def user_threads():
    """Displays all threads of the logged-in user."""
    require_login()
    user_id = session["user_id"]
    thread_list = threads.get_user_threads(user_id)
    return render_template("threads.html", threads=thread_list)


