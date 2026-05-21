from collections import Counter
from datetime import datetime, time, timedelta
from functools import wraps
import hashlib
import mimetypes
import os
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from flask import Flask, abort, flash, redirect, render_template, request, send_file, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from sqlalchemy import inspect, or_, text

from config import Config
from forms import LoginForm, MasterForm, RegistrationForm, SlotForm
from models import Appointment, Master, Offer, Service, Slot, User, db


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Войдите в систему, чтобы продолжить."
login_manager.login_message_category = "warning"

SALON_NAME = "Velvet Touch"
DEMO_CLIENT = {"email": "demo@example.com", "password": "demo123"}
ADMIN_CLIENT = {"email": "admin@velvettouch.ru", "password": "admin123"}
MEDIA_CACHE_DIR = "/data/media-cache" if "AMVERA" in os.environ else os.path.join(app.root_path, "instance", "media-cache")

SERVICE_CATALOG = [
    {
        "name": "Стрижка женская",
        "duration": 60,
        "price": 2500,
        "description": "Форма, укладка и уходовые рекомендации в одном визите.",
    },
    {
        "name": "Стрижка мужская",
        "duration": 45,
        "price": 1800,
        "description": "Чистая форма, современная техника и аккуратная укладка.",
    },
    {
        "name": "Маникюр",
        "duration": 90,
        "price": 2000,
        "description": "Аппаратный маникюр, покрытие и деликатный уход за руками.",
    },
    {
        "name": "Массаж спины",
        "duration": 60,
        "price": 3000,
        "description": "Расслабляющая техника для восстановления и снятия напряжения.",
    },
    {
        "name": "Уход для лица",
        "duration": 75,
        "price": 3200,
        "description": "Мягкое очищение, массаж и сияющий финиш для спокойного ухоженного образа.",
    },
    {
        "name": "Окрашивание волос",
        "duration": 150,
        "price": 5200,
        "description": "Глубокий оттенок, деликатная техника и финишная укладка.",
    },
    {
        "name": "Архитектура бровей",
        "duration": 45,
        "price": 1800,
        "description": "Форма, коррекция и аккуратный натуральный акцент.",
    },
    {
        "name": "Ламинирование ресниц",
        "duration": 60,
        "price": 2600,
        "description": "Новинка салона: мягкий изгиб, уход и выразительный открытый взгляд.",
    },
    {
        "name": "SPA-ритуал для волос",
        "duration": 80,
        "price": 2800,
        "description": "Новинка салона: глубокое питание, блеск и восстановление длины без перегруза.",
    },
]

MASTER_CATALOG = [
    {
        "name": "София Морозова",
        "specialty": "Стилист-колорист",
        "phone": "+7 913 555-20-10",
        "address": "ул. Ленина, 18, Новосибирск",
        "bio": "Отвечает за мягкие формы, воздушные укладки и премиальный клиентский сервис.",
        "photo_filename": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=1000&q=80",
        "services": ["Стрижка женская", "Стрижка мужская", "SPA-ритуал для волос"],
    },
    {
        "name": "Елена Власова",
        "specialty": "Мастер ногтевого сервиса",
        "phone": "+7 913 555-20-11",
        "address": "ул. Ленина, 18, Новосибирск",
        "bio": "Специализируется на чистом маникюре, стойком покрытии и уходовых ритуалах.",
        "photo_filename": "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=1000&q=80",
        "services": ["Маникюр"],
    },
    {
        "name": "Майя Белова",
        "specialty": "Массажист и wellness-специалист",
        "phone": "+7 913 555-20-12",
        "address": "ул. Ленина, 18, Новосибирск",
        "bio": "Создает спокойный восстановительный опыт и помогает клиентам снять напряжение.",
        "photo_filename": "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=1000&q=80",
        "services": ["Массаж спины"],
    },
    {
        "name": "Дарья Орлова",
        "specialty": "Косметолог-эстетист",
        "phone": "+7 913 555-20-13",
        "address": "ул. Ленина, 18, Новосибирск",
        "bio": "Собирает деликатные уходовые ритуалы для ровного тона, сияния и ощущения спокойной заботы.",
        "photo_filename": "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?auto=format&fit=crop&w=1000&q=80",
        "services": ["Уход для лица", "Архитектура бровей", "Ламинирование ресниц"],
    },
    {
        "name": "Полина Громова",
        "specialty": "Стилист по окрашиванию",
        "phone": "+7 913 555-20-14",
        "address": "ул. Ленина, 18, Новосибирск",
        "bio": "Работает с мягкими сложными оттенками и премиальным окрашиванием без визуального перегруза.",
        "photo_filename": "https://images.unsplash.com/photo-1517365830460-955ce3ccd263?auto=format&fit=crop&w=1000&q=80",
        "services": ["Окрашивание волос", "Стрижка женская"],
    },
    {
        "name": "Алина Соколова",
        "specialty": "Brow-artist и мастер деликатного ухода",
        "phone": "+7 913 555-20-15",
        "address": "ул. Ленина, 18, Новосибирск",
        "bio": "Делает мягкую архитектуру бровей, спокойные уходовые акценты и помогает собрать цельный beauty-образ.",
        "photo_filename": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=1000&q=80",
        "services": ["Архитектура бровей", "Уход для лица", "Ламинирование ресниц"],
    },
]

LANDING_TESTIMONIAL = {
    "quote": "После первого визита я наконец перестала теряться в записях: все видно, удобно и очень красиво.",
    "author": "Алина, постоянный клиент Velvet Touch",
}


