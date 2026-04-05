from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import time
import uuid

app = Flask(__name__)
app.secret_key = 'buzzer_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Game state
players = {}       # sid -> {name, email, score}
buzzer_winner = None
buzzer_locked = False
buzz_time = None
host_sid = None

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/join', methods=['POST'])
def join():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    role = request.form.get('role', 'player')
    if not name or not email:
        return redirect('/')
    session['name'] = name
    session['email'] = email
    session['role'] = role
    if role == 'host':
        return redirect(url_for('host_panel'))
    return redirect(url_for('player_panel'))

@app.route('/player')
def player_panel():
    if 'name' not in session:
        return redirect('/')
    return render_template('player.html', name=session['name'], email=session['email'])

@app.route('/host')
def host_panel():
    if 'name' not in session:
        return redirect('/')
    return render_template('host.html', name=session['name'])

@app.route('/leave')
def leave():
    session.clear()
    return redirect('/')

# ── Socket Events ──────────────────────────────────────────────
@socketio.on('connect')
def on_connect():
    pass

@socketio.on('register_player')
def register_player(data):
    global host_sid
    sid = request.sid
    role = data.get('role', 'player')
    name = data.get('name', 'Unknown')
    email = data.get('email', '')

    if role == 'host':
        host_sid = sid
        join_room('host')
        emit('host_registered', {'message': 'You are the host'})
        # Send current players list
        emit('players_update', {'players': list(players.values())})
    else:
        players[sid] = {
            'sid': sid,
            'name': name,
            'email': email,
            'score': 0,
            'buzzed': False
        }
        join_room('players')
        emit('registered', {'name': name, 'buzzer_locked': buzzer_locked})
        # Notify host
        socketio.emit('players_update', {'players': list(players.values())}, room='host')
        # Notify all of new player
        socketio.emit('player_joined', {'name': name, 'count': len(players)}, include_self=False)

@socketio.on('buzz')
def on_buzz(data):
    global buzzer_winner, buzzer_locked, buzz_time
    sid = request.sid

    if buzzer_locked or sid not in players:
        emit('buzz_rejected', {'reason': 'Buzzer is locked!' if buzzer_locked else 'Not registered'})
        return

    buzzer_locked = True
    buzzer_winner = players[sid]
    buzz_time = time.time()
    players[sid]['buzzed'] = True

    # Tell everyone who buzzed
    socketio.emit('buzz_winner', {
        'name': buzzer_winner['name'],
        'email': buzzer_winner['email'],
        'sid': sid,
        'time': buzz_time
    })
    # Update host
    socketio.emit('players_update', {'players': list(players.values())}, room='host')

@socketio.on('reset_buzzer')
def reset_buzzer():
    global buzzer_winner, buzzer_locked, buzz_time
    if request.sid != host_sid:
        return
    buzzer_winner = None
    buzzer_locked = False
    buzz_time = None
    for sid in players:
        players[sid]['buzzed'] = False
    socketio.emit('buzzer_reset', {})
    socketio.emit('players_update', {'players': list(players.values())}, room='host')

@socketio.on('award_point')
def award_point(data):
    if request.sid != host_sid:
        return
    sid = data.get('sid')
    if sid in players:
        players[sid]['score'] += 1
        socketio.emit('score_update', {
            'sid': sid,
            'name': players[sid]['name'],
            'score': players[sid]['score'],
            'players': list(players.values())
        })
        socketio.emit('players_update', {'players': list(players.values())}, room='host')

@socketio.on('deduct_point')
def deduct_point(data):
    if request.sid != host_sid:
        return
    sid = data.get('sid')
    if sid in players:
        players[sid]['score'] = max(0, players[sid]['score'] - 1)
        socketio.emit('score_update', {
            'sid': sid,
            'name': players[sid]['name'],
            'score': players[sid]['score'],
            'players': list(players.values())
        })
        socketio.emit('players_update', {'players': list(players.values())}, room='host')

@socketio.on('kick_player')
def kick_player(data):
    if request.sid != host_sid:
        return
    sid = data.get('sid')
    if sid in players:
        name = players[sid]['name']
        del players[sid]
        socketio.emit('kicked', {'message': 'You were removed by the host'}, room=sid)
        socketio.emit('players_update', {'players': list(players.values())}, room='host')
        socketio.emit('player_left', {'name': name, 'count': len(players)})

@socketio.on('disconnect')
def on_disconnect():
    global host_sid, buzzer_winner, buzzer_locked
    sid = request.sid
    if sid == host_sid:
        host_sid = None
    if sid in players:
        name = players[sid]['name']
        del players[sid]
        if buzzer_winner and buzzer_winner.get('sid') == sid:
            buzzer_winner = None
            buzzer_locked = False
            socketio.emit('buzzer_reset', {})
        socketio.emit('players_update', {'players': list(players.values())}, room='host')
        socketio.emit('player_left', {'name': name, 'count': len(players)})

if __name__ == '__main__':
    print("\n🎯 Buzzer Contest Server Running!")
    print("   Open: http://localhost:5000\n")
    import os
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
