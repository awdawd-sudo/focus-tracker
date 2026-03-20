# 📚 Focus Tracker — Stay Off Your Phone or Apply to McDonald's

A Python app that uses your webcam and computer vision to track whether you're actually studying. Look away for too long? It opens the McDonald's job application. Because if you won't learn, you'd better start somewhere.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Google-orange)

---

## 🎬 How It Works

1. Your webcam watches your face in real time using **MediaPipe Face Mesh**
2. Head pose estimation calculates whether you're looking at the screen or not
3. If you look down (phone check 👀) or away for **3 seconds** — a McDonald's job application opens in your browser
4. A red progress bar builds up as you drift away, so you get a warning before the inevitable

---

## 🚀 Setup

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/focus-tracker.git
cd focus-tracker
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run it**
```bash
python focus_tracker.py
```

Press **Q** to quit.

---

## ⚙️ Configuration

At the top of `focus_tracker.py` you can adjust:

| Setting | Default | What it does |
|---|---|---|
| `DISTRACTION_SECONDS` | `3` | Seconds before getting busted |
| `PITCH_DOWN_THRESHOLD` | `20` | Degrees of head tilt down to count |
| `YAW_THRESHOLD` | `40` | Degrees of sideways turn to count |
| `COOLDOWN_SECONDS` | `30` | Gap between McDonald's openings |

---

## 🛠️ Tech Stack

- **Python 3.8+**
- **OpenCV** — webcam feed and UI overlay
- **MediaPipe** — face mesh and head pose estimation (468 facial landmarks)
- **NumPy** — 3D pose math (solvePnP)
- **webbrowser** — the punishment delivery system

---

## 📋 Requirements

- Python 3.8 or higher
- A webcam
- A desire to actually learn something

---

## 💡 Ideas for Future Features

- [ ] Eye tracking (detect when eyes close or drift)
- [ ] Session stats saved to a file
- [ ] Custom punishment URLs (not just McDonald's)
- [ ] Sound alert before the browser opens
- [ ] Pomodoro timer integration

---

*Built for fun. Stay focused. 📚*
