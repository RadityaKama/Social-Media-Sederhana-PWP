import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
from flask_socketio import SocketIO, join_room, emit
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'batavia_sovereign_final_key_v100'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'social_media_app'

mysql = MySQL(app)
socketio = SocketIO(app, cors_allowed_origins="*")

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

TRANSLATIONS = {
    'id': {'home': 'Beranda', 'explore': 'Jelajah', 'messages': 'Surat', 'notif': 'Kabar', 'profile': 'Profil', 'admin': 'Gubernur', 'logout': 'Keluar', 'post_ph': 'Apa yang sedang terjadi di Batavia?', 'post_btn': 'Terbitkan', 'edit': 'Ubah Data', 'news': 'Warta Kota', 'follow': 'Ikuti', 'unfollow': 'Berhenti Mengikuti'},
    'en': {'home': 'Home', 'explore': 'Explore', 'messages': 'Letters', 'notif': 'News', 'profile': 'Profile', 'admin': 'Governor', 'logout': 'Logout', 'post_ph': 'What is happening in Batavia?', 'post_btn': 'Publish', 'edit': 'Edit Profile', 'news': 'City News', 'follow': 'Follow', 'unfollow': 'Unfollow'}
}

@app.context_processor
def inject():
    lang = session.get('lang', 'id')
    return dict(t=TRANSLATIONS[lang], lang=lang)

@app.route('/set_lang/<lang_code>')
def set_lang(lang_code):
    session['lang'] = lang_code
    return redirect(url_for('auth'))

@app.route('/')
def root():
    if 'loggedin' in session: return redirect(url_for('index'))
    if 'lang' in session: return redirect(url_for('auth'))
    return render_template('landing.html')

@app.route('/auth')
def auth():
    if 'loggedin' in session: return redirect(url_for('index'))
    return render_template('auth.html')

def get_shared_data(uid):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM users WHERE id_user = %s', (uid,))
    user = cur.fetchone()
    cur.execute('''SELECT id_user, username, nama FROM users 
                   WHERE id_user != %s AND id_user NOT IN (SELECT target FROM follows WHERE id_user = %s)
                   ORDER BY RAND() LIMIT 4''', (uid, uid))
    sugg = cur.fetchall()
    cur.execute('SELECT tag_name FROM admin_trending ORDER BY created_at DESC LIMIT 5')
    trends = cur.fetchall()
    return user, sugg, trends

@app.route('/feed')
def index():
    if 'loggedin' not in session: return redirect(url_for('auth'))
    uid = session['id']
    user, sugg, trends = get_shared_data(uid)
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = '''SELECT p.*, u.username, u.nama, u.role,
               (SELECT COUNT(*) FROM likes WHERE id_postingan = p.id_postingan) as likes,
               (SELECT COUNT(*) FROM likes WHERE id_postingan = p.id_postingan AND id_user = %s) as is_liked
               FROM postingan p JOIN users u ON p.id_user = u.id_user 
               WHERE (p.file NOT LIKE 'http%%' OR p.file IS NULL)
               ORDER BY p.created_at DESC'''
    cur.execute(query, (uid,))
    posts = cur.fetchall()
    return render_template('index.html', p='home', u=user, posts=posts, sugg=sugg, trends=trends)

@app.route('/explore')
def explore():
    if 'loggedin' not in session: return redirect(url_for('auth'))
    uid = session['id']
    user, sugg, trends = get_shared_data(uid)
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('''SELECT p.*, u.username FROM postingan p JOIN users u ON p.id_user = u.id_user 
                   WHERE p.file LIKE 'http%%'
                   ORDER BY p.created_at DESC LIMIT 5''')
    news = cur.fetchall()
    cur.execute('''SELECT p.*, u.username, u.role,
                   (SELECT COUNT(*) FROM likes WHERE id_postingan = p.id_postingan) as likes
                   FROM postingan p JOIN users u ON p.id_user = u.id_user
                   WHERE (p.file NOT LIKE 'http%%' OR p.file IS NULL)
                   ORDER BY RAND() LIMIT 20''')
    posts = cur.fetchall()
    return render_template('index.html', p='explore', u=user, news=news, posts=posts, sugg=sugg, trends=trends)

