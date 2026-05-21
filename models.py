from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    appointments = db.relationship("Appointment", backref="client", lazy="dynamic")
    offers = db.relationship("Offer", backref="client", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Master(db.Model):
    __tablename__ = "masters"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(180), nullable=False)
    bio = db.Column(db.Text)
    photo_filename = db.Column(db.String(120))

    slots = db.relationship("Slot", backref="master", lazy="dynamic")
    appointments = db.relationship("Appointment", backref="master", lazy="dynamic")


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"))
    master_id = db.Column(db.Integer, db.ForeignKey("masters.id"))
    start_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="active")
    booked_by_name = db.Column(db.String(120))
    booked_by_phone = db.Column(db.String(30))
    notes = db.Column(db.Text)
    bonus_spent = db.Column(db.Integer, default=0)

    service = db.relationship("Service")


class Slot(db.Model):
    __tablename__ = "slots"

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"))
    master_id = db.Column(db.Integer, db.ForeignKey("masters.id"))
    start_time = db.Column(db.DateTime, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    service = db.relationship("Service")


class Offer(db.Model):
    __tablename__ = "offers"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"))
    description = db.Column(db.String(200))
    discount_percent = db.Column(db.Integer, default=0)
    valid_until = db.Column(db.Date)

    service = db.relationship("Service")
