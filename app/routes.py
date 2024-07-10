from flask import Blueprint, render_template, flash, redirect, url_for, request, abort, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.urls import url_parse
from . import db
from .models import User, Task
from .forms import RegistrationForm, LoginForm, TaskForm

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/tasks')
@login_required
def tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('tasks.html', tasks=tasks)

@main.route('/task/new', methods=['GET', 'POST'])
@login_required
def new_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, description=form.description.data, author=current_user, status='New tasks')
        db.session.add(task)
        db.session.commit()
        flash('Your task has been created!', 'success')
        return redirect(url_for('main.tasks'))
    return render_template('create_task.html', title='New Task', form=form)

@main.route('/task/<int:task_id>')
@login_required
def task(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template('task.html', title=task.title, task=task)

@main.route('/task/<int:task_id>/update', methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403)
    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.status='New tasks'
        db.session.commit()
        flash('Your task has been updated! Please modify the task status in Kanban', 'success')
        return redirect(url_for('main.task', task_id=task.id))
    elif request.method == 'GET':
        form.title.data = task.title
        form.description.data = task.description
    return render_template('create_task.html', title='Update Task', form=form)

@main.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403)
    db.session.delete(task)
    db.session.commit()
    flash('Your task has been deleted!', 'success')
    return redirect(url_for('main.tasks'))

@main.route('/kanban')
@login_required
def kanban():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('kanban.html', tasks=tasks)

@main.route('/update_task_status', methods=['POST'])
@login_required
def update_task_status():
    task_id = request.json.get('taskId')
    new_status = request.json.get('newStatus')
    task = Task.query.get(task_id)
    if task and task.user_id == current_user.id:
        valid_statuses = ['New tasks', 'Backlog', 'Todo', 'In Progress', 'Done']
        new_status = new_status.replace('-', ' ').title()
        if new_status == 'New Tasks':
            new_status = 'New tasks'
        if new_status in valid_statuses:
            task.status = new_status
        else:
            task.status = 'New tasks'  # Default to 'New tasks' if status is not recognized
        db.session.commit()
        return jsonify({'success': True, 'newStatus': task.status})
    return jsonify({'success': False, 'message': 'Task not found or unauthorized'}), 400