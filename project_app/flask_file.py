# imports

from __future__ import print_function
import os                 # os is used to get environment variables IP & PORT
from flask import Flask   # Flask is the web app that we will customize
from flask import render_template
from flask import request, url_for, redirect, session, send_from_directory, flash
from database import db
from models import Project as Project
from models import User as User
from models import Comment as Comment
from models import Tasks as Tasks
from forms import RegisterForm, LoginForm, CommentForm
from werkzeug.utils import secure_filename
import bcrypt
import sys
app = Flask(__name__)     # create an app
UPLOAD_FOLDER = 'static/images'


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_project_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SE3155'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#  Bind SQLAlchemy db object to this Flask app
db.init_app(app)
# Setup models
with app.app_context():
    db.create_all()   # run under the app context

@app.route('/')
@app.route('/index')
def index():
    if session.get('user'):
        return render_template('index.html', user=session['user'])
    return render_template("index.html")


@app.route('/test')
def get_test():
    return render_template('test.html')

@app.route('/projects')
def get_projects():
    if session.get('user'):
        user = db.session.query(User).filter_by(id=session['user_id']).one()
        #order displays the projects alphabetically or reverse-alphabetically per user
        order = user.sorting_order
        #list the favorite projects first
        my_projects = db.session.query(Project).filter_by(user_id=session['user_id'], favorite=1).all()
        my_projects = sort_projects_list(my_projects, order)
        #then list the non-favorite projects
        my_projects_2 = db.session.query(Project).filter_by(user_id=session['user_id'], favorite=0).all()
        my_projects_2 = sort_projects_list(my_projects_2, order)

        #combine the sorted favorites and non-favorites into a single list
        my_projects += my_projects_2

        username = user.email
        my_projects_3 = []
        projects = db.session.query(Project).all()
        for project in projects:
            shared_users = project.shared_with.split("|")
            for shared_user in shared_users:
                if username == shared_user:
                    my_projects_3.append(project)
        my_projects_3 = sort_projects_list(my_projects_3, order)

        my_projects += my_projects_3

        return render_template('projects.html',  projects=my_projects, user=user)
    else:
        return redirect(url_for('login'))

def sort_projects_list(my_projects, order = False):
    if session.get('user'):
        #sort alphabetically by default or specify reverse alphabetical with parameter 'order'
        my_projects_names = []
        for project in my_projects:
            my_projects_names.append(project.title)
        my_projects_names = sorted(my_projects_names, reverse = order)
        sorted_projects = []
        for name in my_projects_names:
            for project in my_projects:
                if name == project.title:
                    sorted_projects.append(project)
        my_projects = sorted_projects
        return my_projects

@app.route('/projects/sort', methods=['POST'])
def sort_projects():
    if session.get('user'):
        #inverts the sorting order and redisplays the projects. Toggles between alphabetical and reverse-alphabetical.
        #get user
        user = db.session.query(User).filter_by(id=session['user_id']).one()
        #invert sorting_order
        user.sorting_order = not user.sorting_order
        #update the session
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('get_projects'))
    else:
        return redirect(url_for('login'))

