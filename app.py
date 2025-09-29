
from flask import Flask, render_template, request, redirect, url_for, session
import messenger
from helper import *

import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

app = Flask(__name__)
app.secret_key = SECRET_KEY

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/lobby", methods=["GET", "POST"])
def lobby():
    mode = request.args.get("mode", "join")  # read the mode from URL
    if request.method == "POST":
        code = request.form.get("code").strip()
        if(lobby_exists(code)):
            if mode == "join":
                return redirect(url_for("join_lobby", code=code))
            elif mode == "view":
                return redirect(url_for("view_lobby", code=code))
    return render_template("lobby.html")

@app.route("/join-lobby/<code>", methods=["GET", "POST"])
def join_lobby(code):
    path = lobby_file_path(code)

    # Validate
    if(not lobby_exists(code)):
        return redirect(url_for("lobby"))
    
    # Check if full
    if rows_in_csv(path) >= HARD_CSV_LIMIT:
        return redirect(url_for("view_lobby", code=code))
    
    if request.method == "POST":
        name = request.form.get("name")
        phone_raw = request.form.get("phone")
        phone = messenger.format_phone(phone_raw, region="CA") 
        note = request.form.get("note")

        if not phone:
            return redirect(url_for("join_lobby", code=code))

        add_to_csv(path, [name, phone, note, None])

        return redirect(url_for("view_lobby", code=code))
    
    return render_template("join-lobby.html", code=code)

@app.route("/view-lobby/<code>", methods=["GET", "POST"])
def view_lobby(code):
    path = lobby_file_path(code)
    entries = read_from_csv(path)
    return render_template("view-lobby.html", users=entries)

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if session.get("admin"):
        return redirect(url_for("admin_manager"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if password == ADMIN_PASSWORD and username == ADMIN_USERNAME:
            session["admin"] = True
            return redirect(url_for("admin_manager"))
        
    return render_template("admin-login.html")

@app.route("/admin/manager", methods=["GET", "POST"])
def admin_manager():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    
    # Show all CSV files
    lobbies = os.listdir(LOBBY_FOLDER)
    for index,lobby in enumerate(lobbies):
        lobbies[index],_ = os.path.splitext(lobby)

    # View a CSV file
    if request.method == "POST":
        row_index = int(request.form.get("row_index"))
        return redirect(url_for("admin_view", code=lobbies[row_index]))
    
    return render_template("admin-manager.html", lobbies=lobbies)

@app.route("/admin/manager/<code>", methods=["GET", "POST"])
def admin_view(code):
    path = lobby_file_path(code)

    # Populate
    entries = read_from_csv(path)

    if request.method == "POST":

        # Delete selected row
        row_index = int(request.form.get("row_index"))
        if 0 <= row_index < len(entries):
            entries.pop(row_index)

        rewrite_csv(path, entries)

        return redirect(url_for("admin_view", code=code))
    
    return render_template("admin-view-lobby.html", users=entries, code=code)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin_login"))

@app.route("/create-lobby", methods=["POST"])
def create_lobby():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    
    code = request.form.get("code")
    path = lobby_file_path(code)

    rewrite_csv(path,[])
    print("hello!")

    return redirect(url_for("admin_manager"))

@app.route("/generate-pairing", methods=["POST"])
def generate_pairing():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    
    code = request.form.get("lobby-code")
    path = lobby_file_path(code)

    # Populate
    entries = read_from_csv(path)

    # Error handle 
    if len(entries) < 2:
        return redirect(url_for("admin_view", code=code))
    
    # Shuffle 
    # Ent. Der.
    # A - > B
    # B - > C
    # C - > A
    derangement = derangement_shuffle(entries) 

    # Append gifter's phone number
    for index,value in enumerate(entries):
        entries[index][3] = derangement[index][1]

    rewrite_csv(path, entries)
    
    return redirect(url_for("admin_view", code=code))

@app.route("/send-message", methods=["POST"])
def send_message():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    
    code = request.form.get("lobby-code")
    path = lobby_file_path(code)

    # Populate
    entries = read_from_csv(path)

    # Error handle 
    if len(entries) == 0:
        return redirect(url_for("admin_view", code=code))
    for value in entries:
        if not messenger.format_phone(value[3]):
            return redirect(url_for("admin_view", code=code))
    
    # Send message
    for _,value in enumerate(entries):
        target_name = value[0]
        target_note = value[2]
        message = f"Event Code: '{code}'\nYour Person: '{target_name}'\nTheir Note: '{target_note}'"
        phone_number = value[3] # Gifter's phone number
        messenger.send_message(phone_number, message)
    
    return redirect(url_for("admin_view", code=code))

if __name__ == "__main__":
    os.makedirs(LOBBY_FOLDER, exist_ok=True)
    app.run()