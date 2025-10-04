"""
Tämä moduuli sisältää Friend App -sovelluksen päälogiikan.
"""

import re
import secrets
import sqlite3
from flask import Flask, abort, redirect, render_template, request, session, make_response

import config
import forum
import messages
import users
import threads  

app = Flask(__name__)
app.secret_key = config.secret_key


def check_csrf():
    """Tarkistaa CSRF-tokenin."""
    if request.form.get("csrf_token") != session.get("csrf_token"):
        abort(403)


def require_login():
    """Varmistaa, että käyttäjä on kirjautunut sisään."""
    if "user_id" not in session:
        abort(403)


@app.route("/")
def index():
    """Näyttää etusivun viestit."""
    all_messages = messages.get_messages()
    return render_template("index.html", messages=all_messages)


@app.route("/user/<int:user_id>")
def show_user(user_id):
    """Näyttää käyttäjän profiilin ja viestit."""
    user = users.get_user(user_id)
    if not user:
        abort(404)
    user_messages = users.get_messages(user_id)
    return render_template("show_user.html", user=user, messages=user_messages)


@app.route("/add_image", methods=["GET", "POST"])
def add_image():
    """Mahdollistaa profiilikuvan lisäämisen."""
    require_login()

    if request.method == "GET":
        return render_template("add_image.html")

    file = request.files["image"]
    if not file.filename.endswith(".jpg"):
        return "VIRHE: väärä tiedostomuoto"

    image = file.read()
    if len(image) > 100 * 1024:
        return "VIRHE: liian suuri kuva"

    user_id = session["user_id"]
    users.update_image(user_id, image)
    return redirect(f"/user/{user_id}")


@app.route("/image/<int:user_id>")
def show_image(user_id):
    """Näyttää käyttäjän profiilikuvan."""
    image = users.get_image(user_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response


@app.route("/find_message")
def find_message():
    """Hakee viestejä hakusanan perusteella."""
    query = request.args.get("query")
    results = messages.find_messages(query) if query else []
    return render_template("find_message.html", query=query or "", results=results)


@app.route("/message/<int:message_id>")
def show_message(message_id):
    """Näyttää yksittäisen viestin ja siihen liittyvät threadit."""
    message = messages.get_message(message_id)
    if not message:
        abort(404)

    classes_list = messages.get_classes(message_id)
    user_id = session.get("user_id")

    threads_list = []
    if user_id:
        if user_id == message["user_id"]:
            threads_list = threads.get_threads_by_message(message_id)

    return render_template(
        "show_message.html",
        message=message,
        classes=classes_list,
        threads=threads_list
    )


@app.route("/new_message")
def new_message():
    """Näyttää uuden viestin lomakkeen."""
    require_login()
    classes_list = messages.get_all_classes()
    return render_template("new_message.html", classes=classes_list)


@app.route("/create_message", methods=["POST"])
def create_message():
    """Luo uuden viestin."""
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
    classes_selected = []

    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes_selected.append((class_title, class_value))

    messages.add_message(title, description, age, user_id, classes_selected)
    return redirect("/")


@app.route("/edit_message/<int:message_id>")
def edit_message(message_id):
    """Näyttää viestin muokkauslomakkeen."""
    require_login()
    message = messages.get_message(message_id)
    if not message:
        abort(404)
    if message["user_id"] != session["user_id"]:
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
    """Päivittää olemassa olevan viestin."""
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
    classes_selected = []

    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes_selected.append((class_title, class_value))

    messages.update_message(message_id, title, description, classes_selected)
    return redirect(f"/message/{message_id}")


@app.route("/remove_message/<int:message_id>", methods=["GET", "POST"])
def remove_message(message_id):
    """Poistaa viestin tai näyttää poiston vahvistuslomakkeen."""
    require_login()
    message = messages.get_message(message_id)
    if not message:
        abort(404)
    if message["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_message.html", message=message)

    check_csrf()
    if "remove" in request.form:
        messages.remove_message(message_id)
        return redirect("/")
    return redirect(f"/message/{message_id}")


@app.route("/register")
def register():
    """Näyttää rekisteröitymislomakkeen."""
    return render_template("register.html")


@app.route("/create", methods=["POST"])
def create():
    """Luo uuden käyttäjän."""
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"

    try:
        user_id = users.create_user(username, password1)
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    session["user_id"] = user_id
    session["username"] = username
    session["csrf_token"] = secrets.token_hex(16)
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Kirjautuminen käyttäjänä."""
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]
    user_id = users.check_login(username, password)

    if user_id:
        session["user_id"] = user_id
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")
    return "VIRHE: väärä tunnus tai salasana"


@app.route("/logout")
def logout():
    """Kirjaa käyttäjän ulos."""
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")


@app.route("/start_thread/<int:message_id>")
def start_thread(message_id):
    """Aloittaa keskustelun ilmoituksen tekijän kanssa."""
    require_login()
    user_id = session["user_id"]

    msg = messages.get_message(message_id)
    if not msg:
        abort(404)

    owner_id = msg["user_id"]
    if owner_id == user_id:
        return "Et voi aloittaa keskustelua itsesi kanssa", 403

    thread_id = threads.get_or_create_thread(message_id, user_id, owner_id)
    return redirect(f"/thread/{thread_id}")


@app.route("/thread/<int:thread_id>")
def show_thread(thread_id):
    """Näyttää keskustelun viestit."""
    require_login()
    user_id = session["user_id"]
    msgs = threads.get_messages(thread_id)
    return render_template("thread.html", messages=msgs, thread_id=thread_id, user_id=user_id)


@app.route("/send_message", methods=["POST"])
def send_message():
    """Lähettää viestin keskustelussa."""
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
    """Näyttää käyttäjän kaikki keskustelut."""
    require_login()
    user_id = session["user_id"]
    thread_list = threads.get_user_threads(user_id)
    return render_template("threads.html", threads=thread_list)



