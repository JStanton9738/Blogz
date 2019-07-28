from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:admin@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'anything'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'index', 'add_user', 'logout', 'bloglist', 'login_user']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login') 

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', title='Home', users=users)

@app.route('/blog', methods=['POST', 'GET'])
def bloglist():
    ind_user = request.args.get('user')
    blog_id = request.args.get('id')

    if blog_id == None and ind_user == None:
        blogs = Blog.query.all()    
        return render_template('bloglist.html', blogs=blogs, title='Blog Archive')

    if blog_id:          
        blog = Blog.query.get(blog_id)
        return render_template('bloglist.html', blog=blog, title='Individual Blog Entries')

    if ind_user:
        blogs = Blog.query.all()    
        user = User.query.get(ind_user)
        return render_template('singleUser.html', blogs=blogs, user=user, title='Blog Posts')



@app.route('/login', methods=['POST', 'GET'])
def login_user():
    username = ''
    password = ''
    username_error = ''
    password_error = ''
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if not username and not password:
            flash('Create account first.', 'error')
            return render_template('login.html')

        if not username:
            flash('Username cannot be blank.', 'error')
            return render_template('login.html')

        if not password:
            flash('Password cannot be blank.', 'error')
            return render_template('login.html')

        if not username:
            flash('Username does not exist.', 'error')
            return render_template('login.html')

        if password != password:
            flash('Password invalid.', 'error')
            return render_template('login.html')
        
        if user and password:
            session['username'] = username
            return redirect('/newpost')

    return render_template('login.html', username=username, username_error=username_error, password_error=password_error)

        
@app.route('/signup', methods=['POST', 'GET'])
def add_user():
    username = ''
    password = ''
    username_error = ''
    password_error = ''
    validate_password = ''
    validate_password_error = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        validate_password = request.form['validate_password']

        existing_user = User.query.filter_by(username=username).first()

        if not username and not password and not validate_password:
            flash('All fields are required.', 'error')
            return render_template('signup.html')

        if password != validate_password:
            flash('Passwords must match.', 'error')
            return render_template('signup.html')

        if len(username) < 3 and len(password) < 3:
            flash('User name and password must be at least 3 characters.', 'error')
            return render_template('signup.html')

        if len(username) < 3:
            flash('User name must be at least 3 characters.', 'error')
            return render_template('signup.html')

        if len(password) < 3:
            flash('Password must be at least 3 characters.', 'error')
            return render_template('signup.html')
    
        if not username_error and not password_error and not validate_password_error:
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                flash('New user created!', 'Success')
                return redirect ('/newpost')
        
            else:
                flash('This username already exits.', 'error')
                return render_template('signup.html')
    else:
        return render_template('signup.html', username=username, username_error=username_error, password=password, validate_password=validate_password, validate_password_error=validate_password_error)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():  

    if request.method == 'POST':   
        title = request.form['title_entry']
        body = request.form['body_entry'] 
        owner = User.query.filter_by(username=session['username']).first()
        title_error = ''
        body_error = ''
        
        if not title:
            title_error = 'Please enter blog title'

        if not body:
            body_error = 'Please enter blog text' 

        if not title_error and not body_error:
            new_blog = Blog(title, body, owner)
            db.session.add(new_blog)
            db.session.commit()
                      
            return redirect('/blog?id={}'.format(new_blog.id))

        else:
            return render_template('mainblog.html', title=title, body=body, title_error=title_error, body_error=body_error, owner=owner)

    return render_template('mainblog.html', title=title)

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    del session['username']
    return redirect('/blog')


if __name__ == '__main__':
    app.run()