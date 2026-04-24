from collections import Counter
from datetime import datetime, time, timedelta

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from config import Config
from forms import LoginForm, RegistrationForm
from models import Appointment, Offer, Service, Slot, User, db


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Сначала войдите в личный кабинет."
login_manager.login_message_category = "warning"


SERVICE_CATALOG = [
    {
        "name": "Стрижка женская",
        "duration": 60,
        "price": 2500,
        "description": "Обновление формы, укладка и рекомендации по домашнему уходу.",
    },
    {
        "name": "Стрижка мужская",
        "duration": 45,
        "price": 1800,
        "description": "Классическая или современная стрижка с укладкой.",
    },
    {
        "name": "Маникюр",
        "duration": 90,
        "price": 2000,
        "description": "Аппаратный маникюр, покрытие и уход за кожей рук.",
    },
    {
        "name": "Массаж спины",
        "duration": 60,
        "price": 3000,
        "description": "Расслабляющий массаж для снятия напряжения и восстановления.",
    },
]


def dt_on(day_offset, hour):
    base_date = datetime.now().date() + timedelta(days=day_offset)
    return datetime.combine(base_date, time(hour, 0))


def seed_services():
    existing_names = {service.name for service in Service.query.all()}
    for item in SERVICE_CATALOG:
        if item["name"] not in existing_names:
            db.session.add(Service(**item))
    db.session.commit()
    return Service.query.order_by(Service.price.asc()).all()


def ensure_future_slots(services, days_ahead=14):
    now = datetime.now()
    slot_hours = [10, 12, 14, 16, 18]
    existing_slots = {
        (slot.service_id, slot.start_time)
        for slot in Slot.query.filter(
            Slot.start_time >= now - timedelta(days=45),
            Slot.start_time <= now + timedelta(days=days_ahead + 3),
        ).all()
    }

    created = False
    for day_offset in range(days_ahead + 1):
        for hour in slot_hours:
            start_time = dt_on(day_offset, hour)
            if start_time <= now + timedelta(minutes=30):
                continue
            for service in services:
                slot_key = (service.id, start_time)
                if slot_key not in existing_slots:
                    db.session.add(
                        Slot(
                            service_id=service.id,
                            start_time=start_time,
                            is_available=True,
                        )
                    )
                    created = True
                    existing_slots.add(slot_key)

    if created:
        db.session.commit()


def ensure_offer(user, service_name, description, discount_percent, valid_days):
    service = Service.query.filter_by(name=service_name).first()
    if service is None:
        return

    existing_offer = Offer.query.filter_by(
        client_id=user.id,
        service_id=service.id,
        description=description,
    ).first()

    if existing_offer is None:
        db.session.add(
            Offer(
                client_id=user.id,
                service_id=service.id,
                description=description,
                discount_percent=discount_percent,
                valid_until=datetime.now().date() + timedelta(days=valid_days),
            )
        )


def ensure_appointment(user, service_name, start_time, status):
    service = Service.query.filter_by(name=service_name).first()
    if service is None:
        return

    slot = Slot.query.filter_by(service_id=service.id, start_time=start_time).first()
    if slot is None:
        slot = Slot(service_id=service.id, start_time=start_time, is_available=True)
        db.session.add(slot)
        db.session.flush()

    appointment = Appointment.query.filter_by(
        client_id=user.id,
        service_id=service.id,
        start_time=start_time,
    ).first()
    if appointment is None:
        appointment = Appointment(
            client_id=user.id,
            service_id=service.id,
            start_time=start_time,
            status=status,
        )
        db.session.add(appointment)
    else:
        appointment.status = status

    if start_time > datetime.now():
        slot.is_available = status != "active"


def normalize_appointments():
    now = datetime.now()
    changed = False

    stale_active = Appointment.query.filter(
        Appointment.status == "active",
        Appointment.start_time < now,
    ).all()
    for appointment in stale_active:
        appointment.status = "completed"
        changed = True

    active_future_slots = {
        (appointment.service_id, appointment.start_time)
        for appointment in Appointment.query.filter(
            Appointment.status == "active",
            Appointment.start_time > now,
        ).all()
    }

    for slot in Slot.query.filter(Slot.start_time > now).all():
        should_be_available = (slot.service_id, slot.start_time) not in active_future_slots
        if slot.is_available != should_be_available:
            slot.is_available = should_be_available
            changed = True

    if changed:
        db.session.commit()


