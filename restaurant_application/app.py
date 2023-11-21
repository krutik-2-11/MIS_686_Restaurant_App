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


# Define your routes
@app.route('/')
def index():
    return 'Hello, Flask with Flask-SQLAlchemy!'

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


if __name__ == '__main__':
    app.run(debug=True)
