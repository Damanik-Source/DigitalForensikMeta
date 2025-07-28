# === server.py ===
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os, json, datetime, folium, io, magic
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas
import exifread
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecret")
login_manager = LoginManager()
login_manager.init_app(app)

UPLOAD_FOLDER = "uploads"
LOG_FILE = "log.json"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id == os.getenv("ADMIN_USERNAME") else None

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == os.getenv("ADMIN_USERNAME") and password == os.getenv("ADMIN_PASSWORD"):
            login_user(User(username))
            return redirect("/dashboard")
        return "Login Failed"
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/dashboard")
@login_required
def dashboard():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            logs = json.load(f)
    else:
        logs = []
    return render_template("dashboard.html", logs=logs)

@app.route("/", methods=["GET", "POST"])
def index():
    metadata = {}
    gps_url = None
    filename = None
    if request.method == "POST":
        file = request.files["file"]
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            with open(filepath, "rb") as f:
                tags = exifread.process_file(f)
                metadata = {tag: str(val) for tag, val in tags.items()}
                if "GPS GPSLatitude" in tags and "GPS GPSLongitude" in tags:
                    lat_ref = tags.get("GPS GPSLatitudeRef", "N")
                    lon_ref = tags.get("GPS GPSLongitudeRef", "E")
                    lat = convert_to_degrees(tags["GPS GPSLatitude"])
                    lon = convert_to_degrees(tags["GPS GPSLongitude"])
                    lat = lat if lat_ref == "N" else -lat
                    lon = lon if lon_ref == "E" else -lon
                    gps_url = url_for("map_view", lat=lat, lon=lon)

            log_metadata(filename, metadata)
    return render_template("index.html", metadata=metadata, gps_url=gps_url, filename=filename)

@app.route("/export_pdf/<filename>")
def export_pdf(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, "rb") as f:
        tags = exifread.process_file(f)
    buf = io.BytesIO()
    p = canvas.Canvas(buf)
    p.setFont("Helvetica", 10)
    p.drawString(100, 800, f"Metadata Report for {filename}")
    y = 780
    for tag, val in tags.items():
        p.drawString(50, y, f"{tag}: {val}")
        y -= 12
        if y < 50:
            p.showPage()
            y = 800
    p.save()
    buf.seek(0)
    return send_file(buf, download_name="metadata_report.pdf", as_attachment=True)

@app.route("/map")
def map_view():
    lat = float(request.args.get("lat"))
    lon = float(request.args.get("lon"))
    m = folium.Map(location=[lat, lon], zoom_start=15)
    folium.Marker([lat, lon], popup="Image Location").add_to(m)
    return m._repr_html_()

def log_metadata(filename, metadata):
    log = {
        "filename": filename,
        "metadata": metadata,
        "timestamp": datetime.datetime.now().isoformat()
    }
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            logs = json.load(f)
    logs.insert(0, log)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def convert_to_degrees(value):
    d, m, s = value.values
    return float(d.num)/d.den + float(m.num)/m.den/60 + float(s.num)/s.den/3600

if __name__ == "__main__":
    app.run(debug=True)
