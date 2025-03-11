from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
from flask_socketio import join_room, leave_room, send, SocketIO, emit
import random
from string import ascii_uppercase
from datetime import datetime
import sqlite3

from lib import caesar_encrypt, caesar_decrypt

app = Flask(__name__)
app.config["SECRET_KEY"] = 'the_most_random_thing'
socketio = SocketIO(app)
rooms = {}
conn = sqlite3.connect('main.db', check_same_thread=False)
c = conn.cursor()
def create_tables():
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')

    
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT,
        user TEXT,
        encrypted_message TEXT,
        datetime TEXT,
        FOREIGN KEY (user) REFERENCES users (username)
    )''')
    
    conn.commit()

create_tables()

rooms = {}
def generate_unique_code(length):
    while True:
        code = "".join(random.choice(ascii_uppercase) for _ in range(length))
        if code not in rooms:
            break
    return code


@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        name = session.get('username') or f'Anonymous {random.randint(1, 1000)}'
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)
        
        if join != False and not code:
            return render_template("home.html", error="Please enter a room code.", code=code)
        
        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", code=code)
        
        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html", username=session.get('username'))

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/tos')
def tos():
    return render_template('tos.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash('Please fill out all fields.', 'error')
            return redirect(url_for('signup'))

        try:
            c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
            conn.commit()
            session['username'] = username
            flash('User registered successfully!', 'success')
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            flash('Error: Username or email already exists.', 'error')
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')


        if not username or not password:
            flash('Please fill out all fields.', 'error')
            return redirect(url_for('login'))

        user = c.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and user[3]==password:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    if 'username' not in session:
        flash('You need to be logged in to access this page.', 'error')
        return redirect(url_for('login'))

    username = session['username']
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()

    if request.method == 'POST':
        password = request.form.get('password')
        if user and user[3] == password:
            user_details = {
                "username": user[1],
                "email": user[2],
            }
            flash('Password verified successfully!', 'success')
        else:
            flash('Incorrect password.', 'error')

    return render_template('user_profile.html', user=username, email=user[2])

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))
    
    c.execute("SELECT user, encrypted_message FROM messages WHERE room_number=?", (room,))
    encrypted_messages = c.fetchall()
    decrypted_messages = []
    for user, encrypted_message in encrypted_messages:
        decrypted_message = caesar_decrypt(encrypted_message)
        decrypted_messages.append({"user": user, "message": decrypted_message})

    return render_template("room.html", code=room, messages=decrypted_messages)

@app.route("/get_users/<room>")
def get_users(room):
    c.execute("SELECT DISTINCT user FROM messages WHERE room_number=?", (room,))
    users = c.fetchall()
    return jsonify(users=[user[0] for user in users], count=len(users))

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }

    encrypted_message = caesar_encrypt(data["data"])
    c.execute("INSERT INTO messages (room_number, user, encrypted_message, datetime) VALUES (?, ?, ?, ?)",
              (room, session.get("username"), encrypted_message, datetime.now()))
    conn.commit()
    send(content, to=room) 
    print(f"{session.get('name')} said: {data['data']}")

@app.route('/modify_account', methods=['GET', 'POST'])
def modify_account():
    if 'username' not in session:
        flash('You need to be logged in to access this page.', 'error')
        return redirect(url_for('login'))

    username = session['username']

    if request.method == "POST":
        new_username = request.form.get('new_username')
        new_email = request.form.get('new_email')
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')


        if new_username:
            c.execute('UPDATE users SET username = ? WHERE username = ?', (new_username, username))
            session['username'] = new_username
            flash('Username updated successfully!', 'success')


        if new_email:
            c.execute('UPDATE users SET email = ? WHERE username = ?', (new_email, username))
            flash('Email updated successfully!', 'success')

        if old_password and new_password and confirm_password:
            user = c.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if user and user[3] == old_password:
                if new_password == confirm_password:
                    c.execute('UPDATE users SET password = ? WHERE username = ?', (new_password, username))
                    flash('Password updated successfully!', 'success')
                else:
                    flash('New passwords do not match.', 'error')
            else:
                flash('Old password is incorrect.', 'error')

        conn.commit()

        return redirect(url_for('modify_account'))
    return render_template("modify_account.html", username=username)

    

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'username' not in session:
        flash('You need to be logged in to delete your account.', 'error')
        return redirect(url_for('login'))

    username = session['username']

    c.execute('DELETE FROM users WHERE username = ?', (username,))
    c.execute('DELETE FROM messages WHERE user = ?', (username,))
    conn.commit()

    session.clear()
    flash('Your account has been successfully deleted.', 'success')
    return redirect(url_for('home'))


@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room!"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect_request")
def disconnect_request():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]

    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")


    socketio.emit("force_disconnect")

if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
