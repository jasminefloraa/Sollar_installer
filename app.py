import os, re, datetime as dt, jwt
from functools import wraps
from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, join_room
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder="static", static_url_path="")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///sunlead.db").replace("postgres://", "postgresql://")
SECRET = os.getenv("SECRET_KEY", "dev-secret-change-me")
db = SQLAlchemy(app); CORS(app); sio = SocketIO(app, cors_allowed_origins="*")

# Demo assumptions (editable) - NOT real pricing
CFG = dict(lead_cost=40, lead_price=100, yield_kwh_per_kw=1400, offset=0.9, cost_per_kw=2800,
           tax_credit=0.30, co2_kg_per_kwh=0.386, default_rate=0.16)
STATUSES = ["New", "Contacted", "Consultation Scheduled", "Proposal Sent", "Won", "Lost"]
now = dt.datetime.utcnow

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120)); email = db.Column(db.String(120), unique=True)
    pw = db.Column(db.String(255)); role = db.Column(db.String(20))
    company = db.Column(db.String(120)); states = db.Column(db.String(200), default="")
    status = db.Column(db.String(20), default="pending"); created = db.Column(db.DateTime, default=now)
    def dict(self):
        return dict(id=self.id, name=self.name, email=self.email, role=self.role, company=self.company,
                    states=self.states, status=self.status, claimed=Lead.query.filter_by(installer_id=self.id).count())

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True); code = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(120)); email = db.Column(db.String(120)); phone = db.Column(db.String(30))
    zip = db.Column(db.String(10)); state = db.Column(db.String(2)); city = db.Column(db.String(80))
    data = db.Column(db.JSON)       # property, energy & interest answers
    estimate = db.Column(db.JSON)
    score = db.Column(db.Integer); qualification = db.Column(db.String(20))
    status = db.Column(db.String(30), default="New")
    installer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created = db.Column(db.DateTime, default=now); updated = db.Column(db.DateTime, default=now, onupdate=now)
    def dict(self, viewer=None):
        full = viewer and (viewer.role == "admin" or self.installer_id == viewer.id)
        inst = db.session.get(User, self.installer_id) if self.installer_id else None
        return dict(id=self.id, code=self.code, name=self.name if full else self.name.split()[0] + " ***",
                    email=self.email if full else "Hidden until claimed", phone=self.phone if full else "Hidden until claimed",
                    zip=self.zip, state=self.state, city=self.city, data=self.data, estimate=self.estimate,
                    score=self.score, qualification=self.qualification, status=self.status,
                    installer_id=self.installer_id, installer=inst.company if inst else None,
                    created=self.created.isoformat(), updated=self.updated.isoformat())

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True); lead_id = db.Column(db.Integer, db.ForeignKey("lead.id"))
    status = db.Column(db.String(30)); by = db.Column(db.Integer); at = db.Column(db.DateTime, default=now)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True); user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    msg = db.Column(db.String(255)); read = db.Column(db.Boolean, default=False); created = db.Column(db.DateTime, default=now)

# ---------- helpers ----------
def token(u): return jwt.encode({"id": u.id, "role": u.role, "exp": now() + dt.timedelta(days=2)}, SECRET, "HS256")

def auth(*roles):
    def deco(f):
        @wraps(f)
        def w(*a, **k):
            try: p = jwt.decode(request.headers.get("Authorization", "").replace("Bearer ", ""), SECRET, algorithms=["HS256"])
            except Exception: return jsonify(error="Login required"), 401
            g.user = db.session.get(User, p["id"])
            if not g.user or g.user.role not in roles: return jsonify(error="Forbidden"), 403
            if g.user.role == "installer" and g.user.status == "suspended": return jsonify(error="Account suspended"), 403
            return f(*a, **k)
        return w
    return deco

def notify(users, msg):
    for u in users:
        db.session.add(Notification(user_id=u.id, msg=msg))
    db.session.commit()
    for u in users: sio.emit("notification", {"msg": msg}, room=f"u{u.id}")

def changed(lead): sio.emit("lead_changed", {"id": lead.id, "code": lead.code}, room="staff")
def admins(): return User.query.filter_by(role="admin").all()

def matching_installers(lead):
    """Rule-based matcher (not ML): approved + service-area match. Replace with smarter logic later."""
    return [i for i in User.query.filter_by(role="installer", status="approved")
            if "ALL" in i.states.upper().split(",") or lead.state in i.states.upper().split(",")]

def num(v, d=0):
    try: return float(v)
    except (TypeError, ValueError): return d

def estimate(d):
    bill = num(d.get("bill")); rate = num(d.get("rate")) or CFG["default_rate"]
    kwh = num(d.get("kwh")) or bill / rate
    kw = round(kwh * 12 * CFG["offset"] / CFG["yield_kwh_per_kw"], 1)
    savings = round(bill * 12 * CFG["offset"])
    net = kw * CFG["cost_per_kw"] * (1 - CFG["tax_credit"])
    return dict(monthly_cost=round(bill), annual_cost=round(bill * 12), offset_pct=int(CFG["offset"] * 100),
                system_kw=kw, annual_savings=savings, payback_years=round(net / savings, 1) if savings else None,
                co2_tonnes=round(kwh * 12 * CFG["offset"] * CFG["co2_kg_per_kwh"] / 1000, 1))