def ensure_demo_data():
    demo_user = User.query.filter_by(email="demo@example.com").first()
    if demo_user is None:
        demo_user = User(
            name="Анна Петрова",
            email="demo@example.com",
            phone="+7 999 123-45-67",
        )
        demo_user.set_password("demo123")
        db.session.add(demo_user)
        db.session.commit()

    demo_schedule = [
        ("Маникюр", dt_on(1, 12), "active"),
        ("Массаж спины", dt_on(3, 18), "active"),
        ("Стрижка женская", dt_on(-7, 14), "completed"),
        ("Маникюр", dt_on(-16, 12), "completed"),
        ("Массаж спины", dt_on(-28, 16), "cancelled"),
    ]

    for service_name, start_time, status in demo_schedule:
        ensure_appointment(demo_user, service_name, start_time, status)

    ensure_offer(
        demo_user,
        "Стрижка женская",
        "Персональная скидка 20% на обновление стрижки и укладку.",
        20,
        25,
    )
    ensure_offer(
        demo_user,
        "Маникюр",
        "Бонус: экспресс-уход для рук при записи на маникюр в будни.",
        15,
        18,
    )

    db.session.commit()
    normalize_appointments()


def collect_dashboard_stats(user):
    now = datetime.now()
    completed_visits = (
        Appointment.query.filter_by(client_id=user.id, status="completed")
        .order_by(Appointment.start_time.desc())
        .all()
    )
    active_visits = Appointment.query.filter(
        Appointment.client_id == user.id,
        Appointment.status == "active",
        Appointment.start_time > now,
    ).all()
    offers = Offer.query.filter(
        Offer.client_id == user.id,
        Offer.valid_until >= now.date(),
    ).all()

    favorite_service = None
    if completed_visits:
        service_counter = Counter(visit.service.name for visit in completed_visits)
        favorite_service = service_counter.most_common(1)[0][0]

    next_visit = min(active_visits, key=lambda visit: visit.start_time) if active_visits else None
    total_spent = sum(visit.service.price for visit in completed_visits)
    possible_savings = sum(
        round(offer.service.price * offer.discount_percent / 100)
        for offer in offers
    )

    return {
        "active_count": len(active_visits),
        "history_count": len(completed_visits),
        "available_slots": Slot.query.filter(
            Slot.is_available.is_(True),
            Slot.start_time > now,
        ).count(),
        "offers_count": len(offers),
        "total_spent": int(total_spent),
        "possible_savings": int(possible_savings),
        "favorite_service": favorite_service,
        "next_visit": next_visit,
    }


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


with app.app_context():
    db.create_all()
    services = seed_services()
    ensure_future_slots(services)
    ensure_demo_data()


