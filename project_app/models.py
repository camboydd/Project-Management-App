from database import db
import datetime


class Project(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("title", db.String(200))
    text = db.Column("text", db.String(100))
    date = db.Column("date", db.String(50))
    category = db.Column("category", db.String(50))
    image_link = db.Column("image_link", db.String(500))
    favorite = db.Column("favorite", db.Boolean)
    shared_with = db.Column("shared_with", db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    comments = db.relationship("Comment", backref="project", cascade="all, delete-orphan", lazy=True)

    def __init__(self, title, text, date, user_id, category, image_link):
        self.title = title
        self.text = text
        self.date = date
        self.user_id = user_id
        self.favorite = False
        self.shared_with = ""
        self.category = category
        self.image_link = image_link


class User(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    first_name = db.Column("first_name", db.String(100))
    last_name = db.Column("last_name", db.String(100))
    email = db.Column("email", db.String(100))
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    sorting_order = db.Column("order", db.Boolean)
    projects = db.relationship("Project", backref="user", lazy=True)
    comments = db.relationship("Comment", backref="user", lazy=True)

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.registered_on = datetime.date.today()
        self.sorting_order = False


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False)
    content = db.Column(db.VARCHAR, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    score = db.Column("score", db.Integer)
    upvote_users = db.Column(db.String(100))
    downvote_users = db.Column(db.String(100))

    def __init__(self, content, project_id, user_id):
        self.date_posted = datetime.date.today()
        self.content = content
        self.project_id = project_id
        self.user_id = user_id
        self.score = 0
        self.upvote_users = "|"
        self.downvote_users = "|"

class Tasks(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    project_id = db.Column("project_id", db.Integer)
    date_posted = db.Column("date_posted", db.String(50))
    start_date = db.Column("start_date", db.String(50))
    end_date = db.Column("end_date", db.String(50))
    main_content = db.Column("main_content", db.String(200))
    status = db.Column("status",db.String(100))
    category = db.Column("category", db.String(50))
    start_time = db.Column("start_time", db.String(50))
    end_time = db.Column("end_time", db.String(50))
    extra_details = db.Column("extra_details", db.String(200))

    def __init__(self, project_id, date_posted, user_id, start_date, end_date, main_content, category, start_time, end_time, extra_details):
        self.project_id = project_id
        self.date_posted = date_posted
        self.user_id = user_id
        self.start_date = start_date
        self.end_date = end_date
        self.main_content = main_content
        self.status = "Waiting"
        self.category = category
        self.start_time = start_time
        self.end_time = end_time
        self.extra_details = extra_details