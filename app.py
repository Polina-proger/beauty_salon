from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Service, Appointment, Slot, Offer
from forms import RegistrationForm, LoginForm, BookingForm
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Создание таблиц и начальных данных
# Инициализация базы данных при старте приложения (без before_first_request)
with app.app_context():
    db.create_all()
    if Service.query.count() == 0:
        # Добавляем тестовые услуги
        services = [
            Service(name='Стрижка женская', duration=60, price=2500, description='Модельная стрижка'),
            Service(name='Стрижка мужская', duration=45, price=1800, description='Классическая или современная'),
            Service(name='Маникюр', duration=90, price=2000, description='Аппаратный маникюр + покрытие'),
            Service(name='Массаж спины', duration=60, price=3000, description='Расслабляющий массаж'),
        ]
        db.session.add_all(services)
        db.session.commit()

    if Slot.query.count() == 0:
        # Генерируем свободные окна на ближайшие 7 дней
        services = Service.query.all()
        today = datetime.now().date()
        for day_offset in range(1, 8):
            day = today + timedelta(days=day_offset)
            for hour in [10, 12, 14, 16]:
                for service in services:
                    start = datetime(day.year, day.month, day.day, hour, 0)
                    slot = Slot(service_id=service.id, start_time=start, is_available=True)
                    db.session.add(slot)
        db.session.commit()

    if User.query.filter_by(email='demo@example.com').first() is None:
        demo = User(name='Анна Петрова', email='demo@example.com', phone='+79991234567')
        demo.set_password('demo123')
        db.session.add(demo)
        db.session.commit()
        # Добавим персональное предложение
        offer = Offer(
            client_id=demo.id,
            service_id=1,
            description='Скидка 20% на первую стрижку!',
            discount_percent=20,
            valid_until=datetime.now().date() + timedelta(days=30)
        )
        db.session.add(offer)
        db.session.commit()

# --- Маршруты ---

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна! Теперь войдите.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Добро пожаловать, {user.name}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Неверный email или пароль', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Активные записи (будущие)
    now = datetime.now()
    active_appointments = Appointment.query.filter(
        Appointment.client_id == current_user.id,
        Appointment.status == 'active',
        Appointment.start_time > now
    ).order_by(Appointment.start_time).limit(3).all()

    # Ближайшие свободные окна
    upcoming_slots = Slot.query.filter(
        Slot.is_available == True,
        Slot.start_time > now
    ).order_by(Slot.start_time).limit(3).all()

    # Актуальные предложения
    today = datetime.now().date()
    offers = Offer.query.filter(
        Offer.client_id == current_user.id,
        Offer.valid_until >= today
    ).limit(3).all()

    return render_template('dashboard.html',
                           active_appointments=active_appointments,
                           upcoming_slots=upcoming_slots,
                           offers=offers)

@app.route('/appointments')
@login_required
def appointments():
    now = datetime.now()
    active = Appointment.query.filter(
        Appointment.client_id == current_user.id,
        Appointment.status == 'active',
        Appointment.start_time > now
    ).order_by(Appointment.start_time).all()
    return render_template('appointments.html', appointments=active)

@app.route('/history')
@login_required
def history():
    past = Appointment.query.filter(
        Appointment.client_id == current_user.id,
        Appointment.status.in_(['completed', 'cancelled'])
    ).order_by(Appointment.start_time.desc()).all()
    return render_template('history.html', appointments=past)

@app.route('/free-slots')
@login_required
def free_slots():
    now = datetime.now()
    slots = Slot.query.filter(
        Slot.is_available == True,
        Slot.start_time > now
    ).order_by(Slot.start_time).all()

    # Группировка по дате для удобства отображения
    slots_by_date = {}
    for slot in slots:
        date_str = slot.start_time.strftime('%Y-%m-%d')
        slots_by_date.setdefault(date_str, []).append(slot)

    return render_template('free_slots.html', slots_by_date=slots_by_date)

@app.route('/book/<int:slot_id>', methods=['POST'])
@login_required
def book_slot(slot_id):
    slot = Slot.query.get_or_404(slot_id)
    if not slot.is_available:
        flash('Это окно уже занято', 'warning')
        return redirect(url_for('free_slots'))

    # Создаём запись
    appointment = Appointment(
        client_id=current_user.id,
        service_id=slot.service_id,
        start_time=slot.start_time,
        status='active'
    )
    slot.is_available = False
    db.session.add(appointment)
    db.session.commit()
    flash(f'Вы записаны на {slot.start_time.strftime("%d.%m.%Y %H:%M")}', 'success')
    return redirect(url_for('appointments'))

@app.route('/offers')
@login_required
def offers():
    today = datetime.now().date()
    active_offers = Offer.query.filter(
        Offer.client_id == current_user.id,
        Offer.valid_until >= today
    ).all()
    return render_template('offers.html', offers=active_offers)

if __name__ == '__main__':
    app.run(debug=True)
