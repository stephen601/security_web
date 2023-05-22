from flask import Flask, render_template, request, redirect, url_for, session, json, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, time
from flask_session import Session
import random
import string





app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///USH.sqlite'
db = SQLAlchemy(app)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/tmp/flask_session'
Session(app)


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
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50))


class HelpDesk(db.Model):
    __tablename__ = 'HelpDesk'
    ticket_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_description = db.Column(db.String(100), nullable=False)
    ticket_date = db.Column(db.Date, nullable=False)
    ticket_time = db.Column(db.Time, nullable=False)
    resolved = db.Column(db.Boolean, default=False)


@app.route('/')
def index():
    if session.get('logged_in'):
        return render_template('index.html', logged_in=True)
    else:
        return render_template('index.html', logged_in=False)


@app.route('/tools')
def tools():
    tools = Tools.query.distinct(Tools.tool_name).all()
    return render_template('tools.html', tools=tools)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Users.query.filter_by(username=username, password=password).first()
        if user is not None:
            # Successful login
            session['logged_in'] = True
            session['user_key'] = ''.join(random.choices(string.ascii_letters + string.digits, k=24))
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials. Please try again.'
    else:
        # Check if the user is already logged in
        if session.get('logged_in'):
            return redirect(url_for('index'))
    return render_template('login.html', error=error)



@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/checkout', methods=['POST'])
def checkout():
    cart_data = request.form.get('cart')
    # Process the cart data here

    # For example, you can convert the JSON string back to a list of items
    cart = json.loads(cart_data)

    # You can then pass the cart data to the checkout page
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

        return redirect(url_for('index'))

    return render_template('contact.html')

@app.route('/services')
def services():
    services = Services.query.all()
    return render_template('services.html', services=services)

@app.route('/shop')
def shop():
    tools = Tools.query.distinct(Tools.tool_name).all()
    services = Services.query.all()
    return render_template('shop.html', tools=tools, services=services)




if __name__ == '__main__':
    app.run(debug=True)
