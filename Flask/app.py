from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_bootstrap import Bootstrap

#from wtforms import StringField, SubmitField, TextAreaField, DateField, SelectField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///siteflask.db'
db = SQLAlchemy(app)
Bootstrap(app)
login_manager = LoginManager(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    tasks = db.relationship('Task', backref='author', lazy=True)

class Task(db.Model):
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
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')



class TaskForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    category = StringField('Category', validators=[DataRequired()])
    data_end_plan = DateField('Data End Plan', validators=[DataRequired()])
    status = SelectField('Status', choices=[('запланирована', 'запланирована'), ('в работе', 'в работе'), ('выполнена', 'выполнена')], default='запланирована')
    submit = SubmitField('Save Task')



@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Ваша учетная запись создана! Теперь вы можете войти в систему', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Войти не удалось. Пожалуйста, проверьте адрес электронной почты и пароль', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/dashboard")
def dashboard():
    if current_user.is_authenticated:
        tasks = Task.query.filter_by(author=current_user).all()
        return render_template('dashboard.html', tasks=tasks)
    else:
        return redirect(url_for('login'))


@app.route("/task/new", methods=['GET', 'POST'])
@login_required
def new_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(name=form.name.data, description=form.description.data, category=form.category.data, data_end_plan=form.data_end_plan.data, status=form.status.data, author=current_user)
        db.session.add(task)
        db.session.commit()
        flash('Ваша задача выполнена!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_task.html', title='New Task', form=form, legend='New Task')

@app.route("/task/<int:task_id>")
@login_required
def task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403)
    return render_template('task.html', title=task.name, task=task)


@app.route("/task/<int:task_id>/update", methods=['GET', 'POST'])
@login_required
def update_task(task_id):
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
        flash('Ваше задание было обновлено!', 'success')
        return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        form.name.data = task.name
        form.description.data = task.description
        form.category.data = task.category
        form.data_end_plan.data = task.data_end_plan
        form.status.data = task.status
    return render_template('create_task.html', title='Update Task', form=form, legend='Update Task')



@app.route("/task/<int:task_id>/delete", methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403)
    db.session.delete(task)
    db.session.commit()
    flash('Ваше задание было удалено!', 'success')
    return redirect(url_for('dashboard'))


# ...

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Создайте тестового пользователя
        user = User.query.filter_by(username='Mike').first()
        if not user:
            user = User(username='Mike', email='mike@test.ru', password='1q2w3e')
            db.session.add(user)
            db.session.commit()

        # Создайте 10 тестовых заданий
        if Task.query.count() == 0:
            for i in range(10):
                task = Task(name=f'Test Task {i+1}', description=f'This is test task {i+1}', category='Test', data_end_plan=datetime.utcnow() + timedelta(days=i+1), author=user)
                db.session.add(task)
            db.session.commit()

    app.run(debug=True)
