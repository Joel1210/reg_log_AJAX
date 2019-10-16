from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import connectToMySQL
from datetime import datetime
from flask_bcrypt import Bcrypt
import re



app = Flask(__name__)

app.secret_key = "shhhhhh"

bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 


@app.route('/')
def toWelcome():
    return redirect('/welcome/')
    
@app.route('/welcome/')
def welcome():

    return render_template('index.html')

@app.route("/username", methods=['POST'])
def username():
    found = False
    mysql = connectToMySQL('Flax_Ajax')   
    query = "SELECT username from User WHERE User.username = %(user)s;"
    data = { 'user': request.form['rusername'] }
    result = mysql.query_db(query, data)
    print(request.form['rusername'])
    count = len(request.form['rusername'])
    if result:
        found = True
    return render_template('partials/username.html', found=found, name_length=count)  

@app.route('/register', methods=['POST'])
def register():
    
    isValid = True

    if len(request.form['rfname']) < 2:
        flash('Your first name must have at least 2 characters!', category="firstname")
        isValid = False
       
    if request.form['rfname'].isalpha() == False:
        flash('Your first name can only contain alphabetical characters!', category="firstname")
        isValid = False

    if len(request.form['rlname']) <2:
        flash('Your last name must have at least 2 characters!', category="lastname")
        isValid = False
    
    if request.form['rlname'].isalpha() == False:
        flash('Your last name can only contain alphabetical characters!', category="lastname")
        isValid = False

    if not EMAIL_REGEX.match(request.form['remail']):
        flash('You must enter a valid email address!', category="email")
        isValid = False

    query = 'SELECT count(*) r FROM User WHERE email = %(em)s'

    data = {
        "em" : request.form['remail']
    }
    
    mysql = connectToMySQL('Flax_Ajax')
    check = mysql.query_db(query, data)

    print('*****', check)
    
    if check[0]['r'] != 0:
        flash('Your email is already registered!', category="email")
        isValid = False

    if len(request.form['rpassword']) < 8:
        flash('Your password must have at least 8 characters!', category="password")
        isValid = False
        # return redirect('/')

    if request.form['rpassword'] != request.form['rconfirm']:
        flash("Your passwords don't match!", category="passwordconfirm")
        isValid = False

    if not isValid:
        return redirect('/welcome/')
    
    else: 
        pw_hash = bcrypt.generate_password_hash(request.form['rpassword'])
        
        query = "INSERT INTO User(first_name, last_name, username, email, passwordhash) VALUES (%(fn)s, %(ln)s, %(un)s, %(em)s, %(pwh)s);"

        data = {
            "fn": request.form["rfname"],
            "ln": request.form["rlname"],
            "un": request.form['rusername'],
            "em": request.form["remail"],
            "pwh": pw_hash
        }
        mysql = connectToMySQL('Flax_Ajax')
        users = mysql.query_db(query, data)


        flash("You've successfully registered!", category="successregister")


        session['id'] = users
        session['username'] = data['un']
        session['firstname'] = data['fn']
        session['lastname'] = data['ln']
        session['email'] = data['em']

        return redirect('/success')

        

   
@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/login', methods=['POST'])
def login():

    query = 'SELECT * FROM User WHERE email = %(em)s;'

    data = {
        "em" : request.form['lemail']
    }

    mysql = connectToMySQL('Flax_Ajax')
    info = mysql.query_db(query, data)
   

    if len(info) != 1:
        flash('Invalid email, please try again', category='loginerror' )
        return redirect('/welcome/')

    if len(info) ==1:
        if bcrypt.check_password_hash(info[0]['passwordhash'], request.form['lpassword']):
            session['id'] = info[0]['user_id']  
            session['firstname'] = info[0]['first_name']
            session['lastname'] = info[0]['last_name']
            session['email'] = info[0]['email']

            flash("You've successfully logged in!", category='loggedin' )
            return redirect('/success')
        else:
            flash('Invalid password, please try again', category='pwerror')
            return redirect('/welcome/')





   




@app.route('/logout')
def logout():
    session.clear()

    return redirect('/welcome')





if __name__ == "__main__":
    app.run(debug=True)