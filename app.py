from flask import Flask, render_template, request, redirect, url_for, session, json, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, time
from flask_session import Session
import random
import string
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask import flash






app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///USH.sqlite'
db = SQLAlchemy(app)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/tmp/flask_session'
Session(app)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
class Tools(db.Model):
    __tablename__ = 'Tools'
    tool_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tool_name = db.Column(db.String(50), nullable=False)
    tool_price = db.Column(db.Float, nullable=False)
    tool_image = db.Column(db.String(50))

class Services(db.Model):
    __tablename__ = 'Services'
    service_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_description = db.Column(db.String(100), nullable=False)
    service_price = db.Column(db.Float, nullable=False)
    service_image = db.Column(db.String(50))


class Users(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(50))

    # Add a method to set the password using a hashed value
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Add a method to check if the provided password matches the hashed password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class HelpDesk(db.Model):
    __tablename__ = 'HelpDesk'
    ticket_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_description = db.Column(db.String(100), nullable=False)
    ticket_date = db.Column(db.Date, nullable=False)
    ticket_time = db.Column(db.Time, nullable=False)
    resolved = db.Column(db.Boolean, default=False)
    fix = db.Column(db.String(100))



@app.route('/')
def index():
    if session.get('logged_in'):
        username = session.get('username')
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('index.html', logged_in=True, first_name=user.first_name, last_name=user.last_name)
    return render_template('index.html', logged_in=False)




@app.route('/tools')
def tools():
    tools = Tools.query.distinct(Tools.tool_name).all()
    return render_template('tools.html', tools=tools)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = Users.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            # Successful login
            session['logged_in'] = True
            session['username'] = username
            session['user_key'] = ''.join(random.choices(string.ascii_letters + string.digits, k=24))

            # Initialize the user's cart if it doesn't exist
            if 'cart' not in session:
                session['cart'] = []

            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.')
    else:
        # Check if the user is already logged in
        if session.get('logged_in'):
            return redirect(url_for('index'))
    return render_template('login.html', form=form)




@app.route('/logout')
def logout():
    # Clear the user's cart and username when they log out
    session.pop('logged_in', None)
    session.pop('cart', None)
    session.pop('username', None)
    return redirect(url_for('index'))



@app.route('/help')
def help():
    if not session.get('logged_in'):
        # User is not logged in, handle the error or redirect to the login page
        return redirect(url_for('login'))

    return render_template('help.html')


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if not session.get('logged_in'):
        # User is not logged in, handle the error or redirect to the login page
        return redirect(url_for('login'))

    if request.method == 'POST':
        cart_data = request.form.get('cart')
        new_cart = json.loads(cart_data)

        # Fetch the existing cart from the session
        existing_cart = session.get('cart', [])

        # Update quantities if the item is already in the cart, else add the item
        for new_item in new_cart:
            for existing_item in existing_cart:
                if new_item['id'] == existing_item['id']:
                    existing_item['quantity'] += new_item['quantity']
                    break
            else:  # If the item was not found in the cart, add it
                existing_cart.append(new_item)

        session['cart'] = existing_cart

        return render_template('checkout.html', cart=existing_cart)
    else:
        # For a GET request, fetch the cart from the session
        cart = session.get('cart', [])
        return render_template('checkout.html', cart=cart)




@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    item_id = request.form.get('itemId')
    item_name = request.form.get('itemName')
    item_image = request.form.get('itemImage')
    item_price = request.form.get('itemPrice')

    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == item_id:
            item['quantity'] += 1
            break
    else:
        cart.append({
            'id': item_id,
            'name': item_name,
            'image': item_image,
            'price': item_price,
            'quantity': 1
        })

    session['cart'] = cart  # Store the updated cart data in the session

    return 'Success'




@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        description = request.form['description']
        date_str = request.form['date']
        time_str = request.form['time']

        # Convert the date and time strings to Python date and time objects
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_obj = datetime.strptime(time_str, '%H:%M').time()

        help_desk_entry = HelpDesk(
            ticket_description=description,
            ticket_date=date,
            ticket_time=time_obj
        )
        db.session.add(help_desk_entry)
        db.session.commit()

        return redirect(url_for('helpdesk'))

    return render_template('contact.html')


@app.route('/services')
def services():
    services = Services.query.all()
    return render_template('services.html', services=services)

@app.route('/shop')
def shop():
    tools = Tools.query.distinct(Tools.tool_name).all()
    services = Services.query.all()
    logged_in = session.get('logged_in', False)  # Get the value of 'logged_in' from the session, default to False if not present
    return render_template('shop.html', tools=tools, services=services, logged_in=logged_in)


@app.route('/account', methods=['GET', 'POST'])
def account():
    if not session.get('logged_in'):
        # User is not logged in, handle the error or redirect to the login page
        return redirect(url_for('login'))

    username = session.get('username')
    user = Users.query.filter_by(username=username).first()
    if not user:
        # User does not exist, handle the error
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate the password and confirm password fields
        if password != confirm_password:
            error = 'Password and confirm password do not match.'
            return render_template('account.html', user=user, error=error)

        # Update the user information
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        # Update the password if a new password is provided
        if password:
            user.set_password(password)

        db.session.commit()

        return redirect(url_for('account'))

    return render_template('account.html', user=user)



@app.route('/employee')
def employee():
        return render_template('employee.html', username=session.get('username'))


@app.route('/helpdesk', methods=['GET', 'POST'])
def helpdesk():
    if request.method == 'POST':
        ticket_id = request.form.get('ticket_id')
        resolved = request.form.get('resolved') == 'true'
        fix = request.form.get('fix')

        ticket = HelpDesk.query.get(ticket_id)
        ticket.resolved = resolved
        ticket.fix = fix

        db.session.execute(
            text("UPDATE HelpDesk SET resolved=:resolved, fix=:fix WHERE ticket_id=:ticket_id"),
            {'resolved': resolved, 'fix': fix, 'ticket_id': ticket_id}
        )
        db.session.commit()

    tickets = HelpDesk.query.all()
    return render_template('helpdesk.html', tickets=tickets)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        # Check if the username already exists
        existing_user = Users.query.filter_by(username=username).first()
        if existing_user:
            error = 'Username already exists. Please choose a different username.'
            return render_template('signup.html', error=error)

        # Create a new user
        new_user = Users(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        new_user.set_password(password)  # Hash the password

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Redirect to the login page after successful sign-up
        return redirect(url_for('login'))

    # If it's a GET request, render the sign-up form
    return render_template('signup.html')

@app.route('/update-account', methods=['POST'])
def update_account():
    if not session.get('logged_in'):
        # User is not logged in, handle the error or redirect to the login page
        return redirect(url_for('login'))

    user_id = request.form.get('user_id')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if password != confirm_password:
        error = 'New password and confirm password do not match.'
        user = Users.query.get(user_id)
        return render_template('account.html', user=user, error=error)

    user = Users.query.get(user_id)
    if not user:
        # User does not exist, handle the error
        return redirect(url_for('login'))

    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.set_password(password)  # Set the new password
    db.session.commit()

    return redirect(url_for('account'))






if __name__ == '__main__':
    app.run(debug=True)