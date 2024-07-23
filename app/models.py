from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from datetime import datetime
from enum import Enum

class AccessLevel(Enum):
    NOOB = 1
    ANON = 2
    MOOT = 3

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    tasks = db.relationship('Task', backref='author', lazy='dynamic')
    claims = db.relationship('Tag', back_populates='user')
    access_level = db.Column(db.Enum(AccessLevel), default=AccessLevel.NOOB)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def claim_task(self, task):
        claim_tag = Tag(name=f'Claimed by {self.username}', type='claim', user=self)
        task.add_tag(claim_tag)
        db.session.add(claim_tag)
        db.session.commit()
    def unclaim_task(self, task):
        claim_tags = [tag for tag in task.tags if tag.type == 'claim' and tag.user == self]
        for tag in claim_tags:
            task.remove_tag(tag)
            db.session.delete(tag)
        db.session.commit()

    def set_access_level(self, level):
        if isinstance(level, AccessLevel):
            self.access_level = level
        elif isinstance(level, str):
            self.access_level = AccessLevel[level.upper()]
        else:
            raise ValueError("Invalid access level")
    def has_access_level(self, level):
        if isinstance(level, str):
            level = AccessLevel[level.upper()]
        return self.access_level.value >= level.value
    
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='New tasks')
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tags = db.relationship('Tag', secondary='task_tags', back_populates='tasks')

    def __repr__(self):
        return f'<Task {self.title}>'
    
    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)

    def is_claimed_by(self, user):
        return any(tag.type == 'claim' and tag.user == user for tag in self.tags)
    
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # e.g., 'claim', 'category', 'priority', etc.

    # For 'claim' type tags, we'll associate a user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', back_populates='claims')

    # Many-to-many relationship with Task
    tasks = db.relationship('Task', secondary='task_tags', back_populates='tags')

    def __repr__(self):
        return f'<Tag {self.name} ({self.type})>'

# Association table for the many-to-many relationship between Task and Tag
task_tags = db.Table('task_tags',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)