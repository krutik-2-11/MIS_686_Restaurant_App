from flask import Flask, render_template,request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text, inspect

# Define MySQL connection details
mysql_username = 'admin'
mysql_password = 'hw6secure'
mysql_host = 'database-1.cjo3spnhosm6.ap-northeast-1.rds.amazonaws.com'
mysql_db_name = 'RestaurantCo'

app = Flask(__name__)

# Configure the MySQL connection using Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{mysql_username}:{mysql_password}@{mysql_host}/{mysql_db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define your model
class Customer(db.Model):
    CustomerID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    Phone = db.Column(db.String(20), nullable=False)

    __tablename__ = 'Customers' 

    def __repr__(self):
        return f'<Customer {self.CustomerID} - {self.FirstName} {self.LastName}>'


# Define your model for Reservations
class Reservation(db.Model):
    ReservationID = db.Column(db.Integer, primary_key=True)
    ReservationTime = db.Column(db.Time, nullable=False)
    ReservationDate = db.Column(db.Date, nullable=False)
    NumGuests = db.Column(db.Integer, nullable=False)
    CustomerID = db.Column(db.Integer, db.ForeignKey('Customers.CustomerID'), nullable=False)
    customer = db.relationship('Customer', backref=db.backref('reservations', lazy=True))

    __tablename__ = 'Reservations'

    def __repr__(self):
        return f'<Reservation {self.ReservationID} - Time: {self.ReservationTime}, Date: {self.ReservationDate}, Guests: {self.NumGuests}>'


# Define your model for Feedback
class Feedback(db.Model):
    FeedbackId = db.Column(db.Integer, primary_key=True)
    FeedbackDate = db.Column(db.Date, nullable=False)
    FeedbackText = db.Column(db.Text, nullable=False)
    CustomerID = db.Column(db.Integer, db.ForeignKey('Customers.CustomerID'), nullable=False)
    customer = db.relationship('Customer', backref=db.backref('feedbacks', lazy=True))

    __tablename__ = 'Feedback'

    def __repr__(self):
        return f'<Feedback {self.FeedbackId} - Date: {self.FeedbackDate}, Text: {self.FeedbackText}>'

class MenuCat(db.Model):
    ItemName = db.Column(db.Text, primary_key=True)
    Price = db.Column(db.Integer, nullable=False)
    CategoryName = db.Column(db.Text, nullable=False)

    __tablename__ = 'MenuCat'

    def __repr__(self):
        return f'<MenuCat {self.ItemName} - Price: {self.Price}, Text: {self.CategoryName}>'
    

class Menu(db.Model):
    ItemID = db.Column(db.Integer, primary_key=True)
    ItemName = db.Column(db.Text, nullable=False)
    Price = db.Column(db.Integer, nullable=False)

    __tablename__ = 'Menu'

    def __repr__(self):
        return f'<Menu {self.ItemID} - Price: {self.Price}, Text: {self.ItemName}>'

# Define your routes
@app.route('/')
def index():
    # Render the template with the list of customers
    return render_template('index.html')

# Page to list all the customers
@app.route('/custom-query')
def custom_query():

    # Write your custom SQL query
    sql_query = text('SELECT * FROM Customers')

    result = db.session.execute(sql_query)
    
    # Fetch the results
    customers = result.fetchall()

    print(customers)

    # Render the template with the list of customers
    return render_template('customer_list.html', customers=customers)


# Page to add a new customer
@app.route('/add-customer', methods=['GET', 'POST'])
def add_customer_form():
    if request.method == 'POST':
        # Get form data
        CustomerID = request.form['CustomerID']
        FirstName = request.form['FirstName']
        LastName = request.form['LastName']
        Email = request.form['Email']
        Phone = request.form['Phone']

        # Create a new Customer instance
        new_customer = Customer(CustomerID=CustomerID, FirstName=FirstName, LastName=LastName, Email=Email, Phone=Phone)

        try:
            # Add the new customer to the database session
            db.session.add(new_customer)

            # Commit the changes to the database
            db.session.commit()

            print("Customer added to the database")

            # Redirect to the customer list after adding a new customer
            return redirect(url_for('custom_query'))

        except Exception as e:
            # Rollback in case of an error
            db.session.rollback()
            print(f"Error: {e}")

    return render_template('add_customer_form.html')

