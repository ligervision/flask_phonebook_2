from app import app, db
from app.models import User, Post

@app.shell_context_processor
def make_context():
    return {'db': db, 'Post': Post, 'User': User}

@app.before_first_request
def create_tables():
    db.create_all()
    