from flask import Flask, render_template, redirect, url_for, request, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from models import db, User, Message, Group

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['UPLOAD_FOLDER'] = 'static/media'
socketio = SocketIO(app, async_mode='eventlet')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect unauthorized users to login page
db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    groups = Group.query.all()
    return render_template('index.html', groups=groups, user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files['file']
    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    msg = Message(sender_id=current_user.id, media_path=path)
    db.session.add(msg)
    db.session.commit()
    socketio.emit('new_message', {
        'username': current_user.username,
        'media': path
    }, broadcast=True)
    return '', 200

@socketio.on('send_message')
def handle_send_message(data):
    content = data['message']
    group_id = data.get('group_id')
    msg = Message(sender_id=current_user.id, content=content, group_id=group_id)
    db.session.add(msg)
    db.session.commit()
    room = f"group_{group_id}" if group_id else None
    emit('new_message', {
        'username': current_user.username,
        'content': content
    }, room=room, broadcast=not room)

@socketio.on('join')
def on_join(data):
    room = f"group_{data['group_id']}"
    join_room(room)
    emit('status', {'msg': f'{current_user.username} has joined the room.'}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = f"group_{data['group_id']}"
    leave_room(room)
    emit('status', {'msg': f'{current_user.username} has left the room.'}, room=room)

@app.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        group_name = request.form['group_name']
        if Group.query.filter_by(name=group_name).first():
            flash('Group name already exists.')
            return redirect(url_for('create_group'))
        group = Group(name=group_name)
        group.members.append(current_user)
        db.session.add(group)
        db.session.commit()
        flash('Group created successfully!')
        return redirect(url_for('index'))
    return render_template('create_group.html')

@app.route('/group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def group_chat(group_id):
    group = Group.query.get_or_404(group_id)
    if current_user not in group.members:
        flash('You’re not a member of this group.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        content = request.form['message']
        if content:
            message = GroupMessage(content=content, user_id=current_user.id, group_id=group_id)
            db.session.add(message)
            db.session.commit()
    messages = GroupMessage.query.filter_by(group_id=group_id).order_by(GroupMessage.timestamp).all()
    return render_template('group_chat.html', group=group, messages=messages)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