def dt_on(day_offset, hour):
    return datetime.combine(datetime.now().date() + timedelta(days=day_offset), time(hour, 0))


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("login", next=request.path))
        if not current_user.is_admin:
            flash("Эта зона доступна только администратору.", "warning")
            return redirect(url_for("dashboard"))
        return view_func(*args, **kwargs)

    return wrapped_view


def migrate_legacy_schema():
    inspector = inspect(db.engine)
    existing_tables = inspector.get_table_names()

    def ensure_column(table_name, column_name, ddl):
        current_columns = {col["name"] for col in inspect(db.engine).get_columns(table_name)}
        if column_name not in current_columns:
            db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl}"))
            db.session.commit()

    if "users" in existing_tables:
        ensure_column("users", "is_admin", "BOOLEAN DEFAULT 0")
    if "appointments" in existing_tables:
        ensure_column("appointments", "master_id", "INTEGER")
        ensure_column("appointments", "booked_by_name", "VARCHAR(120)")
        ensure_column("appointments", "booked_by_phone", "VARCHAR(30)")
        ensure_column("appointments", "notes", "TEXT")
        ensure_column("appointments", "bonus_spent", "INTEGER DEFAULT 0")
    if "slots" in existing_tables:
        ensure_column("slots", "master_id", "INTEGER")


def seed_services():
    existing_names = {service.name for service in Service.query.all()}
    for item in SERVICE_CATALOG:
        if item["name"] not in existing_names:
            db.session.add(Service(**item))
    db.session.commit()
    return Service.query.order_by(Service.price.asc()).all()


def seed_masters():
    master_lookup = {master.name: master for master in Master.query.all()}
    for item in MASTER_CATALOG:
        master = master_lookup.get(item["name"])
        if master is None:
            master = Master(
                name=item["name"],
                specialty=item["specialty"],
                phone=item["phone"],
                address=item["address"],
                bio=item["bio"],
                photo_filename=item["photo_filename"],
            )
            db.session.add(master)
        else:
            master.specialty = item["specialty"]
            master.phone = item["phone"]
            master.address = item["address"]
            master.bio = item["bio"]
            master.photo_filename = item["photo_filename"]
    db.session.commit()
    return Master.query.order_by(Master.name.asc()).all()


def service_by_name(name):
    return Service.query.filter_by(name=name).first()


def default_master_for_service(service_name):
    for item in MASTER_CATALOG:
        if service_name in item["services"]:
            return Master.query.filter_by(name=item["name"]).first()
    return Master.query.order_by(Master.id.asc()).first()


def backfill_master_links():
    changed = False

    for slot in Slot.query.filter(Slot.master_id.is_(None)).all():
        master = default_master_for_service(slot.service.name)
        if master is not None:
            slot.master_id = master.id
            changed = True

    for appointment in Appointment.query.filter(Appointment.master_id.is_(None)).all():
        master = default_master_for_service(appointment.service.name)
        if master is not None:
            appointment.master_id = master.id
            changed = True
        if not appointment.booked_by_name and appointment.client is not None:
            appointment.booked_by_name = appointment.client.name
            changed = True
        if not appointment.booked_by_phone and appointment.client is not None:
            appointment.booked_by_phone = appointment.client.phone
            changed = True

    if changed:
        db.session.commit()


def ensure_admin_user():
    admin = User.query.filter_by(email=ADMIN_CLIENT["email"]).first()
    if admin is None:
        admin = User(
            name="Администратор Velvet Touch",
            email=ADMIN_CLIENT["email"],
            phone="+7 913 555-10-00",
            is_admin=True,
        )
        admin.set_password(ADMIN_CLIENT["password"])
        db.session.add(admin)
        db.session.commit()
    elif not admin.is_admin:
        admin.is_admin = True
        if not admin.phone:
            admin.phone = "+7 913 555-10-00"
        db.session.commit()


def ensure_offer(user, service_name, description, discount_percent, valid_days):
    service = service_by_name(service_name)
    if service is None:
        return

    exists = Offer.query.filter_by(
        client_id=user.id,
        service_id=service.id,
        description=description,
    ).first()
    if exists is None:
        db.session.add(
            Offer(
                client_id=user.id,
                service_id=service.id,
                description=description,
                discount_percent=discount_percent,
                valid_until=datetime.now().date() + timedelta(days=valid_days),
            )
        )


def create_or_update_appointment(user, service_name, start_time, status, notes=""):
    service = service_by_name(service_name)
    master = default_master_for_service(service_name)
    if service is None or master is None:
        return

    slot = Slot.query.filter_by(
        service_id=service.id,
        master_id=master.id,
        start_time=start_time,
    ).first()
    if slot is None:
        slot = Slot(
            service_id=service.id,
            master_id=master.id,
            start_time=start_time,
            is_available=status != "active",
        )
        db.session.add(slot)
        db.session.flush()

    appointment = Appointment.query.filter_by(
        client_id=user.id,
        service_id=service.id,
        master_id=master.id,
        start_time=start_time,
    ).first()
    if appointment is None:
        appointment = Appointment(
            client_id=user.id,
            service_id=service.id,
            master_id=master.id,
            start_time=start_time,
            status=status,
            booked_by_name=user.name,
            booked_by_phone=user.phone,
            notes=notes,
            bonus_spent=0,
        )
        db.session.add(appointment)
    else:
        appointment.status = status
        appointment.booked_by_name = appointment.booked_by_name or user.name
        appointment.booked_by_phone = appointment.booked_by_phone or user.phone
        if notes and not appointment.notes:
            appointment.notes = notes

    if start_time > datetime.now():
        slot.is_available = status != "active"


