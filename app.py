import random, tempfile, os, re, time, requests, numpy as np
from flask import Flask, render_template, request, jsonify
from voice import embed
import config

app = Flask(__name__)
AUDIO_EXT = (".wav", ".mp3", ".m4a", ".ogg", ".opus", ".aac",
             ".flac", ".amr", ".3gp", ".mp4", ".wma", ".webm")
ENROLL_PIN = getattr(config, "ENROLL_PIN", "4321")
CACHE, DB = {}, {}
state = {"fails": 0}
PHRASES = [
    "Please open the gate for me.",
    "Today I am testing my smart voice lock system.",
    "My voice is used to verify my identity.",
    "Please recognize my voice and open the gate.",
    "Please verify my voice before granting access.",
    "The security system is ready for testing.",
    "My voice should be recognized correctly.",
    "Only the registered user should get access.",
    "The voice authentication process is starting now.",
    "The microphone is recording my voice clearly.",
]

def rebuild():
    DB.clear()
    os.makedirs("samples", exist_ok=True)
    for name in sorted(os.listdir("samples")):
        folder = os.path.join("samples", name)
        if not os.path.isdir(folder):
            continue
        embs = []
        for f in sorted(os.listdir(folder)):
            if not f.lower().endswith(AUDIO_EXT):
                continue
            p = os.path.join(folder, f)
            if p not in CACHE:
                try:
                    CACHE[p] = embed(p)
                except Exception as ex:
                    print("skip", p, ex)
                    CACHE[p] = None
            if CACHE[p] is not None:
                embs.append(CACHE[p])
        if embs:
            DB[name] = np.array(embs)
    print("Enrolled:", {n: len(m) for n, m in DB.items()})

def person_scores(e):
    return {n: float(np.mean(np.sort(m @ e)[::-1][:3])) for n, m in DB.items()}

def telegram_alert(msg):
    for cid in config.TELEGRAM_CHAT_IDS:
        try:
            requests.post(
                f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage",
                data={"chat_id": cid, "text": msg}, timeout=5)
        except Exception as e:
            print("telegram error:", e)

def open_gate():
    try:
        requests.get(config.ESP32_URL, params={"key": config.ESP32_KEY}, timeout=4)
    except Exception as e:
        print("esp32 error:", e)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/enroll")
def enroll_page():
    return render_template("enroll.html")

@app.route("/phrase")
def phrase():
    return jsonify(phrase=random.choice(PHRASES))

@app.route("/enroll_info")
def enroll_info():
    return jsonify({n: len(m) for n, m in DB.items()})

@app.route("/enroll_upload", methods=["POST"])
def enroll_upload():
    if request.form.get("pin") != ENROLL_PIN:
        return jsonify(ok=False, msg="Galat PIN")
    name = request.form.get("name", "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_]{2,20}", name):
        return jsonify(ok=False, msg="Naam sirf letters/numbers (2-20)")
    folder = os.path.join("samples", name)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"web_{int(time.time()*1000)}.wav")
    request.files["audio"].save(path)
    try:
        embed(path)
    except Exception as ex:
        os.remove(path)
        return jsonify(ok=False, msg=f"Sample kharab/chhota: {ex}")
    rebuild()
    return jsonify(ok=True, msg=f"{name}: {len(DB[name])} samples ho gaye")

@app.route("/verify", methods=["POST"])
def verify():
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as t:
        request.files["audio"].save(t.name)
        path = t.name
    try:
        e = embed(path)
    except Exception as ex:
        return jsonify(ok=False, msg=f"Audio problem: {ex}")
    finally:
        os.remove(path)

    scores = person_scores(e)
    best_name = max(scores, key=scores.get)
    best = scores[best_name]
    print({n: round(s, 3) for n, s in scores.items()}, "-> best:", best_name)
    info = f"(score {best:.2f}, chahiye {config.THRESHOLD})"

    if best >= config.THRESHOLD:
        state["fails"] = 0
        open_gate()
        return jsonify(ok=True, msg=f"Welcome {best_name}! Gate is opening. {info}")

    state["fails"] += 1
    if state["fails"] >= config.MAX_FAILS:
        telegram_alert("🚨 Security Alert: 3 failed voice authentication attempts detected at the gate.")
        state["fails"] = 0
        return jsonify(ok=False, msg=f"3 failed attempts. Owners have been notified. {info}")
    left = config.MAX_FAILS - state["fails"]
    return jsonify(ok=False, msg=f"Voice not recognized. {left} attempt(s) remaining. {info}")

if __name__ == "__main__":
    rebuild()
    app.run(host="0.0.0.0", port=5000, ssl_context="adhoc")