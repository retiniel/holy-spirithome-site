import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

load_dotenv()

MAIL_HOST = os.getenv("MAIL_HOST", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

LOG_FILE = "submissions.log"

def log_submission(kind, data):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.utcnow().isoformat()}Z | {kind} | {data}\n")

def send_email(subject, html_body, sender_display=None, reply_to=None):
    if not MAIL_USERNAME or not MAIL_PASSWORD or not RECEIVER_EMAIL:
        return False, "Mail server not configured."

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{sender_display or 'Holy Spirit Home'} <{MAIL_USERNAME}>"
    msg["To"] = RECEIVER_EMAIL
    if reply_to:
        msg["Reply-To"] = reply_to

    part = MIMEText(html_body, "html")
    msg.attach(part)

    try:
        server = smtplib.SMTP(MAIL_HOST, MAIL_PORT, timeout=15)
        server.ehlo()
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_USERNAME, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        return True, None
    except Exception as e:
        return False, str(e)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit_prayer", methods=["POST"])
def submit_prayer():
    data = request.json or request.form
    name = data.get("name", "Anonyme")
    email = data.get("email", "")
    subject_text = data.get("subject", "")
    details = data.get("details", "")

    if not subject_text.strip() and not details.strip():
        return jsonify({"ok": False, "msg": "Le sujet de prière est vide."}), 400

    html = f"""
    <h2>Nouveau sujet de prière</h2>
    <p><strong>Prénom : </strong>{name}</p>
    <p><strong>Email : </strong>{email or 'Non fourni'}</p>
    <p><strong>Sujet court : </strong>{subject_text}</p>
    <p><strong>Détails : </strong><br/>{details.replace('\\n','<br/>')}</p>
    <p>Envoyé depuis Holy Spirit Home.</p>
    """

    ok, err = send_email("Nouveau sujet de prière — Holy Spirit Home", html, sender_display=name, reply_to=email or None)
    log_submission("prayer", {"name": name, "email": email, "subject": subject_text, "details": details, "success": ok, "err": err})
    if ok:
        return jsonify({"ok": True, "msg": "Merci — votre sujet de prière a bien été envoyé."})
    else:
        return jsonify({"ok": False, "msg": f"Erreur à l'envoi : {err}"}), 500

@app.route("/contact", methods=["POST"])
def contact():
    data = request.json or request.form
    name = data.get("name", "Anonyme")
    email = data.get("email", "")
    message = data.get("message", "")

    if not message.strip():
        return jsonify({"ok": False, "msg": "Le message est vide."}), 400

    html = f"""
    <h2>Message de contact</h2>
    <p><strong>Prénom : </strong>{name}</p>
    <p><strong>Email : </strong>{email or 'Non fourni'}</p>
    <p><strong>Message : </strong><br/>{message.replace('\\n','<br/>')}</p>
    """

    ok, err = send_email("Contact — Holy Spirit Home", html, sender_display=name, reply_to=email or None)
    log_submission("contact", {"name": name, "email": email, "message": message, "success": ok, "err": err})
    if ok:
        return jsonify({"ok": True, "msg": "Merci — votre message a bien été envoyé."})
    else:
        return jsonify({"ok": False, "msg": f"Erreur à l'envoi : {err}"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