@app.route('/notifications')
def notifications():
    if 'loggedin' not in session: return redirect(url_for('auth'))
    uid = session['id']
    user, sugg, trends = get_shared_data(uid)
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM notifications WHERE id_user = %s ORDER BY created_at DESC LIMIT 30', (uid,))
    notifs = cur.fetchall()
    cur.execute('UPDATE notifications SET is_read = 1 WHERE id_user = %s', (uid,))
    mysql.connection.commit()
    return render_template('index.html', p='notif', u=user, notifs=notifs, sugg=sugg, trends=trends)

@app.route('/profile')
@app.route('/profile/<int:user_id>')
def profile(user_id=None):
    if 'loggedin' not in session: return redirect(url_for('auth'))
    uid = session['id']
    target_id = user_id if user_id else uid
    user, sugg, trends = get_shared_data(uid)
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM users WHERE id_user = %s', (target_id,))
    target = cur.fetchone()
    if not target: return redirect(url_for('index'))
    cur.execute('''SELECT p.*, (SELECT COUNT(*) FROM likes WHERE id_postingan = p.id_postingan) as likes 
                   FROM postingan p WHERE id_user = %s AND (p.file NOT LIKE 'http%%' OR p.file IS NULL) 
                   ORDER BY created_at DESC''', (target_id,))
    posts = cur.fetchall()
    cur.execute('SELECT COUNT(*) as c FROM postingan WHERE id_user = %s AND (file NOT LIKE "http%%" OR file IS NULL)', (target_id,))
    post_count = cur.fetchone()['c']
    cur.execute('SELECT COUNT(*) as c FROM follows WHERE target = %s', (target_id,))
    followers_count = cur.fetchone()['c']
    cur.execute('SELECT COUNT(*) as c FROM follows WHERE id_user = %s', (target_id,))
    following_count = cur.fetchone()['c']
    is_following = False
    if uid != target_id:
        cur.execute('SELECT * FROM follows WHERE id_user = %s AND target = %s', (uid, target_id))
        is_following = cur.fetchone() is not None
    return render_template('index.html', p='profile', u=user, target=target, posts=posts, 
                           me=(uid==target_id), following=is_following, sugg=sugg, trends=trends,
                           stats={'post': post_count, 'follower': followers_count, 'following': following_count})

@app.route('/messages')
@app.route('/messages/<int:chat_id>')
def messages(chat_id=None):
    if 'loggedin' not in session: return redirect(url_for('auth'))
    uid = session['id']
    user, sugg, trends = get_shared_data(uid)
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('''SELECT u.id_user, u.username, u.nama, u.role FROM users u
                   WHERE u.id_user != %s AND u.id_user IN 
                   (SELECT target FROM follows WHERE id_user=%s UNION SELECT id_user FROM follows WHERE target=%s)''', (uid, uid, uid))
    contacts = cur.fetchall()
    msgs = []
    rcv = None
    if chat_id:
        cur.execute('SELECT * FROM users WHERE id_user = %s', (chat_id,))
        rcv = cur.fetchone()
        cur.execute('''SELECT * FROM messages 
                       WHERE (sender_id=%s AND receiver_id=%s) OR (sender_id=%s AND receiver_id=%s) 
                       ORDER BY created_at ASC''', (uid, chat_id, chat_id, uid))
        msgs = cur.fetchall()
    return render_template('chat.html', u=user, contacts=contacts, rcv=rcv, msgs=msgs)

@app.route('/admin')
def admin():
    if 'loggedin' not in session or session.get('role') != 'admin': return redirect(url_for('index'))
    uid = session['id']
    user, _, _ = get_shared_data(uid)
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    cur.execute('SELECT * FROM postingan ORDER BY created_at DESC LIMIT 50')
    posts = cur.fetchall()
    return render_template('admin.html', u=user, users=users, posts=posts)