@app.route('/projects/<project_id>')
def get_project(project_id):
    if session.get('user'):
        my_project = db.session.query(Project).filter_by(id=project_id).one()
        main_user = db.session.query(User).filter_by(id=my_project.user_id).one()
        user = db.session.query(User).filter_by(id=session['user_id']).one()
        tasks = db.session.query(Tasks).filter_by(project_id = my_project.id)
        form = CommentForm()
        return render_template('project.html',  project=my_project, user=user, main_user=main_user.email, form=form, tasks=tasks)
    else:
        return redirect(url_for('login'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/projects/new', methods=['GET','POST'])
def new_project():
    if session.get('user'):
        if request.method == 'POST':
            title = request.form['title']
            text = request.form['projectText']
            category = request.form['category']
            from datetime import date
            today = date.today()
            today = today.strftime("%m-%d-%Y")
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_link = url_for('uploaded_file', filename=filename)
            new_record = Project(title, text, today, session['user_id'], category, image_link)
            db.session.add(new_record)
            db.session.commit()

            return redirect(url_for('get_projects'))
        else:
            return render_template('new_project.html', user = session['user_id'])
    else:
        return redirect(url_for('login'))


@app.route('/projects/edit/<project_id>', methods=['GET', 'POST'])
def update_project(project_id):
    if session.get('user'):
        if request.method == 'POST':
            project = db.session.query(Project).filter_by(id=project_id).one()
            #get title data
            title = request.form['title']
            #get project data
            text = request.form['projectText']
            category = request.form['category']
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                image_link = project.image_link
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_link = url_for('uploaded_file', filename=filename)
            # update project data
            project.title = title
            project.text = text
            project.image_link = image_link
            project.category = category
            # update project in DB
            db.session.add(project)
            db.session.commit()

            return redirect(url_for('get_projects'))
        else:
            # retrieve project from database
            my_project = db.session.query(Project).filter_by(id=project_id).one()

            return render_template('new_project.html', project=my_project, user=session['user'])
    else:
        return redirect(url_for('login'))

@app.route('/projects/delete/<project_id>', methods=['POST'])
def delete_project(project_id):
    if session.get('user'):
        # retrieve project from database
        my_project = db.session.query(Project).filter_by(id=project_id).one()
        db.session.delete(my_project)
        db.session.commit()

        return redirect(url_for('get_projects'))
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():
        # salt and hash password
        h_password = bcrypt.hashpw(
            request.form['password'].encode('utf-8'), bcrypt.gensalt())
        # get entered user data
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        # create user model
        new_user = User(first_name, last_name, request.form['email'], h_password)
        # add user to database and commit
        db.session.add(new_user)
        db.session.commit()
        # save the user's name to the session
        session['user'] = first_name
        session['user_id'] = new_user.id  # access id value from user model of this newly added user
        # show user dashboard view
        return redirect(url_for('index'))

    # something went wrong - display register view
    return render_template('register.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    # validate_on_submit only validates using POST
    if login_form.validate_on_submit():
        # we know user exists. We can use one()
        the_user = db.session.query(User).filter_by(email=request.form['email']).one()
        # user exists check password entered matches stored password
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), the_user.password):
            # password match add user info to session
            session['user'] = the_user.first_name
            session['user_id'] = the_user.id
            # render view
            return redirect(url_for('index'))

        # password check failed
        # set error message to alert user
        login_form.password.errors = ["Incorrect username or password."]
        return render_template("login.html", form=login_form)
    else:
        # form did not validate or GET request
        return render_template("login.html", form=login_form)


@app.route('/logout')
def logout():
    # check if a user is saved in session
    if session.get('user'):
        session.clear()

    return redirect(url_for('index'))


@app.route('/projects/<project_id>/comment', methods=['POST'])
def new_comment(project_id):
    if session.get('user'):
        comment_form = CommentForm()
        # validate_on_submit only validates using POST
        if comment_form.validate_on_submit():
            # get comment data
            comment_text = request.form['comment']
            if comment_text:
                new_record = Comment(comment_text, int(project_id), session['user_id'])
                db.session.add(new_record)
                db.session.commit()

            username = request.form['username']
            if username:
                #new_record = Comment(comment_text, int(project_id), session['user_id'])
                # retrieve project from database
                my_project = db.session.query(Project).filter_by(id=project_id).one()
                #append user to the share list
                my_project.shared_with += (username.strip() + "|" )
                #update the session
                db.session.add(my_project)
                db.session.commit()

        return redirect(url_for('get_project', project_id=project_id))

    else:
        return redirect(url_for('login'))

#favorite a project
@app.route('/projects/favorite/<project_id>', methods=['POST'])
def favorite_project(project_id):
    if session.get('user'):
        # retrieve project from database
        my_project = db.session.query(Project).filter_by(id=project_id).one()
        #toggle the value of favorite
        my_project.favorite = not my_project.favorite
        #update the session
        db.session.add(my_project)
        db.session.commit()

        return redirect(url_for('get_projects'))
    else:
        return redirect(url_for('login'))

#upvotes a comment for the user
@app.route('/projects/<project_id>/<comment_id>/up', methods=['POST'])
def upvote_comment(project_id, comment_id):
    if session.get('user'):
        #user, project, and comment are items in the database
        user = db.session.query(User).filter_by(id=session['user_id']).one()
        project = db.session.query(Project).filter_by(id=project_id).one()
        comment = db.session.query(Comment).filter_by(id=comment_id).one()
        #pull the users who have upvoted the comment
        upvote_users = [""]
        #pull the users who have downvoted the comment
        downvote_users = [""]
        #check that users have upvoted the comment
        if comment.upvote_users:
            upvote_users = comment.upvote_users.split("|")
        #check that users have downvoted the comment
        if comment.downvote_users:
            downvote_users = comment.downvote_users.split("|")
        #check that the user has not already upvoted the comment
        if user.email not in upvote_users:
            #increase the comment score
            comment.score += 1
            #append the user to the list of upvote users
            comment.upvote_users += (user.email + "|")
            #check if the user had previously downvoted the comment
            if user.email in downvote_users:
                #increase the comment score (-1 -> +1 not 0)
                comment.score += 1
                #remove the user from the list of downvoted users
                downvote_users.remove(user.email)
                #ensure that upvote users is not empty
                if not downvote_users:
                    downvote_users = "|"
                #reformat upvote users for the database
                else:
                    downvote_users = "|".join(downvote_users)
                comment.downvote_users = downvote_users
            db.session.add(comment)
            db.session.commit()

        return redirect(url_for('get_project', project_id = project_id))
    else:
        return redirect(url_for('login'))

#downvotes a comment for the user
@app.route('/projects/<project_id>/<comment_id>/down', methods=['POST'])
def downvote_comment(project_id, comment_id):
    if session.get('user'):
        #user, project, and comment are items in the database
        user = db.session.query(User).filter_by(id=session['user_id']).one()
        project = db.session.query(Project).filter_by(id=project_id).one()
        comment = db.session.query(Comment).filter_by(id=comment_id).one()
        #pull the users who have upvoted the comment
        upvote_users = comment.upvote_users
        #pull the users who have downvoted the comment
        downvote_users = comment.downvote_users
        #check that users have upvoted the comment
        if comment.upvote_users:
            upvote_users = comment.upvote_users.split("|")
        #check that users have downvoted the comment
        if comment.downvote_users:
            downvote_users = comment.downvote_users.split("|")
        #check that the user has not already downvoted the comment
        if user.email not in downvote_users:
            #decrease the comment score
            comment.score -= 1
            #append the user to the list of downvote users
            comment.downvote_users += (user.email + "|")
            #check if the user had previously upvoted the comment
            if user.email in upvote_users:
                #decrease the comment score (+1 -> -1 not 0)
                comment.score -= 1
                #remove the user from the list of upvoted users
                upvote_users.remove(user.email)
                #ensure that upvote users is not empty
                if not upvote_users:
                    upvote_users = "|"
                #reformat upvote users for the database
                else:
                    upvote_users = "|".join(upvote_users)
                comment.upvote_users = upvote_users
            db.session.add(comment)
            db.session.commit()

        return redirect(url_for('get_project', project_id = project_id))
    else:
        return redirect(url_for('login'))

#removes the upvote or downvote for the user
@app.route('/projects/<project_id>/<comment_id>/remove_vote', methods=['POST'])
def remove_vote(project_id, comment_id):
    if session.get('user'):
        #user, project, and comment are items in the database
        user = db.session.query(User).filter_by(id=session['user_id']).one()
        project = db.session.query(Project).filter_by(id=project_id).one()
        comment = db.session.query(Comment).filter_by(id=comment_id).one()
        #pull the users who have upvoted the comment
        upvote_users = comment.upvote_users
        #pull the users who have downvoted the comment
        downvote_users = comment.downvote_users
        #check that users have upvoted the comment
        if comment.upvote_users:
            upvote_users = comment.upvote_users.split("|")
        #check that users have downvoted the comment
        if comment.downvote_users:
            downvote_users = comment.downvote_users.split("|")
        #remove the user from the upvoted users and decrease the comment score
        if user.email in upvote_users:
            comment.score -= 1
            upvote_users.remove(user.email)
        #remove the user from the downvoted users and increase the comment score
        if user.email in downvote_users:
            comment.score += 1
            downvote_users.remove(user.email)
        #ensure that the upvoted users is not None type
        if not upvote_users:
            upvote_users = "|"
        #ensure that the downvoted users is not None type
        if not downvote_users:
            downvote_users = "|"
        #reformat upvote and downvote users for the database
        comment.upvote_users = "|".join(upvote_users)
        comment.downvote_users = "|".join(downvote_users)
        db.session.add(comment)
        db.session.commit()

        return redirect(url_for('get_project', project_id = project_id))
    else:
        return redirect(url_for('login'))

#removes the comment
@app.route('/projects/<project_id>/<comment_id>/remove', methods=['POST'])
def remove_comment(project_id, comment_id):
    if session.get('user'):
        #user, project, and comment are items in the database
        user = db.session.query(User).filter_by(id=session['user_id']).one()
        project = db.session.query(Project).filter_by(id=project_id).one()
        comment = db.session.query(Comment).filter_by(id=comment_id).one()

        #check that the user is the owner of the comment or the owner of the project
        if comment.user_id == user.id or project.user_id == user.id:
            db.session.delete(comment)
            db.session.commit()

        return redirect(url_for('get_project', project_id = project_id))
    else:
        return redirect(url_for('login'))


@app.route('/projects/<project_id>/task/new', methods=['GET','POST'])
def new_task(project_id):
    if session.get('user'):
        if request.method == 'POST':
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            main_content = request.form['main_content']
            category = request.form['category']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            from datetime import date, datetime
            today = today = date.today()
            extra_details = request.form['extra_details']
            # start_date = start_date.strftime("%m-%d-%Y")
            # end_date = end_date.strftime("%m-%d-%Y")

            new_task = Tasks(project_id, today, session['user_id'], start_date, end_date, main_content, category, start_time, end_time,extra_details)
            db.session.add(new_task)
            db.session.commit()

            return redirect(url_for('get_project', project_id = project_id))
        else:
            a_user = db.session.query(User).filter_by(email='bdelunap@uncc.edu').one()
            return render_template('new_task.html', user = session['user_id'])
    else:
        return redirect(url_for('login'))


@app.route('/projects/<project_id>/task/edit/<task_id>', methods=['GET', 'POST'])
def update_task(task_id,project_id):
    if session.get('user'):
        if request.method == 'POST':
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            main_content = request.form['main_content']
            category = request.form['category']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            status = request.form['status']
            extra_details = request.form['extra_details']
            task = db.session.query(Tasks).filter_by(id=task_id).one()
            # update note data
            task.start_date = start_date
            task.end_date = end_date
            task.main_content = main_content
            task.category = category
            task.start_time = start_time
            task.end_time = end_time
            task.status = status
            task.extra_details = extra_details
            # update note in DB
            db.session.add(task)
            db.session.commit()

            return redirect(url_for('get_project', project_id = project_id))
        else:
            # retrieve note from database
            my_task = db.session.query(Tasks).filter_by(id=task_id).one()

            return render_template('new_task.html', task=my_task, user=session['user'])
    else:
        return redirect(url_for('login'))

@app.route('/projects/<project_id>/task/delete/<task_id>', methods=['POST'])
def delete_task(task_id,project_id):
    if session.get('user'):
        # retrieve note from database
        task = db.session.query(Tasks).filter_by(id=task_id).one()
        db.session.delete(task)
        db.session.commit()

        return redirect(url_for('get_project', project_id = project_id))
    else:
        return redirect(url_for('login'))


 
app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 5000)),debug=True)
