from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

socketio = SocketIO(app)

active_sessions = {}

@app.route('/')
def home():
    return render_template('home.html', active_sessions=active_sessions)

@app.route('/create_session', methods=['POST'])
def create_session():
    session_name = request.form['session_name']
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        'name': session_name,
        'admin': request.remote_addr,
        'current_page': 1,
        'users': [],
        'pending_users': [],
        'pdf_file': None
    }
    session['user_type'] = 'admin'
    session['session_id'] = session_id
    return redirect(url_for('viewer', session_id=session_id))

@app.route('/join_session/<session_id>', methods=['POST'])
def join_session(session_id):
    if session_id in active_sessions:
        user_name = request.form['user_name']
        active_sessions[session_id]['pending_users'].append({
            'name': user_name,
            'ip': request.remote_addr
        })
        session['user_type'] = 'viewer'
        session['session_id'] = session_id
        session['user_name'] = user_name
        return redirect(url_for('viewer', session_id=session_id))
    return "Session not found", 404

@app.route('/viewer/<session_id>')
def viewer(session_id):
    if session_id not in active_sessions:
        return "Session not found", 404
    return render_template('viewer.html', 
                           session_id=session_id, 
                           pdf_file=active_sessions[session_id]['pdf_file'],
                           user_type=session.get('user_type'))

@app.route('/upload_pdf/<session_id>', methods=['POST'])
def upload_pdf(session_id):
    if session_id in active_sessions and session.get('user_type') == 'admin':
        if active_sessions[session_id]['pdf_file'] is None:
            uploaded_file = request.files['pdf_file']
            if uploaded_file and uploaded_file.filename.endswith('.pdf'):
                filename = f"{session_id}_{uploaded_file.filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                uploaded_file.save(file_path)
                active_sessions[session_id]['pdf_file'] = filename
                active_sessions[session_id]['current_page'] = 1  # Reset to first page
                socketio.emit('pdf_uploaded', {'filename': filename}, room=session_id)
                return "PDF uploaded successfully", 200
        else:
            return "PDF already uploaded", 400
    return "Failed to upload PDF", 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@socketio.on('connect')
def handle_connect():
    session_id = session.get('session_id')
    if session_id in active_sessions:
        join_room(session_id)
        if session.get('user_type') == 'viewer':
            emit('user_joined', {'name': session.get('user_name')}, room=session_id)
        elif session.get('user_type') == 'admin':
            emit('admin_connected', {'pdf_uploaded': active_sessions[session_id]['pdf_file'] is not None})

@socketio.on('change_page')
def handle_page_change(data):
    session_id = session.get('session_id')
    if session_id in active_sessions and session.get('user_type') == 'admin':
        active_sessions[session_id]['current_page'] = data['page']
        emit('page_changed', {'page': data['page']}, room=session_id)

@socketio.on('get_admin_page')
def handle_get_admin_page():
    session_id = session.get('session_id')
    if session_id in active_sessions:
        current_page = active_sessions[session_id]['current_page']
        emit('admin_page', {'page': current_page})

@socketio.on('accept_user')
def handle_accept_user(data):
    session_id = session.get('session_id')
    if session_id in active_sessions and session.get('user_type') == 'admin':
        user = next((u for u in active_sessions[session_id]['pending_users'] if u['name'] == data['user_name']), None)
        if user:
            active_sessions[session_id]['users'].append(user)
            active_sessions[session_id]['pending_users'].remove(user)
            emit('user_accepted', {'name': user['name']}, room=session_id)

@socketio.on('reject_user')
def handle_reject_user(data):
    session_id = session.get('session_id')
    if session_id in active_sessions and session.get('user_type') == 'admin':
        user = next((u for u in active_sessions[session_id]['pending_users'] if u['name'] == data['user_name']), None)
        if user:
            active_sessions[session_id]['pending_users'].remove(user)
            emit('user_rejected', {'name': user['name']}, room=session_id)

if __name__ == '__main__':
    socketio.run(app, debug=True)