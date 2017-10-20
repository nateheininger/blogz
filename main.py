from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'asecretkey'


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
    username = db.Column(db.String(120))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')


    def __init__(self, username, password):
        self.username = username
        self.password = password

def logged_in():
    owner = User.query.filter_by(username=session['username']).first()
    return owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    
    form_value = request.args.get('id')
    user_id = request.args.get('user')

    if request.method == 'POST':
        title_error = ''
        body_error = ''
      
        blog_title = request.form['title']
        blog_body = request.form['body']


        if blog_title == '':
            title_error = "Please enter a blog title!" 

        if blog_body == '':
            body_error = "A blog entry should not be empty!"


        if not title_error and not body_error:     
            new_blog = Blog(blog_title,blog_body, logged_in())
            db.session.add(new_blog)
            db.session.commit()
            blog = Blog.query.filter_by(title=blog_title).first()
            return redirect('/blog?id={0}'.format(blog.id))
        
        else:
            return render_template('newpost.html', title="My Blog!", title_error=title_error, body_error=body_error, blog_title=blog_title, blog_body=blog_body)
    
    if request.method == 'GET' and form_value:
        blog = Blog.query.get(form_value)
        return render_template('single.html', title="My Blog", blog=blog)  

    if request.method == 'GET' and user_id:
        blogs = Blog.query.filter_by(owner_id=user_id).all() 
        return render_template('individual.html', blogs=blogs)   
   
    
    blogs = Blog.query.all()  
    return render_template('blog.html',title="My Blog!", blogs=blogs)        

@app.route('/new-post', methods=['POST', 'GET'])
def new_post():
    return render_template('newpost.html', title="My Blog!")

@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if not user:
            flash('Username not found. Please sign up!')
            return render_template('login.html')

        if user and user.password != password:
            flash('Password is incorrect!')
            return render_template('login.html', username=username)

        if user and user.password == password:
            session['username'] = username
            flash('logged in!')
            return redirect('/new-post')
        else:
            flash('User Password Incorrect, or user does not exist', 'error')
            pass


    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']
        verify = request.form['verify']       

        user_error = ''
        password_error = ''
        verify_error = ''


        if len(user_name) < 3 or len(user_name) > 20:
            user_error = "Please enter a valid username"

        else:
            user_name = user_name

        if len(password) < 3 or len(password) > 20:
            password_error = "Please enter a valid password"
        
        if verify != password:
            verify_error = "Passwords must match!"
        
    
        existing_user = User.query.filter_by(username=user_name).first()

        if existing_user:
            user_error = "That username is taken!"

        if not existing_user and not user_error and not password_error and not verify_error:
            new_user = User(user_name, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = user_name
            return redirect('/new-post')
        
        else:
            return render_template('signup.html', user_error = user_error, password_error = password_error, verify_error = verify_error, username = user_name)

        
    return render_template('signup.html')

@app.route('/logout', methods=['POST'])
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


if __name__ == '__main__':
    app.run()