def seed_demo_user():
    user = User.query.filter_by(email=DEMO_CLIENT["email"]).first()
    if user is None:
        user = User(
            name="Анна Петрова",
            email=DEMO_CLIENT["email"],
            phone="+7 999 123-45-67",
            is_admin=False,
        )
        user.set_password(DEMO_CLIENT["password"])
        db.session.add(user)
        db.session.commit()

    demo_schedule = [
        ("Маникюр", dt_on(1, 12), "active", "Спокойная нюдовая палитра."),
        ("Стрижка женская", dt_on(2, 16), "active", "Легкая укладка и обновление формы."),
        ("Уход для лица", dt_on(3, 11), "active", "Спокойный уход без агрессивных активов."),
        ("Стрижка женская", dt_on(-8, 14), "completed", "Повтор любимой формы."),
        ("Маникюр", dt_on(-18, 12), "completed", "Уход и покрытие."),
        ("Окрашивание волос", dt_on(-24, 13), "completed", "Теплый темный оттенок и блеск."),
        ("Уход для лица", dt_on(-38, 11), "completed", "Сияние и восстановление."),
        ("Архитектура бровей", dt_on(-45, 15), "completed", "Мягкая натуральная форма."),
        ("Массаж спины", dt_on(-30, 16), "cancelled", "Перенос по семейным обстоятельствам."),
    ]

    for service_name, start_time, status, notes in demo_schedule:
        create_or_update_appointment(user, service_name, start_time, status, notes)

    ensure_offer(
        user,
        "Стрижка женская",
        "Персональная скидка 20% на стрижку и экспресс-укладку.",
        20,
        20,
    )
    ensure_offer(
        user,
        "Маникюр",
        "Подарочный SPA-уход при записи на маникюр в будний день.",
        15,
        18,
    )
    ensure_offer(
        user,
        "Ламинирование ресниц",
        "Новинка сезона: скидка 20% на ламинирование ресниц для клиентов с активным бонусным статусом.",
        20,
        45,
    )
    ensure_offer(
        user,
        "Окрашивание волос",
        "Скидка 15% на окрашивание для клиентов с высоким бонусным статусом.",
        15,
        30,
    )

    db.session.commit()


def ensure_future_slots(days_ahead=14):
    now = datetime.now()
    hours = [9, 11, 13, 15, 17, 19]

    service_map = {
        item["name"]: item["services"] for item in MASTER_CATALOG
    }
    masters = {master.name: master for master in Master.query.all()}

    existing_keys = {
        (slot.service_id, slot.master_id, slot.start_time)
        for slot in Slot.query.filter(
            Slot.start_time >= now - timedelta(days=30),
            Slot.start_time <= now + timedelta(days=days_ahead + 5),
        ).all()
    }

    created = False
    for master_name, services in service_map.items():
        master = masters.get(master_name)
        if master is None:
            continue
        for service_name in services:
            service = service_by_name(service_name)
            if service is None:
                continue
            for day_offset in range(days_ahead + 1):
                for hour in hours:
                    start_time = dt_on(day_offset, hour)
                    if start_time <= now + timedelta(minutes=30):
                        continue
                    slot_key = (service.id, master.id, start_time)
                    if slot_key not in existing_keys:
                        db.session.add(
                            Slot(
                                service_id=service.id,
                                master_id=master.id,
                                start_time=start_time,
                                is_available=True,
                            )
                        )
                        existing_keys.add(slot_key)
                        created = True

    if created:
        db.session.commit()


def normalize_appointments_and_slots():
    now = datetime.now()
    changed = False

    for appointment in Appointment.query.filter(
        Appointment.status == "active",
        Appointment.start_time < now,
    ).all():
        appointment.status = "completed"
        changed = True

    active_keys = {
        (appointment.service_id, appointment.master_id, appointment.start_time)
        for appointment in Appointment.query.filter(
            Appointment.status == "active",
            Appointment.start_time > now,
        ).all()
    }

    for slot in Slot.query.filter(Slot.start_time <= now, Slot.is_available.is_(True)).all():
        slot.is_available = False
        changed = True

    for slot in Slot.query.filter(Slot.start_time > now).all():
        should_be_available = (
            slot.service_id,
            slot.master_id,
            slot.start_time,
        ) not in active_keys
        if slot.is_available != should_be_available:
            slot.is_available = should_be_available
            changed = True

    if changed:
        db.session.commit()


def ensure_loyalty_offers(user):
    loyalty = build_loyalty_profile(user)
    if loyalty["points"] >= 3000:
        ensure_offer(
            user,
            "Уход для лица",
            "Gold-привилегия: 25% на уход для лица и приоритетный выбор утреннего окна.",
            25,
            60,
        )
        ensure_offer(
            user,
            "Массаж спины",
            "Скрытая привилегия Velvet Gold: 20% на расслабляющий массаж спины.",
            20,
            45,
        )
        ensure_offer(
            user,
            "SPA-ритуал для волос",
            "Новинка для уровня Velvet Gold: 15% на SPA-ритуал для волос и восстановление блеска.",
            15,
            60,
        )
        db.session.commit()


def collect_dashboard_stats(user):
    now = datetime.now()
    active = Appointment.query.filter(
        Appointment.client_id == user.id,
        Appointment.status == "active",
        Appointment.start_time > now,
    ).all()
    history = Appointment.query.filter(
        Appointment.client_id == user.id,
        Appointment.status.in_(["completed", "cancelled"]),
    ).all()
    offers = Offer.query.filter(
        Offer.client_id == user.id,
        Offer.valid_until >= now.date(),
    ).all()

    favorite_service = None
    completed = [item for item in history if item.status == "completed"]
    if completed:
        favorite_service = Counter(appt.service.name for appt in completed).most_common(1)[0][0]

    next_visit = min(active, key=lambda item: item.start_time) if active else None
    loyalty = build_loyalty_profile(user, completed)
    return {
        "active_count": len(active),
        "history_count": len(history),
        "offers_count": len(offers),
        "next_visit": next_visit,
        "favorite_service": favorite_service,
        "bonus_points": loyalty["points"],
        "loyalty_tier": loyalty["tier_name"],
    }