@app.context_processor
def inject_navigation_state():
    return {"now": datetime.now()}


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        ensure_offer(
            user,
            "Маникюр",
            "Приветственная скидка 10% на первое посещение салона.",
            10,
            21,
        )
        db.session.commit()

        flash("Регистрация прошла успешно. Теперь можно войти.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            flash(f"Добро пожаловать, {user.name}!", "success")
            return redirect(next_page) if next_page else redirect(url_for("dashboard"))
        flash("Неверный email или пароль.", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из личного кабинета.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    now = datetime.now()
    active_appointments = Appointment.query.filter(
        Appointment.client_id == current_user.id,
        Appointment.status == "active",
        Appointment.start_time > now,
    ).order_by(Appointment.start_time.asc()).limit(4).all()

    history_preview = Appointment.query.filter(
        Appointment.client_id == current_user.id,
        Appointment.status.in_(["completed", "cancelled"]),
    ).order_by(Appointment.start_time.desc()).limit(4).all()

    upcoming_slots = Slot.query.filter(
        Slot.is_available.is_(True),
        Slot.start_time > now,
    ).order_by(Slot.start_time.asc()).limit(6).all()

    offers = Offer.query.filter(
        Offer.client_id == current_user.id,
        Offer.valid_until >= now.date(),
    ).order_by(Offer.valid_until.asc()).limit(3).all()

    stats = collect_dashboard_stats(current_user)
    services = Service.query.order_by(Service.price.asc()).all()

    return render_template(
        "dashboard.html",
        active_appointments=active_appointments,
        history_preview=history_preview,
        upcoming_slots=upcoming_slots,
        offers=offers,
        services=services,
        stats=stats,
    )


@app.route("/appointments")
@login_required
def appointments():
    now = datetime.now()
    active = Appointment.query.filter(
        Appointment.client_id == current_user.id,
        Appointment.status == "active",
        Appointment.start_time > now,
    ).order_by(Appointment.start_time.asc()).all()
    return render_template("appointments.html", appointments=active)


@app.route("/appointments/<int:appointment_id>/cancel", methods=["POST"])
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.filter_by(
        id=appointment_id,
        client_id=current_user.id,
    ).first_or_404()

    if appointment.status != "active" or appointment.start_time <= datetime.now():
        flash("Эту запись уже нельзя отменить.", "warning")
        return redirect(url_for("appointments"))

    appointment.status = "cancelled"
    slot = Slot.query.filter_by(
        service_id=appointment.service_id,
        start_time=appointment.start_time,
    ).first()
    if slot is not None:
        slot.is_available = True

    db.session.commit()
    flash("Запись отменена, окно снова доступно для бронирования.", "info")
    return redirect(url_for("appointments"))


@app.route("/history")
@login_required
def history():
    history_items = Appointment.query.filter(
        Appointment.client_id == current_user.id,
        Appointment.status.in_(["completed", "cancelled"]),
    ).order_by(Appointment.start_time.desc()).all()
    return render_template("history.html", appointments=history_items)


@app.route("/free-slots")
@login_required
def free_slots():
    now = datetime.now()
    selected_service_id = request.args.get("service_id", type=int)
    selected_date = request.args.get("date", "").strip()

    query = Slot.query.filter(
        Slot.is_available.is_(True),
        Slot.start_time > now,
    )
    if selected_service_id:
        query = query.filter(Slot.service_id == selected_service_id)

    if selected_date:
        try:
            target_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
            day_start = datetime.combine(target_date, time.min)
            day_end = day_start + timedelta(days=1)
            query = query.filter(Slot.start_time >= day_start, Slot.start_time < day_end)
        except ValueError:
            flash("Дата фильтра указана некорректно.", "warning")
            return redirect(url_for("free_slots"))

    slots = query.order_by(Slot.start_time.asc()).all()

    slots_by_date = {}
    for slot in slots:
        date_key = slot.start_time.strftime("%d.%m.%Y")
        slots_by_date.setdefault(date_key, []).append(slot)

    services = Service.query.order_by(Service.name.asc()).all()
    return render_template(
        "free_slots.html",
        services=services,
        slots_by_date=slots_by_date,
        selected_service_id=selected_service_id,
        selected_date=selected_date,
        slots_count=len(slots),
    )


@app.route("/book/<int:slot_id>", methods=["POST"])
@login_required
def book_slot(slot_id):
    slot = Slot.query.get_or_404(slot_id)
    if not slot.is_available or slot.start_time <= datetime.now():
        flash("Это окно уже недоступно для записи.", "warning")
        return redirect(url_for("free_slots"))

    conflict = Appointment.query.filter(
        Appointment.client_id == current_user.id,
        Appointment.status == "active",
        Appointment.start_time == slot.start_time,
    ).first()
    if conflict is not None:
        flash("У вас уже есть запись на это время. Выберите другое окно.", "warning")
        return redirect(url_for("free_slots"))

    appointment = Appointment(
        client_id=current_user.id,
        service_id=slot.service_id,
        start_time=slot.start_time,
        status="active",
    )
    slot.is_available = False
    db.session.add(appointment)
    db.session.commit()

    flash(
        f"Запись подтверждена: {slot.service.name}, {slot.start_time.strftime('%d.%m.%Y в %H:%M')}.",
        "success",
    )
    return redirect(url_for("appointments"))


@app.route("/offers")
@login_required
def offers():
    today = datetime.now().date()
    active_offers = Offer.query.filter(
        Offer.client_id == current_user.id,
        Offer.valid_until >= today,
    ).order_by(Offer.valid_until.asc()).all()
    return render_template("offers.html", offers=active_offers)


if __name__ == "__main__":
    app.run(debug=True)