def score(d, state):
    s = 30 if d.get("ownership") == "Owner" else 0
    b = num(d.get("bill")); s += 25 if b >= 150 else 15 if b >= 100 else 5 if b >= 60 else 0
    s += {"Yes": 15, "Maybe": 7}.get(d.get("interest"), 0)
    s += {"ASAP": 10, "1-3 months": 8, "3-6 months": 4}.get(d.get("timeframe"), 0)
    s += 5 if d.get("roof_cond") == "Good" else 2 if d.get("roof_cond") == "Fair" else 0
    s += 5 if num(d.get("roof_age")) < 20 else 0
    s += 5 if d.get("prop_type") in ("Single-family", "Townhouse") else 0
    s += 5 if d.get("phone") and d.get("email") else 0
    q = "High Potential" if s >= 75 else "Qualified" if s >= 55 else "Needs Review" if s >= 35 else "Unqualified"
    if d.get("ownership") != "Owner" and q in ("High Potential", "Qualified"): q = "Needs Review"
    return s, q

# ---------- auth ----------
@app.post("/api/auth/register")
def register():
    j = request.json or {}
    if not all(j.get(k) for k in ("name", "email", "password", "company", "states")) or len(j["password"]) < 8:
        return jsonify(error="All fields required; password min 8 chars"), 400
    if User.query.filter_by(email=j["email"].lower()).first(): return jsonify(error="Email already registered"), 409
    u = User(name=j["name"], email=j["email"].lower(), pw=generate_password_hash(j["password"]), role="installer",
             company=j["company"], states=j["states"].upper().replace(" ", ""), status="pending")
    db.session.add(u); db.session.commit()
    notify(admins(), f"New installer awaiting approval: {u.company}")
    return jsonify(message="Registered. An admin must approve your account before you can claim leads."), 201

@app.post("/api/auth/login")
def login():
    j = request.json or {}
    u = User.query.filter_by(email=(j.get("email") or "").lower()).first()
    if not u or not check_password_hash(u.pw, j.get("password") or ""): return jsonify(error="Invalid credentials"), 401
    return jsonify(token=token(u), user=u.dict())

# ---------- homeowner ----------
@app.post("/api/homeowner/assessment")
def assessment():
    d = request.json or {}
    errs = []
    if not re.fullmatch(r"\d{5}", d.get("zip", "")): errs.append("Valid 5-digit ZIP required")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.\w+", d.get("email", "")): errs.append("Valid email required")
    if len(re.sub(r"\D", "", d.get("phone", ""))) < 10: errs.append("Valid phone required")
    if num(d.get("bill")) <= 0: errs.append("Monthly bill required")
    for k in ("name", "state", "city", "ownership"):
        if not d.get(k): errs.append(f"{k} required")
    if errs: return jsonify(errors=errs), 400
    sc, q = score(d, d["state"]); est = estimate(d)
    keep = ("name", "email", "phone", "zip", "state", "city")
    lead = Lead(name=d["name"], email=d["email"], phone=d["phone"], zip=d["zip"], state=d["state"].upper(), city=d["city"],
                data={k: v for k, v in d.items() if k not in keep}, estimate=est, score=sc, qualification=q)
    db.session.add(lead); db.session.flush()
    lead.code = f"SL-{now().year}-{lead.id:06d}"
    db.session.add(History(lead_id=lead.id, status="New")); db.session.commit()
    if q in ("Qualified", "High Potential"):
        notify(matching_installers(lead), "New qualified solar lead available in your service area.")
    if q == "High Potential": notify(admins(), f"New high-potential lead received: {lead.code}")
    changed(lead)
    return jsonify(code=lead.code, qualification=q, estimate=est, message="Your solar assessment is ready."), 201

# ---------- leads ----------
@app.get("/api/leads")
@auth("admin", "installer")
def leads():
    qs = Lead.query.order_by(Lead.created.desc())
    if g.user.role == "installer":
        qs = qs.filter(((Lead.installer_id == None) & Lead.qualification.in_(["Qualified", "High Potential"])) | (Lead.installer_id == g.user.id))
    return jsonify([l.dict(g.user) for l in qs if g.user.role == "admin" or l.installer_id == g.user.id or g.user.states.upper() and (l.state in g.user.states.split(",") or "ALL" in g.user.states)])

@app.patch("/api/leads/<int:i>/status")
@auth("admin", "installer")
def set_status(i):
    l = db.get_or_404(Lead, i); s = (request.json or {}).get("status")
    if s not in STATUSES: return jsonify(error="Invalid status"), 400
    if g.user.role == "installer" and l.installer_id != g.user.id: return jsonify(error="Not your lead"), 403
    l.status = s; db.session.add(History(lead_id=l.id, status=s, by=g.user.id)); db.session.commit()
    if g.user.role == "installer": notify(admins(), f"{l.code} moved to {s} by {g.user.company}")
    changed(l); return jsonify(l.dict(g.user))

