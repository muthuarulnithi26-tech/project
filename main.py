from flask import Flask, render_template, request, redirect, flash, session
from controller.models import User, create_tables
from controller.database import SessionLocal

app = Flask(__name__)
app.secret_key = "super-secret-key"

create_tables()
db = SessionLocal()

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template(
        "home.html",
        username=session.get("username")
    )

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email_or_phone = request.form["email_or_phone"]
        password = request.form["password"]

        if db.query(User).filter_by(email_or_phone=email_or_phone).first():
            flash("User already exists")
            return redirect("/register")

        user = User(
            username=username,
            email_or_phone=email_or_phone,
            password=password
        )
        db.add(user)
        db.commit()

        flash("Registration successful. Please login.")
        return redirect("/login")

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email_or_phone = request.form["email_or_phone"]
        password = request.form["password"]

        user = db.query(User).filter_by(
            email_or_phone=email_or_phone,
            password=password
        ).first()

        if user:
            session["username"] = user.username
            flash("Login successful")
            return redirect("/")
        else:
            flash("Invalid credentials")
            return redirect("/login")

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
