from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:admin@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():        
    if request.method == 'POST':   
        title = request.form['title_entry']
        body = request.form['body_entry'] 
        title_error = ''
        body_error = '' 


        if not title:            
            title_error = 'Please enter blog title'
           
        if not body:
            body_error = 'Please enter blog text' 
        
    
        if not title_error and not body_error:    
            new_blog = Blog(title, body)
            db.session.add(new_blog)
            db.session.commit()

            return redirect('./bloglist?id={}'.format(new_blog.id))
        else:    
            return render_template('mainblog.html', title=title, body=body, title_error=title_error, body_error=body_error)
    else:
        return render_template('mainblog.html')

@app.route('/')
def index():
    return redirect('/bloglist')

@app.route('/bloglist')
def bloglist():
    blog_id = request.args.get('id')

    if blog_id == None:
        blogs = Blog.query.all()    
        return render_template('bloglist.html', title = "build-a-blog", blogs=blogs)

    else:          
        blog = Blog.query.get(blog_id)
        return render_template('singleentry.html', title = "build-a-blog", blog=blog)


if __name__ == '__main__':
    app.run()