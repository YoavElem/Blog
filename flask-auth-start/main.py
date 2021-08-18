import flask
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import flask_sqlalchemy
app = Flask(__name__)


login_manager=LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(1000))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB. 
# db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        all_users=db.session.query(User).all()
        for user in all_users:
            if user.email==request.form.get('email'):
                flask.flash('Already registered with email')
                return render_template('register.html')
        new_user=User(email=request.form.get('email'),password=generate_password_hash(request.form.get('password'),method='pbkdf2:sha256',salt_length=8),name=request.form.get('name'))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('secrets',pre_user=new_user))
    return render_template("register.html")


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        pre_user = User.query.filter_by(email=request.form.get('email')).first()
        if pre_user!=None:
            if check_password_hash(pre_user.password,request.form.get('password')):
                login_user(pre_user)
                return redirect(url_for('secrets',pre_user=pre_user))
            else:
                flask.flash('Boobs')
        else:
            flask.flash('Ass')
        # print()
        # print('user logged in')
        # if user.is_authenticated:
        #     login_user(user)
        #     return redirect(url_for('secrets'))
        # if user!=None:
        #
    return render_template("login.html")


@app.route('/secrets',methods=['POST','GET'])
@login_required
def secrets():
    return render_template('secrets.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/download',methods=['POST','GET'])
def download():
    filename='cheat_sheet.pdf'
    app.config['UPLOAD_FOLDER']='/static/files'
    print(app.config['UPLOAD_FOLDER'])

    uploads=app.root_path+app.config['UPLOAD_FOLDER']
    print(uploads)
    return send_from_directory(directory=uploads,path=filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
