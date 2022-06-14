from app import app
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from app.forms import SignUpForm, PostForm, LoginForm
from app.models import Post, User

@app.route("/index")
@app.route("/")
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        # Get the data from the form fields
        email = form.email.data
        username = form.username.data
        password = form.password.data
        # Query the User table for any users with username/email from form
        user_check = User.query.filter((User.email == email)|(User.username == username)).all()
        if user_check:
            flash('A user with that username and/or email already exists. Please try again.', 'danger')
            return redirect(url_for('signup'))

        # Add the user to the database
        new_user = User(email=email, username=username, password=password)

        # Show message of success
        flash(f'{new_user.username} has successfully signed up!', 'success')
        # redirect back to the homepage
        return redirect(url_for('index'))

    return render_template('signup.html', form=form)


@app.route('/create-post', methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        # Get data from the form
        post_title = form.title.data
        post_body = form.body.data
        post_address = form.address.data
        user_id = current_user.id
        # Add new post to database with form info
        new_post = Post(title=post_title, body=post_body, address=post_address, user_id=user_id)
        # Flash a success message to the user
        flash(f'"{new_post.title}" by {new_post.author.username} has been created', 'success')
        # Return to the home page
        return redirect(url_for('index'))

    return render_template('create_post.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Get the data from form
        username = form.username.data
        password = form.password.data
        # Query our user table for a user with the username from the form
        user = User.query.filter_by(username=username).first()
        # If the user exists and the password for that user is correct
        if user is not None and user.check_password(password):
            # log the user in
            login_user(user)
            # Flash a success message
            flash(f"Welcome back, {user.username}!", "primary")
            # Redirect to the home page
            return redirect(url_for('index'))
        
        # If user is None or password incorrect, flash message and redirect to login
        flash('Incorrect username and/or password. Please try again.', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have logged out of the Phonebook', 'secondary')
    return redirect(url_for('index'))


@app.route('/posts/<post_id>')
def view_single_post(post_id):
    post = Post.query.get_or_404(post_id) # SELECT * FROM post WHERE id = post_id  --(post_id comes from the URL)
    return render_template('single_post.html', post=post)


@app.route('/edit-posts/<post_id>', methods=["GET", "POST"])
@login_required
def edit_single_post(post_id):
    post_to_edit = Post.query.get_or_404(post_id)
    if current_user != post_to_edit.author:
        flash("You do not have permission to edit that post", "danger")
        return redirect(url_for('index'))
    form = PostForm()
    if form.validate_on_submit():
        # Get form data
        new_title = form.title.data
        new_body = form.body.data
        new_address = form.address.data
        # update the post to edit with the form data
        post_to_edit.update(title=new_title, body=new_body, address=new_address)

        flash(f'{post_to_edit.title} has been updated', 'primary')
        return redirect(url_for('view_single_post', post_id=post_to_edit.id))

    return render_template('edit_post.html', post=post_to_edit, form=form)


@app.route('/delete-posts/<post_id>')
@login_required
def delete_single_post(post_id):
    post_to_delete = Post.query.get_or_404(post_id)
    if current_user != post_to_delete.author:
        flash("You do not have permission to delete that post", "danger")
        return redirect(url_for('index'))
    post_to_delete.delete()
    flash(f'{post_to_delete.title} has been deleted', 'info')
    return redirect(url_for('index'))
    