@app.post("/api/leads/<int:i>/claim")
@auth("installer")
def claim(i):
    if g.user.status != "approved": return jsonify(error="Account not approved yet"), 403
    l = db.get_or_404(Lead, i)
    if l.qualification not in ("Qualified", "High Potential"): return jsonify(error="Lead not claimable"), 400
    n = Lead.query.filter_by(id=i, installer_id=None).update({"installer_id": g.user.id})  # atomic: first come, first served
    db.session.commit()
    if not n: return jsonify(error="Lead already claimed"), 409
    notify([g.user], f"Lead {l.code} has been assigned to you.")
    notify(admins(), f"{l.code} claimed by {g.user.company}")
    changed(l); return jsonify(l.dict(g.user))

@app.patch("/api/leads/<int:i>/assign")
@auth("admin")
def assign(i):
    l = db.get_or_404(Lead, i); inst = db.session.get(User, (request.json or {}).get("installer_id") or 0)
    l.installer_id = inst.id if inst else None; db.session.commit()
    if inst: notify([inst], f"Lead {l.code} has been assigned to you.")
    changed(l); return jsonify(l.dict(g.user))

@app.delete("/api/leads/<int:i>")
@auth("admin")
def remove(i):
    l = db.get_or_404(Lead, i); History.query.filter_by(lead_id=i).delete(); db.session.delete(l); db.session.commit()
    sio.emit("lead_changed", {"id": i}, room="staff"); return jsonify(ok=True)

# ---------- installers / notifications / analytics ----------
@app.get("/api/installers")
@auth("admin")
def installers(): return jsonify([u.dict() for u in User.query.filter_by(role="installer")])

@app.patch("/api/installers/<int:i>")
@auth("admin")
def inst_status(i):
    u = db.get_or_404(User, i); s = (request.json or {}).get("status")
    if s not in ("approved", "suspended", "pending"): return jsonify(error="Invalid"), 400
    u.status = s; db.session.commit(); notify([u], f"Your installer account is now {s}.")
    sio.emit("lead_changed", {}, room="staff"); return jsonify(u.dict())

@app.get("/api/notifications")
@auth("admin", "installer")
def notes():
    return jsonify([dict(id=n.id, msg=n.msg, read=n.read, created=n.created.isoformat())
                    for n in Notification.query.filter_by(user_id=g.user.id).order_by(Notification.created.desc()).limit(30)])

@app.patch("/api/notifications/<int:i>/read")
@auth("admin", "installer")
def read(i):
    n = db.get_or_404(Notification, i)
    if n.user_id == g.user.id: n.read = True; db.session.commit()
    return jsonify(ok=True)

@app.get("/api/analytics/dashboard")
@auth("admin")
def analytics():
    L = Lead.query.all(); cnt = lambda f: sum(1 for l in L if f(l))
    q = cnt(lambda l: l.qualification in ("Qualified", "High Potential")); assigned = cnt(lambda l: l.installer_id)
    won = cnt(lambda l: l.status == "Won")
    by = lambda key: {k: cnt(lambda l, k=k: key(l) == k) for k in sorted({key(l) for l in L})}
    days = {}
    for l in L: days[l.created.strftime("%m-%d")] = days.get(l.created.strftime("%m-%d"), 0) + 1
    rev, cost = assigned * CFG["lead_price"], q * CFG["lead_cost"]
    return jsonify(total=len(L), new=cnt(lambda l: l.status == "New"), qualified=q, assigned=assigned, won=won,
                   lost=cnt(lambda l: l.status == "Lost"), revenue=rev, cost=cost, margin=rev - cost,
                   conversion=round(100 * won / assigned) if assigned else 0,
                   response_rate=round(100 * assigned / q) if q else 0,
                   by_status=by(lambda l: l.status), by_qualification=by(lambda l: l.qualification),
                   by_state=by(lambda l: l.state), by_day=days, assumptions=CFG)

@sio.on("connect")
def on_connect(a=None):
    try: p = jwt.decode((a or {}).get("token", ""), SECRET, algorithms=["HS256"])
    except Exception: return
    join_room(f"u{p['id']}"); join_room("staff")

@app.get("/api/health")
def health(): return jsonify(ok=True)

@app.get("/")
def index(): return app.send_static_file("index.html")

with app.app_context():
    db.create_all()
    if not User.query.filter_by(role="admin").first():
        db.session.add(User(name="SunLead Admin", email="admin@sunlead.com", pw=generate_password_hash("Admin@123"), role="admin", status="approved"))
    if not User.query.filter_by(email="demo@installer.com").first():   # ready-made approved installer for demos
        db.session.add(User(name="Demo Installer", email="demo@installer.com", pw=generate_password_hash("Installer@123"), role="installer",
                            company="Bright Roof Solar", states="ALL", status="approved"))
    db.session.commit()

if __name__ == "__main__":
    sio.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)), allow_unsafe_werkzeug=True)