# ⚡ BuzzerX — Real-Time Contest Buzzer System

A full-stack real-time buzzer system for quiz contests and competitions.
Built with Python (Flask + SocketIO).

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the server
```bash
python app.py
```

### 3. Open in browser
```
http://localhost:5000
```

---

## 🎮 How It Works

### Players
- Go to `http://localhost:5000`
- Enter name + email → join as **Player**
- Press the glowing **BUZZ IN** button (or press Space/Enter)
- First player to buzz wins the round!

### Host
- Go to `http://localhost:5000`
- Enter name + email → join as **Host**
- Monitor all players and their scores
- When someone buzzes:
  - Award `+1 point` for correct answer
  - Deduct `−1 point` for wrong answer
  - Click **Reset Buzzer** for next round
- Can also award/deduct points per player individually
- Can kick players from the game

---

## 🌐 Multiplayer Setup

To play across devices on the same network:
1. Find your local IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. Players connect to `http://YOUR_IP:5000`

---

## 📁 File Structure
```
buzzer/
├── app.py              # Flask server + SocketIO logic
├── requirements.txt    # Python dependencies
├── templates/
│   ├── login.html      # Sign-in page
│   ├── player.html     # Player buzzer page
│   └── host.html       # Host control panel
└── README.md
```
