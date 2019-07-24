from flask import Flask, request, redirect, render_template, session, flash 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:admin@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body):
        self.title = title
        self.body = body

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
    allowed_routes = ['login_user', 'show_blog', 'add_user', 'index', 'static']
    if 'username' not in session and request.endpoint not in allowed_routes:
        return redirect('/login') 

def empty_val(x):
    if x:
        return True
    else:
        return False


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():        
    if request.method == 'POST':   
        title = request.form['title_entry']
        body = request.form['body_entry'] 
        owner = User.query.filter_by(username=session['username']).first()
        post_new = Blog(title, body, owner)

        if empty_val(title) and empty_val(body):
            db.session.add(post_new)
            db.session.commit()
            post_link = "blog?id=" + str(post_new.id)
            return redirect(post_link)

        else:
            if not empty_val(title) and not empty_val(body):
                flash('Enter blog title and entry', 'error')
                return render_template('mainblog.html', title=title, body=body)
            elif not empty_val(title):
                flash('Enter blog title', 'error')
                return render_template('mainblog.html', title=title)
            elif not empty_val(body):
                flash('Enter blog entry', 'error')
                return render_template('mainblog.html', body=body)

    else:
        return render_template('mainblog.html')

@app.route('/')
def index():
    return redirect('/bloglist')

@app.route('/bloglist')
def bloglist():
    blog_id = request.args.get('id')
    single_user_id = requet.args.get('owner_id')

    if (blog_id):
        blogs = Blog.query.get(blog_id)    
        return render_template('bloglist.html', blogs=blogs)

    else: 
        if (single_user_id):
            ind_user_blog_posts = Blog.query.filter_by(owner_id=single_user_id)
            return render_template('user.html', posts=ind_user_blog_posts)
        else:
            all_blog_posts = Blog.query.all() 
            return render_template('bloglist.html', posts=all_user_blog_posts)        
        
@app.route('/signup', methods=['POST', 'GET'])
def add_user():
    if request.method == 'POST':
        user_name = request.form['username']
        user_password = request.form['password']
        user_password_validate = request.form['password_validate']

        if not empty_val(user_name) or not empty_val(user_password) or not empty_val(user_password_validate)
            flash('All fields are required', 'error')
            return render_template('signup.html')

        if user_password != user_password_validate:
            flash('Passwords must match', 'error')
            return render_template('signup.html')

        if len(user_name) < 8 and len(user_password) < 8:
            flash('User name and password must be at least 8 characters', 'error')
            return render_template('signup.html')

        if len(user_name) < 8:
            flash('User name must be at least 8 characters', 'error')
            return render_template('signup.html')

        if len(user_password) < 8:
            flash('Password must be at least 8 characters', 'error')
            return render_template('signup.html')
        

        existing_user = User.query.filter_by(username=user_name).first()

        if not existing_user:
            new_user = User(user_name, user_password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = user_name
            flash('New user created', 'Success')
            return redirect ('/newpost')
        
        else:
            flash('This username already exits', 'error')
            return render_template('signup.html')
    else:
        return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username and not password:
            flash('Username and password cannot be blank', 'error')
            return render_template('login.html')

        if not username:
            flash('Username cannot be blank', 'error')
            return render_template('login.html')

        if not password:
            flash('Password cannot be blank', 'error')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()

        if not user:
            flash('Username does not exist', 'error')
            return render_template('login.html')

        if user.password != password:
            flash('Password invalid', 'error')
            return render_template('login.html')
        
        if user and user.password == password:
            session['username'] = username
            return redirect('newpost')

    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    flash('Logout complete', 'Success')
    return redirect('/blog')





if __name__ == '__main__':
    app.run()