@app.route('/api/auth', methods=['POST'])
def api_auth():
    data = request.get_json()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if data['action'] == 'login':
        username = data['username'].strip()
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        acc = cur.fetchone()
        if acc:
            valid = False
            try:
                if check_password_hash(acc['password'], data['password']): valid = True
            except: pass
            if not valid and acc['password'] == data['password']: valid = True 
            if not valid and acc['password'] == data['password'].strip(): valid = True
            if valid:
                session['loggedin'] = True
                session['id'] = acc['id_user']
                session['role'] = acc['role']
                session['username'] = acc['username']
                return jsonify({'status': 'success'})
        return jsonify({'status': 'error', 'message': 'Kredensial tidak valid'})
    elif data['action'] == 'register':
        cur.execute('SELECT * FROM users WHERE username = %s', (data['username'],))
        if cur.fetchone(): return jsonify({'status': 'error', 'message': 'Username sudah ada'})
        hashed = generate_password_hash(data['password'])
        cur.execute('INSERT INTO users (username, nama, email, password, role) VALUES (%s, %s, %s, %s, %s)',
                    (data['username'], data['fullname'], data['email'], hashed, data['role']))
        mysql.connection.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})

@app.route('/api/post', methods=['POST'])
def api_post():
    if 'loggedin' not in session: return jsonify({'status':'error'})
    caption = request.form.get('caption')
    file = request.files.get('file')
    is_news = request.form.get('is_news')
    link_url = request.form.get('link_url')
    filename = None
    if is_news == '1':
        filename = link_url
    elif file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO postingan (id_user, caption, file) VALUES (%s, %s, %s)',
                (session['id'], caption, filename))
    mysql.connection.commit()
    return jsonify({'status': 'success'})

@app.route('/api/act', methods=['POST'])
def api_act():
    if 'loggedin' not in session: return jsonify({'status':'error'})
    data = request.get_json()
    uid = session['id']
    cur = mysql.connection.cursor()
    if data['type'] == 'like':
        try:
            cur.execute('INSERT INTO likes (id_user, id_postingan) VALUES (%s, %s)', (uid, data['pid']))
            mysql.connection.commit()
            return jsonify({'status': 'liked'})
        except:
            cur.execute('DELETE FROM likes WHERE id_user=%s AND id_postingan=%s', (uid, data['pid']))
            mysql.connection.commit()
            return jsonify({'status': 'unliked'})
    elif data['type'] == 'follow':
        try:
            cur.execute('INSERT INTO follows (id_user, target) VALUES (%s, %s)', (uid, data['tid']))
            cur.execute('INSERT INTO notifications (id_user, message) VALUES (%s, %s)', 
                       (data['tid'], f"@{session['username']} mulai mengikuti anda."))
            mysql.connection.commit()
            return jsonify({'status': 'success'})
        except: return jsonify({'status': 'error'})
    elif data['type'] == 'trend' and session.get('role') == 'admin':
        cur.execute('INSERT INTO admin_trending (tag_name, post_count) VALUES (%s, 0)', (data['tag'],))
        mysql.connection.commit()
        return jsonify({'status': 'success'})
    elif data['type'] == 'update_profile':
        cur.execute('UPDATE users SET nama=%s, bio=%s WHERE id_user=%s', (data['fullname'], data['bio'], uid))
        mysql.connection.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('root'))

@socketio.on('join')
def on_join(data):
    join_room(data['room'])

@socketio.on('send_message')
def on_message(data):
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO messages (sender_id, receiver_id, message) VALUES (%s, %s, %s)',
                (session['id'], data['receiver_id'], data['message']))
    mysql.connection.commit()
    emit('receive_message', {'msg': data['message'], 'sender_id': session['id']}, room=data['room'])

if __name__ == '__main__':
    socketio.run(app, debug=True)