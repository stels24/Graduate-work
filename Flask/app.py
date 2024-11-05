from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///siteflask.db'
db = SQLAlchemy(app)
Bootstrap(app)
login_manager = LoginManager(app)


class User(UserMixin, db.Model):
    """
    Модель пользователя для хранения информации о пользователях.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    tasks = db.relationship('Task', backref='author', lazy=True)


class Task(db.Model):
    """
    Модель задачи для хранения информации о задачах.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)
    data_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_end_plan = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='запланирована')
    data_end = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class RegistrationForm(FlaskForm):
    """
    Форма для регистрации пользователей.
    """
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    """
    Форма для входа пользователей.
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class TaskForm(FlaskForm):
    """
    Форма для создания и обновления задач.
    """
    name = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание')
    category = StringField('Категория', validators=[DataRequired()])
    data_end_plan = DateField('Планируемая дата завершения', validators=[DataRequired()])
    status = SelectField('Статус', choices=[('запланирована', 'запланирована'), ('в работе', 'в работе'), ('выполнена', 'выполнена')], default='запланирована')
    submit = SubmitField('Сохранить задачу')


@app.route("/")
def home():
    """
    Главная страница, которая перенаправляет на страницу приветствия, если пользователь аутентифицирован, или на страницу входа в систему в противном случае.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))


@login_manager.user_loader
def load_user(user_id):
    """
    Функция загрузки пользователя для Flask-Login.
    """
    return User.query.get(int(user_id))


@app.route("/register", methods=['GET', 'POST'])
def register():
    """
    Страница для регистрации пользователей.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Ваша учетная запись была создана! Теперь вы можете войти в систему', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    """
    Страница для входа пользователей.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Вход не удался. Пожалуйста, проверьте адрес электронной почты и пароль', 'danger')
    return render_template('login.html', title='Вход', form=form)


@app.route("/logout")
def logout():
    """
    Страница для выхода пользователей.
    """
    logout_user()
    return redirect(url_for('login'))


@app.route("/dashboard")
def dashboard():
    """
    Страница панели управления.
    """
    if current_user.is_authenticated:
        tasks = Task.query.filter_by(author=current_user).all()
        return render_template('dashboard.html', tasks=tasks)
    else:
        return redirect(url_for('login'))


@app.route("/task/new", methods=['GET', 'POST'])
@login_required
def new_task():
    """
    Страница для создания новой задачи.
    """
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(name=form.name.data, description=form.description.data, category=form.category.data, data_end_plan=form.data_end_plan.data, status=form.status.data, author=current_user)
        db.session.add(task)
        db.session.commit()
        flash('Ваша задача была создана!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_task.html', title='Новая задача', form=form, legend='Новая задача')


@app.route("/task/<int:task_id>")
@login_required
def task(task_id):
    """
    Страница для просмотра задачи.
    """
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403)
    return render_template('task.html', title=task.name, task=task)


@app.route("/task/<int:task_id>/update", methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    """
    Страница для обновления задачи.
    """
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403)
    form = TaskForm()
    if form.validate_on_submit():
        task.name = form.name.data
        task.description = form.description.data
        task.category = form.category.data
        task.data_end_plan = form.data_end_plan.data
        task.status = form.status.data
        db.session.commit()
        flash('Ваша задача была обновлена!', 'success')
        return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        form.name.data = task.name
        form.description.data = task.description
        form.category.data = task.category
        form.data_end_plan.data = task.data_end_plan
        form.status.data = task.status
    return render_template('create_task.html', title='Обновить задачу', form=form, legend='Обновить задачу')


@app.route("/task/<int:task_id>/delete", methods=['POST'])
@login_required
def delete_task(task_id):
    """
    Страница для удаления задачи.
    """
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403)
    db.session.delete(task)
    db.session.commit()
    flash('Ваша задача была удалена!', 'success')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Create a test user
        user = User.query.filter_by(username='Mike').first()
        if not user:
            user = User(username='Mike', email='mike@test.ru', password='1q2w3e')
            db.session.add(user)
            db.session.commit()

        # Create 10 test tasks
        if Task.query.count() == 0:
            for i in range(10):
                task = Task(name=f'Test Task {i+1}', description=f'This is test task {i+1}', category='Test', data_end_plan=datetime.utcnow() + timedelta(days=i+1), author=user)
                db.session.add(task)
            db.session.commit()

    app.run(debug=True)