# Page to update the customer
@app.route('/update-customer/<int:CustomerID>', methods=['GET', 'POST'])
def update_customer(CustomerID):
    # Fetch the customer from the database using the provided customer_id
    customer = Customer.query.get(CustomerID)

    if request.method == 'POST':
        # Get updated form data
        customer.CustomerID = request.form['CustomerID']
        customer.FirstName = request.form['FirstName']
        customer.LastName = request.form['LastName']
        customer.Email = request.form['Email']
        customer.Phone = request.form['Phone']

        try:
            # Commit the changes to the database
            db.session.commit()

            print("Customer updated in the database")

            # Redirect to the customer list after updating the customer
            return redirect(url_for('custom_query'))

        except Exception as e:
            # Rollback in case of an error
            db.session.rollback()
            print(f"Error: {e}")

    return render_template('update_customer.html', customer=customer)

# Page to delete a customer
@app.route('/delete-customer/<int:CustomerID>', methods=['GET', 'POST'])
def delete_customer(CustomerID):
    # Fetch the customer from the database using the provided customer_id
    customer = Customer.query.get(CustomerID)

    if request.method == 'POST':
        try:
            # Delete the customer from the database session
            db.session.delete(customer)

            # Commit the changes to the database
            db.session.commit()

            print("Customer deleted from the database")

            # Redirect to the customer list after deleting the customer
            return redirect(url_for('custom_query'))

        except Exception as e:
            # Rollback in case of an error
            db.session.rollback()
            print(f"Error: {e}")

    return render_template('delete_customer.html', customer=customer)


# Page to list all the reservations
@app.route('/reservation-list')
def reservation_list():
    # Write your custom SQL query to fetch reservation details along with customer details
    sql_query = text('SELECT Reservations.*, Customers.FirstName, Customers.LastName, Customers.Email, Customers.Phone '
                     'FROM Reservations '
                     'JOIN Customers ON Reservations.CustomerID = Customers.CustomerID')

    result = db.session.execute(sql_query)

    # Fetch the results and convert each row to a dictionary
    rows = result.fetchall()
    column_names = result.keys()
    reservations = [dict(zip(column_names, row)) for row in rows]

    print(reservations)

    # Render the template with the list of reservations
    return render_template('reservations.html', reservations=reservations)


# Page to list all the feedback
@app.route('/feedback-list')
def feedback_list():
    # Write your custom SQL query to fetch feedback details along with customer details
    sql_query = text('SELECT Feedback.FeedbackId,Feedback.CustomerId,Feedback.FeedbackDate,Feedback.FeedbackText, Customers.FirstName, Customers.LastName, Customers.Email, Customers.Phone '
                     'FROM Feedback '
                     'JOIN Customers ON Feedback.CustomerId = Customers.CustomerID')

    result = db.session.execute(sql_query)

    # Fetch the results and convert each row to a dictionary
    rows = result.fetchall()
    column_names = result.keys()
    feedbacks = [dict(zip(column_names, row)) for row in rows]

    print(feedbacks)

    # Render the template with the list of feedback
    return render_template('feedback_list.html', feedbacks=feedbacks)

# Page to list all the menucatjoin
@app.route('/MenuCatView')
def MenuCat_View():
    # Write your custom SQL query to fetch feedback details along with customer details
    sql_query = text('SELECT * FROM RestaurantCo.MenuCat')

    result = db.session.execute(sql_query)

    # Fetch the results and convert each row to a dictionary
    rows = result.fetchall()
    column_names = result.keys()
    menucatjoin = [dict(zip(column_names, row)) for row in rows]

    print(menucatjoin)

    # Render the template with the list of feedback
    return render_template('menucatview.html', menucatjoin=menucatjoin)

@app.route('/Menu')
def Menu_View():
    # Write your custom SQL query to fetch feedback details along with customer details
    sql_query = text('SELECT * FROM RestaurantCo.Menu')

    result = db.session.execute(sql_query)

    # Fetch the results and convert each row to a dictionary
    rows = result.fetchall()
    column_names = result.keys()
    menus = [dict(zip(column_names, row)) for row in rows]

    print(menus)

    # Render the template with the list of feedback
    return render_template('menu.html', menus=menus)


if __name__ == '__main__':
    app.run(debug=True)
