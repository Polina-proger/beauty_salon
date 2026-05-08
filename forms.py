from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    TimeField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class RegistrationForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Телефон", validators=[Optional(), Length(max=20)])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField(
        "Повторите пароль",
        validators=[DataRequired(), EqualTo("password")],
    )
    submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")


class BookingDetailsForm(FlaskForm):
    booked_by_name = StringField(
        "Кто записывается",
        validators=[DataRequired(), Length(min=2, max=120)],
    )
    booked_by_phone = StringField(
        "Телефон для связи",
        validators=[DataRequired(), Length(min=6, max=30)],
    )
    notes = TextAreaField(
        "Комментарий к записи",
        validators=[Optional(), Length(max=500)],
    )
    submit = SubmitField("Подтвердить запись")


class MasterForm(FlaskForm):
    name = StringField("Имя мастера", validators=[DataRequired(), Length(max=100)])
    specialty = StringField("Специализация", validators=[DataRequired(), Length(max=120)])
    phone = StringField("Телефон мастера", validators=[DataRequired(), Length(max=20)])
    address = StringField("Адрес салона", validators=[DataRequired(), Length(max=180)])
    bio = TextAreaField("Краткое описание", validators=[Optional(), Length(max=500)])
    photo_filename = StringField(
        "Имя файла фото",
        validators=[Optional(), Length(max=120)],
    )
    submit = SubmitField("Добавить мастера")


class SlotForm(FlaskForm):
    service_id = SelectField("Услуга", coerce=int, validators=[DataRequired()])
    master_id = SelectField("Мастер", coerce=int, validators=[DataRequired()])
    date = DateField("Дата", format="%Y-%m-%d", validators=[DataRequired()])
    slot_time = TimeField("Время", format="%H:%M", validators=[DataRequired()])
    submit = SubmitField("Создать окно")
