from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

from controller.models import User, Song, BroadcasterProfile, create_tables
from controller.database import SessionLocal

app = Flask(__name__)
app.secret_key = "super-secret-key"  # change in production

# ---------------- CONFIG ----------------
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------- DATABASE ----------------
create_tables()
db = SessionLocal()

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template(
        "home.html",
        username=session.get("username"),
        role=session.get("role")
    )

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email_or_phone = request.form.get("email_or_phone")
        password = request.form.get("password")

        if db.query(User).filter_by(email_or_phone=email_or_phone).first():
            flash("User already exists")
            return redirect("/register")

        user = User(
            username=username,
            email_or_phone=email_or_phone,
            password=generate_password_hash(password),
            role="listener"
        )
        db.add(user)
        db.commit()  # ensure commit
        flash("Registration successful. Please login.")
        return redirect("/login")

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email_or_phone = request.form.get("email_or_phone")
        password = request.form.get("password")

        user = db.query(User).filter_by(email_or_phone=email_or_phone).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            flash("Login successful")
            # Redirect based on role
            if user.role == "broadcaster":
                return redirect("/upload")
            else:
                return redirect("/")
        else:
            flash("Invalid credentials")
            return redirect("/login")

    return render_template("login.html")

# ---------------- PROFILE ----------------
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/login")

    user = db.query(User).filter_by(id=session["user_id"]).first()
    broadcaster_profile = db.query(BroadcasterProfile).filter_by(user_id=user.id).first()
    return render_template("profile.html", user=user, profile=broadcaster_profile)

# ---------------- BECOME BROADCASTER ----------------
@app.route("/become-broadcaster", methods=["GET", "POST"])
def become_broadcaster():
    if "user_id" not in session:
        return redirect("/login")

    user = db.query(User).filter_by(id=session["user_id"]).first()
    if not user:
        session.clear()
        return redirect("/login")

    if user.role == "broadcaster":
        flash("You are already a broadcaster")
        return redirect("/upload")

    if request.method == "POST":
        channel_name = request.form.get("channel_name")
        contact = request.form.get("contact")

        if not channel_name or not contact:
            flash("All fields are required")
            return redirect("/become-broadcaster")

        profile = BroadcasterProfile(
            user_id=user.id,
            channel_name=channel_name,
            contact_email=contact
        )
        db.add(profile)

        user.role = "broadcaster"
        db.commit()  # ensure both user role & profile saved
        session["role"] = "broadcaster"

        flash("Broadcaster activated 🎉")
        return redirect("/upload")

    return render_template("become_broadcaster.html")

# ---------------- UPLOAD SONG ----------------
@app.route("/upload", methods=["GET", "POST"])
def upload_song():
    if session.get("role") != "broadcaster":
        flash("Broadcaster access only")
        return redirect("/become-broadcaster")

    if request.method == "POST":
        title = request.form.get("title")
        file = request.files.get("file")

        if not title or not file:
            flash("All fields are required")
            return redirect("/upload")

        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        # Save in DB
        song = Song(
            title=title,
            file_path=file_path,
            broadcaster_id=session["user_id"]
        )
        db.add(song)
        db.commit()  # ensure commit
        flash("Song uploaded successfully")
        return redirect("/upload")

    return render_template("upload_song.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if session.get("role") != "broadcaster":
        flash("Access denied")
        return redirect("/")

    user_id = session["user_id"]
    songs = db.query(Song).filter_by(broadcaster_id=user_id).all()
    return render_template("broadcaster_dashboard.html", songs=songs)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out")
    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