def build_loyalty_profile(user, completed_appointments=None):
    completed = completed_appointments
    if completed is None:
        completed = Appointment.query.filter(
            Appointment.client_id == user.id,
            Appointment.status == "completed",
        ).order_by(Appointment.start_time.desc()).all()

    total_spent = int(sum(item.service.price for item in completed))
    spent_bonus = (
        db.session.query(db.func.coalesce(db.func.sum(Appointment.bonus_spent), 0))
        .filter(
            Appointment.client_id == user.id,
            Appointment.status != "cancelled",
        )
        .scalar()
        or 0
    )
    points = max((total_spent // 10) - int(spent_bonus), 0)
    visits = len(completed)

    tiers = [
        ("Start", 0),
        ("Velvet Bronze", 250),
        ("Velvet Silver", 600),
        ("Velvet Gold", 1100),
    ]

    tier_name = tiers[0][0]
    current_threshold = 0
    next_threshold = None
    for index, (name, threshold) in enumerate(tiers):
        if points >= threshold:
            tier_name = name
            current_threshold = threshold
            next_threshold = tiers[index + 1][1] if index + 1 < len(tiers) else None

    points_to_next = max(next_threshold - points, 0) if next_threshold is not None else 0
    progress_percent = 100
    if next_threshold is not None:
        span = max(next_threshold - current_threshold, 1)
        progress_percent = int(((points - current_threshold) / span) * 100)
        progress_percent = min(max(progress_percent, 0), 100)

    available_reward = "Персональный бонус уже открыт"
    if visits == 0:
        available_reward = "После первого визита откроется приветственный бонус"
    elif points < 250:
        available_reward = "Еще немного и откроется скидка 10% на любимую услугу"
    elif points < 600:
        available_reward = "Доступна скидка 10% или уходовый комплимент к записи"
    elif points < 1100:
        available_reward = "Доступен приоритетный подбор удобного окна и бонус 15%"
    else:
        available_reward = "Доступны закрытые предложения и повышенный бонус 15%"

    return {
        "points": points,
        "visits": visits,
        "total_spent": total_spent,
        "tier_name": tier_name,
        "next_threshold": next_threshold,
        "points_to_next": points_to_next,
        "progress_percent": progress_percent,
        "available_reward": available_reward,
        "spent_bonus": int(spent_bonus),
    }


def redeemable_services_for_user(user):
    loyalty = build_loyalty_profile(user)
    available_points = loyalty["points"]
    active_service_ids = {
        item.service_id
        for item in Appointment.query.filter(
            Appointment.client_id == user.id,
            Appointment.status == "active",
            Appointment.start_time > datetime.now(),
        ).all()
    }

    services = []
    for service in Service.query.order_by(Service.price.asc()).all():
        has_slot = Slot.query.filter(
            Slot.service_id == service.id,
            Slot.is_available.is_(True),
            Slot.start_time > datetime.now(),
        ).first() is not None
        if has_slot and service.price <= available_points and service.id not in active_service_ids:
            services.append(
                {
                    "service": service,
                    "bonus_cost": int(service.price),
                }
            )
    return services


def collect_admin_stats():
    now = datetime.now()
    return {
        "clients": User.query.filter_by(is_admin=False).count(),
        "masters": Master.query.count(),
        "future_appointments": Appointment.query.filter(
            Appointment.status == "active",
            Appointment.start_time > now,
        ).count(),
        "free_slots": Slot.query.filter(
            Slot.is_available.is_(True),
            Slot.start_time > now,
        ).count(),
    }


def available_dates_for_service(service_id):
    slots = (
        Slot.query.filter(
            Slot.is_available.is_(True),
            Slot.start_time > datetime.now(),
            Slot.service_id == service_id,
        )
        .order_by(Slot.start_time.asc())
        .all()
    )
    dates = []
    seen = set()
    for slot in slots:
        key = slot.start_time.date()
        if key not in seen:
            seen.add(key)
            dates.append(key)
    return dates


def available_times_for_service_date(service_id, selected_date):
    start = datetime.combine(selected_date, time.min)
    end = start + timedelta(days=1)
    slots = (
        Slot.query.filter(
            Slot.is_available.is_(True),
            Slot.start_time >= start,
            Slot.start_time < end,
            Slot.service_id == service_id,
        )
        .order_by(Slot.start_time.asc())
        .all()
    )
    values = []
    seen = set()
    for slot in slots:
        key = slot.start_time.strftime("%H:%M")
        if key not in seen:
            seen.add(key)
            values.append(key)
    return values


def available_slots_for_selection(service_id, selected_date, selected_time):
    start_dt = datetime.combine(selected_date, datetime.strptime(selected_time, "%H:%M").time())
    end_dt = start_dt + timedelta(minutes=1)
    return (
        Slot.query.join(Master)
        .filter(
            Slot.is_available.is_(True),
            Slot.service_id == service_id,
            Slot.start_time >= start_dt,
            Slot.start_time < end_dt,
        )
        .order_by(Master.name.asc())
        .all()
    )


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


with app.app_context():
    db.create_all()
    migrate_legacy_schema()
    seed_services()
    seed_masters()
    backfill_master_links()
    ensure_admin_user()
    ensure_future_slots()
    seed_demo_user()
    normalize_appointments_and_slots()


@app.context_processor
def inject_global_context():
    return {
        "now": datetime.now(),
        "salon_name": SALON_NAME,
        "media_url": media_url,
        "service_image_url": service_image_url,
        "new_service_names": {"Ламинирование ресниц", "SPA-ритуал для волос"},
    }


def _looks_like_remote_media(path):
    return bool(path and "://" in path)


def _cache_filename_for_url(src):
    parsed = urlparse(src)
    base_hash = hashlib.sha256(src.encode("utf-8")).hexdigest()
    extension = os.path.splitext(parsed.path)[1].lower()
    if not extension or len(extension) > 5:
        extension = mimetypes.guess_extension("image/jpeg") or ".jpg"
    return f"{base_hash}{extension}"


def _cached_remote_media_path(src):
    os.makedirs(MEDIA_CACHE_DIR, exist_ok=True)
    return os.path.join(MEDIA_CACHE_DIR, _cache_filename_for_url(src))


def proxy_media_url(src):
    return url_for("proxy_media", src=src)


def media_url(path, folder="images/landing"):
    if not path:
        path = "https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg?auto=compress&cs=tinysrgb&w=1000&h=1300&dpr=2"
    if _looks_like_remote_media(path):
        return proxy_media_url(path)
    return url_for("static", filename=f"{folder}/{path}")


def service_image_url(service_name):
    service_map = {
        "Стрижка женская": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f?auto=format&fit=crop&w=1200&q=80",
        "Стрижка мужская": "https://images.unsplash.com/photo-1622286342621-4bd786c2447c?auto=format&fit=crop&w=1200&q=80",
        "Маникюр": "https://images.unsplash.com/photo-1604902396830-aca29e19b067?auto=format&fit=crop&w=1200&q=80",
        "Массаж спины": "https://images.unsplash.com/photo-1515377905703-c4788e51af15?auto=format&fit=crop&w=1200&q=80",
        "Уход для лица": "https://images.unsplash.com/photo-1552693673-1bf958298935?auto=format&fit=crop&w=1200&q=80",
        "Окрашивание волос": "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=1200&q=80",
        "Архитектура бровей": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=1200&q=80",
        "Ламинирование ресниц": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=1200&q=80",
        "SPA-ритуал для волос": "https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?auto=format&fit=crop&w=1200&q=80",
    }
    image_src = service_map.get(
        service_name,
        "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=1200&q=80",
    )
    return proxy_media_url(image_src)


@app.route("/media/external")
def proxy_media():
    src = request.args.get("src", "").strip()
    if not _looks_like_remote_media(src):
        abort(404)

    cache_path = _cached_remote_media_path(src)
    if os.path.exists(cache_path):
        mimetype = mimetypes.guess_type(cache_path)[0] or "image/jpeg"
        return send_file(cache_path, mimetype=mimetype, max_age=86400)

    try:
        remote_request = Request(src, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(remote_request, timeout=12) as response:
            payload = response.read()
            mime_type = response.info().get_content_type() or "image/jpeg"
    except (URLError, ValueError, OSError):
        abort(404)

    with open(cache_path, "wb") as cache_file:
        cache_file.write(payload)

    return send_file(cache_path, mimetype=mime_type, max_age=86400)


@app.route("/")
def index():
    services = Service.query.order_by(Service.price.asc()).all()
    masters = Master.query.order_by(Master.name.asc()).all()
    preview_slots = Slot.query.filter(
        Slot.is_available.is_(True),
        Slot.start_time > datetime.now(),
    ).order_by(Slot.start_time.asc()).limit(3).all()
    return render_template(
        "landing.html",
        services=services,
        masters=masters,
        preview_slots=preview_slots,
        testimonial=LANDING_TESTIMONIAL,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f"Добро пожаловать, {user.name}!", "success")
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            if user.is_admin:
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("dashboard"))
        flash("Неверный email или пароль.", "danger")

    return render_template("login.html", form=form)


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
            is_admin=False,
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

        flash("Профиль создан. Теперь можно войти и выбрать удобное время.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for("admin_dashboard"))

    now = datetime.now()
    active_appointments = Appointment.query.filter(
        Appointment.client_id == current_user.id,
        Appointment.status == "active",
        Appointment.start_time > now,
    ).order_by(Appointment.start_time.asc()).all()

    history_preview = Appointment.query.filter(
        Appointment.client_id == current_user.id,
        Appointment.status.in_(["completed", "cancelled"]),
    ).order_by(Appointment.start_time.desc()).limit(3).all()

    slot_preview = Slot.query.filter(
        Slot.is_available.is_(True),
        Slot.start_time > now,
    ).order_by(Slot.start_time.asc()).limit(4).all()

    ensure_loyalty_offers(current_user)
    offers = Offer.query.filter(
        Offer.client_id == current_user.id,
        Offer.valid_until >= now.date(),
    ).order_by(Offer.valid_until.asc()).all()
    loyalty = build_loyalty_profile(current_user)

    return render_template(
        "dashboard.html",
        stats=collect_dashboard_stats(current_user),
        loyalty=loyalty,
        active_appointments=active_appointments,
        history_preview=history_preview,
        slot_preview=slot_preview,
        offers=offers,
    )


@app.route("/appointments")
@login_required
def appointments():
    if current_user.is_admin:
        return redirect(url_for("admin_dashboard"))

    items = Appointment.query.filter(
        Appointment.client_id == current_user.id,
        Appointment.status == "active",
        Appointment.start_time > datetime.now(),
    ).order_by(Appointment.start_time.asc()).all()
    return render_template("appointments.html", appointments=items)


@app.route("/history")
@login_required
def history():
    if current_user.is_admin:
        return redirect(url_for("admin_dashboard"))

    items = Appointment.query.filter(
        Appointment.client_id == current_user.id,
        Appointment.status.in_(["completed", "cancelled"]),
    ).order_by(Appointment.start_time.desc()).all()
    return render_template("history.html", appointments=items)


@app.route("/free-slots")
@login_required
def free_slots():
    if current_user.is_admin:
        return redirect(url_for("admin_dashboard"))

    selected_service_id = request.args.get("service_id", type=int)
    selected_date = request.args.get("date", "").strip()
    selected_time = request.args.get("time", "").strip()
    selected_master = request.args.get("master", "").strip()
    redeem_bonus = request.args.get("redeem_bonus") == "1"

    services = Service.query.order_by(Service.name.asc()).all()
    selected_service = None
    available_dates = []
    available_times = []
    master_slots = []
    selected_slot = None
    selected_date_label = ""

    if selected_service_id:
        selected_service = db.session.get(Service, selected_service_id)
        if selected_service is None:
            flash("Выбранная услуга не найдена.", "warning")
            return redirect(url_for("free_slots"))
        available_dates = available_dates_for_service(selected_service_id)

    parsed_date = None
    if selected_service and selected_date:
        try:
            parsed_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
            selected_date_label = parsed_date.strftime("%d.%m.%Y")
        except ValueError:
            flash("Некорректная дата.", "warning")
            return redirect(url_for("free_slots", service_id=selected_service_id))

    if selected_service and parsed_date:
        available_times = available_times_for_service_date(selected_service_id, parsed_date)

    if selected_service and parsed_date and selected_time:
        try:
            datetime.strptime(selected_time, "%H:%M")
        except ValueError:
            flash("Некорректное время.", "warning")
            return redirect(
                url_for(
                    "free_slots",
                    service_id=selected_service_id,
                    date=selected_date,
                )
            )
        master_slots = available_slots_for_selection(selected_service_id, parsed_date, selected_time)
        if selected_master:
            if selected_master == "any":
                selected_slot = master_slots[0] if master_slots else None
            else:
                selected_slot = next(
                    (slot for slot in master_slots if str(slot.master_id) == selected_master),
                    None,
                )

    return render_template(
        "free_slots.html",
        services=services,
        selected_service=selected_service,
        selected_service_id=selected_service_id,
        selected_date=selected_date,
        selected_date_label=selected_date_label,
        selected_time=selected_time,
        selected_master=selected_master,
        available_dates=available_dates,
        available_times=available_times,
        master_slots=master_slots,
        selected_slot=selected_slot,
        redeem_bonus=redeem_bonus,
    )


@app.route("/book/<int:slot_id>", methods=["GET", "POST"])
@login_required
def book_slot(slot_id):
    if current_user.is_admin:
        return redirect(url_for("admin_dashboard"))

    slot = Slot.query.get_or_404(slot_id)
    if not slot.is_available or slot.start_time <= datetime.now():
        flash("Это окно уже недоступно.", "warning")
        return redirect(url_for("free_slots"))

    conflict = Appointment.query.filter(
        Appointment.client_id == current_user.id,
        Appointment.status == "active",
        Appointment.start_time == slot.start_time,
    ).first()
    if conflict:
        flash("У вас уже есть запись на это время.", "warning")
        return redirect(url_for("appointments"))

    redeem_bonus = request.args.get("redeem_bonus") == "1"
    loyalty = build_loyalty_profile(current_user)
    can_redeem = redeem_bonus and loyalty["points"] >= int(slot.service.price)

    if request.method == "POST":
        redeem_bonus_post = request.form.get("redeem_bonus") == "1"
        loyalty = build_loyalty_profile(current_user)
        bonus_spent = 0
        notes = "Запись оформлена через упрощенную воронку."
        if redeem_bonus_post:
            if loyalty["points"] < int(slot.service.price):
                flash("Для оплаты этой услуги бонусами сейчас не хватает баллов.", "warning")
                return redirect(url_for("offers"))
            bonus_spent = int(slot.service.price)
            notes = f"Запись оформлена через бонусную программу. Списано {bonus_spent} бонусов."
        appointment = Appointment(
            client_id=current_user.id,
            service_id=slot.service_id,
            master_id=slot.master_id,
            start_time=slot.start_time,
            status="active",
            booked_by_name=current_user.name,
            booked_by_phone=current_user.phone,
            notes=notes,
            bonus_spent=bonus_spent,
        )
        slot.is_available = False
        db.session.add(appointment)
        db.session.commit()
        if bonus_spent:
            flash(f"Запись подтверждена. Списано {bonus_spent} бонусов.", "success")
        else:
            flash("Запись подтверждена. Все детали сохранены в личном кабинете.", "success")
        return redirect(url_for("appointments"))

    return render_template("booking.html", slot=slot, redeem_bonus=redeem_bonus, can_redeem=can_redeem)


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
        master_id=appointment.master_id,
        start_time=appointment.start_time,
    ).first()
    if slot is not None:
        slot.is_available = True

    db.session.commit()
    flash("Запись отменена. Окно снова открыто для бронирования.", "info")
    return redirect(url_for("appointments"))


@app.route("/offers")
@login_required
def offers():
    if current_user.is_admin:
        return redirect(url_for("admin_dashboard"))

    ensure_loyalty_offers(current_user)
    items = Offer.query.filter(
        Offer.client_id == current_user.id,
        Offer.valid_until >= datetime.now().date(),
    ).order_by(Offer.valid_until.asc()).all()
    return render_template(
        "offers.html",
        offers=items,
        loyalty=build_loyalty_profile(current_user),
        redeemable_services=redeemable_services_for_user(current_user),
    )


@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template("admin_dashboard.html", stats=collect_admin_stats())


@app.route("/admin/masters", methods=["GET", "POST"])
@admin_required
def admin_add_master():
    form = MasterForm(prefix="master")
    if form.validate_on_submit():
        db.session.add(
            Master(
                name=form.name.data,
                specialty=form.specialty.data,
                phone=form.phone.data,
                address=form.address.data,
                bio=form.bio.data,
                photo_filename=form.photo_filename.data,
            )
        )
        db.session.commit()
        flash("Мастер добавлен.", "success")
        return redirect(url_for("admin_masters_list"))
    if request.method == "POST":
        flash("Не удалось добавить мастера. Проверьте заполнение полей.", "danger")
    return render_template(
        "admin_add_master.html",
        form=form,
        page_title="Добавить мастера",
        page_heading="Добавить мастера",
        page_subtitle="Заполните большую понятную форму. После сохранения мастер появится в списке команды.",
        submit_label="Добавить мастера",
        form_action=url_for("admin_add_master"),
    )


@app.route("/admin/masters/<int:master_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_master(master_id):
    master = Master.query.get_or_404(master_id)
    form = MasterForm(prefix="master")

    if request.method == "GET":
        form.name.data = master.name
        form.specialty.data = master.specialty
        form.phone.data = master.phone
        form.address.data = master.address
        form.photo_filename.data = master.photo_filename
        form.bio.data = master.bio

    if form.validate_on_submit():
        master.name = form.name.data
        master.specialty = form.specialty.data
        master.phone = form.phone.data
        master.address = form.address.data
        master.photo_filename = form.photo_filename.data
        master.bio = form.bio.data
        db.session.commit()
        flash("Данные мастера обновлены.", "success")
        return redirect(url_for("admin_masters_list"))
    if request.method == "POST":
        flash("Не удалось обновить мастера. Проверьте заполнение полей.", "danger")

    return render_template(
        "admin_add_master.html",
        form=form,
        page_title="Редактировать мастера",
        page_heading="Редактировать мастера",
        page_subtitle="Обновите карточку мастера: имя, специализацию, контакты, фото и описание.",
        submit_label="Сохранить изменения",
        form_action=url_for("admin_edit_master", master_id=master.id),
    )


@app.route("/admin/masters/<int:master_id>/delete", methods=["POST"])
@admin_required
def admin_delete_master(master_id):
    master = Master.query.get_or_404(master_id)
    has_appointments = Appointment.query.filter_by(master_id=master.id).first() is not None
    if has_appointments:
        flash("Нельзя удалить мастера, пока с ним связаны записи клиентов или история визитов.", "warning")
        return redirect(url_for("admin_masters_list"))

    Slot.query.filter_by(master_id=master.id).delete(synchronize_session=False)
    db.session.delete(master)
    db.session.commit()
    flash("Мастер удален из списка команды.", "info")
    return redirect(url_for("admin_masters_list"))


@app.route("/admin/masters/list")
@admin_required
def admin_masters_list():
    masters = Master.query.order_by(Master.name.asc()).all()
    return render_template("admin_masters_list.html", masters=masters)


@app.route("/admin/slots", methods=["GET", "POST"])
@admin_required
def admin_add_slot():
    form = SlotForm(prefix="slot")
    form.service_id.choices = [
        (service.id, service.name) for service in Service.query.order_by(Service.name.asc()).all()
    ]
    form.master_id.choices = [
        (master.id, master.name) for master in Master.query.order_by(Master.name.asc()).all()
    ]

    if form.validate_on_submit():
        start_time = datetime.combine(form.date.data, form.slot_time.data)
        exists = Slot.query.filter_by(
            service_id=form.service_id.data,
            master_id=form.master_id.data,
            start_time=start_time,
        ).first()
        if exists:
            flash("Такое окно уже существует.", "warning")
        elif start_time <= datetime.now():
            flash("Нужно выбрать время в будущем.", "warning")
        else:
            db.session.add(
                Slot(
                    service_id=form.service_id.data,
                    master_id=form.master_id.data,
                    start_time=start_time,
                    is_available=True,
                )
            )
            db.session.commit()
            flash("Новое окно добавлено в расписание.", "success")
            return redirect(url_for("admin_appointments", date=form.date.data.strftime("%Y-%m-%d")))
    elif request.method == "POST":
        flash("Не удалось создать окно. Проверьте дату и время.", "danger")

    return render_template(
        "admin_add_slot.html",
        form=form,
        page_title="Создать окно",
        page_heading="Создать окно",
        page_subtitle="Выберите услугу, мастера, дату и время. Все поля специально увеличены, чтобы работать было проще.",
        submit_label="Создать окно",
        form_action=url_for("admin_add_slot"),
    )


@app.route("/admin/slots/<int:slot_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_slot(slot_id):
    slot = Slot.query.get_or_404(slot_id)
    form = SlotForm(prefix="slot")
    form.service_id.choices = [
        (service.id, service.name) for service in Service.query.order_by(Service.name.asc()).all()
    ]
    form.master_id.choices = [
        (master.id, master.name) for master in Master.query.order_by(Master.name.asc()).all()
    ]

    if request.method == "GET":
        form.service_id.data = slot.service_id
        form.master_id.data = slot.master_id
        form.date.data = slot.start_time.date()
        form.slot_time.data = slot.start_time.time()

    if form.validate_on_submit():
        new_start_time = datetime.combine(form.date.data, form.slot_time.data)
        exists = Slot.query.filter(
            Slot.id != slot.id,
            Slot.service_id == form.service_id.data,
            Slot.master_id == form.master_id.data,
            Slot.start_time == new_start_time,
        ).first()
        if exists:
            flash("Такое окно уже существует.", "warning")
        elif new_start_time <= datetime.now():
            flash("Нужно выбрать время в будущем.", "warning")
        else:
            slot.service_id = form.service_id.data
            slot.master_id = form.master_id.data
            slot.start_time = new_start_time
            db.session.commit()
            flash("Окно обновлено.", "success")
            return redirect(url_for("admin_appointments", date=form.date.data.strftime("%Y-%m-%d"), status="free"))
    elif request.method == "POST":
        flash("Не удалось обновить окно. Проверьте дату и время.", "danger")

    return render_template(
        "admin_add_slot.html",
        form=form,
        page_title="Изменить окно",
        page_heading="Изменить окно",
        page_subtitle="Обновите услугу, мастера, дату или время свободного окна.",
        submit_label="Сохранить изменения",
        form_action=url_for("admin_edit_slot", slot_id=slot.id),
    )


@app.route("/admin/slots/<int:slot_id>/delete", methods=["POST"])
@admin_required
def admin_delete_slot(slot_id):
    slot = Slot.query.get_or_404(slot_id)
    if not slot.is_available:
        flash("Нельзя удалить окно, если оно уже связано с активной записью.", "warning")
        return redirect(url_for("admin_appointments"))

    slot_date = slot.start_time.strftime("%Y-%m-%d")
    db.session.delete(slot)
    db.session.commit()
    flash("Свободное окно удалено.", "info")
    return redirect(url_for("admin_appointments", date=slot_date, status="free"))


@app.route("/admin/appointments")
@admin_required
def admin_appointments():
    selected_date = request.args.get("date", "").strip()
    selected_master_id = request.args.get("master_id", type=int)
    selected_service_id = request.args.get("service_id", type=int)
    selected_status = request.args.get("status", "").strip()
    selected_query = request.args.get("q", "").strip()

    if not any([selected_date, selected_master_id, selected_service_id, selected_status, selected_query]):
        selected_date = datetime.now().date().isoformat()

    query = Appointment.query.join(Service).join(Master)
    if selected_date:
        try:
            filter_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
            start = datetime.combine(filter_date, time.min)
            end = datetime.combine(filter_date, time.max)
            query = query.filter(Appointment.start_time >= start, Appointment.start_time <= end)
        except ValueError:
            selected_date = ""
    if selected_master_id:
        query = query.filter(Appointment.master_id == selected_master_id)
    if selected_service_id:
        query = query.filter(Appointment.service_id == selected_service_id)
    if selected_status and selected_status != "free":
        query = query.filter(Appointment.status == selected_status)
    if selected_query:
        lookup = f"%{selected_query}%"
        query = query.filter(
            or_(
                Appointment.booked_by_name.ilike(lookup),
                Appointment.booked_by_phone.ilike(lookup),
                Appointment.notes.ilike(lookup),
                Service.name.ilike(lookup),
                Master.name.ilike(lookup),
                Master.phone.ilike(lookup),
                Master.address.ilike(lookup),
            )
        )

    appointments = [] if selected_status == "free" else query.order_by(Appointment.start_time.asc()).all()

    slots_query = Slot.query.join(Service).join(Master).filter(
        Slot.is_available.is_(True),
        Slot.start_time > datetime.now(),
    )
    if selected_date:
        try:
            filter_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
            start = datetime.combine(filter_date, time.min)
            end = datetime.combine(filter_date, time.max)
            slots_query = slots_query.filter(Slot.start_time >= start, Slot.start_time <= end)
        except ValueError:
            pass
    if selected_master_id:
        slots_query = slots_query.filter(Slot.master_id == selected_master_id)
    if selected_service_id:
        slots_query = slots_query.filter(Slot.service_id == selected_service_id)
    if selected_status and selected_status != "free":
        slots_query = slots_query.filter(text("1=0"))
    if selected_query:
        lookup = f"%{selected_query}%"
        slots_query = slots_query.filter(
            or_(
                Service.name.ilike(lookup),
                Master.name.ilike(lookup),
                Master.phone.ilike(lookup),
                Master.address.ilike(lookup),
            )
        )

    free_slots = slots_query.order_by(Slot.start_time.asc()).all()
    return render_template(
        "admin_appointments.html",
        appointments=appointments,
        free_slots=free_slots,
        masters=Master.query.order_by(Master.name.asc()).all(),
        services=Service.query.order_by(Service.name.asc()).all(),
        selected_date=selected_date,
        selected_master_id=selected_master_id,
        selected_service_id=selected_service_id,
        selected_status=selected_status,
        selected_query=selected_query,
    )


@app.route("/admin/appointments/<int:appointment_id>/status", methods=["POST"])
@admin_required
def admin_update_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    target_status = request.form.get("status")
    if target_status not in {"active", "completed", "cancelled"}:
        flash("Неизвестный статус.", "warning")
        return redirect(url_for("admin_appointments"))

    appointment.status = target_status
    slot = Slot.query.filter_by(
        service_id=appointment.service_id,
        master_id=appointment.master_id,
        start_time=appointment.start_time,
    ).first()
    if slot is not None and appointment.start_time > datetime.now():
        slot.is_available = target_status != "active"

    db.session.commit()
    flash("Статус записи обновлен.", "success")
    return redirect(url_for("admin_appointments"))


if __name__ == "__main__":
    app.run(debug=True)
