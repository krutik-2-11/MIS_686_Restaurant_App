from flask import Flask, render_template,request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text, inspect
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from textblob import TextBlob

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
    
class Orders(db.Model):
    OrderID = db.Column(db.Integer, primary_key=True)
    CustomerID = db.Column(db.Text, nullable=False)
    OrderDate = db.Column(db.Integer, nullable=False)
    TotalAmount=db.Column(db.Integer,nullable=False)

    __tablename__ = 'Orders'

    def __repr__(self):
        return f'<Menu {self.OrderID} - Price: {self.CustomerID}, Text: {self.OrderDate},Text:{self.TotalAmount}>'

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

    # Perform sentiment analysis on feedback texts and count positive, negative, and neutral comments
    positive_count = 0
    negative_count = 0
    neutral_count = 0

    # Add your sentiment analysis logic here using a library like TextBlob or NLTK
    for feedback in feedbacks:
        feedback_text = feedback['FeedbackText']
        analysis = TextBlob(feedback_text)

        # Classify the sentiment
        if analysis.sentiment.polarity > 0:
            positive_count += 1
        elif analysis.sentiment.polarity < 0:
            negative_count += 1
        else:
            neutral_count += 1


    # Avoid zero values in the sizes array
    sizes = [positive_count + 0.1, negative_count + 0.1, neutral_count + 0.1]

    # Generate a pie chart
    labels = ['Positive', 'Negative', 'Neutral']
    colors = ['#2ecc71', '#e74c3c', '#3498db']
    explode = (0.1, 0, 0)  # explode the 1st slice (Positive)

    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Save the pie chart to a BytesIO object
    chart_image = BytesIO()
    plt.savefig(chart_image, format='png')
    chart_image.seek(0)
    plt.close()

    # Convert BytesIO to base64-encoded string to embed in HTML
    chart_data = base64.b64encode(chart_image.getvalue()).decode('utf-8')

    # Render the template with the pie chart and list of feedback
    return render_template('feedback_list.html', feedbacks=feedbacks, chart_data=chart_data)

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

@app.route('/menu_category_view')
def menu_category_view():
    # Write your custom SQL query to fetch data for visualization
    sql_query = text('SELECT CategoryName,count(ItemName) as ItemCount FROM RestaurantCo.MenuCat group by CategoryName')

    result = db.session.execute(sql_query)

    # Fetch the results and convert each row to a dictionary
    rows = result.fetchall()
    column_names = result.keys()
    menucat_avg_prices = [dict(zip(column_names, row)) for row in rows]

    # Pass the prepared data to the template
    return render_template('mencatview.html', menucat_avg_prices=menucat_avg_prices)

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

@app.route('/sales')
def sales():
    # Write your custom SQL query to fetch data for visualization
    sql_query = text('SELECT sum(TotalAmount) as TA,Month(OrderDate) as OD FROM RestaurantCo.Orders group by OD')

    result = db.session.execute(sql_query)

    # Fetch the results and convert each row to a dictionary
    rows = result.fetchall()
    column_names = result.keys()
    orders = [dict(zip(column_names, row)) for row in rows]

    # Pass the prepared data to the template
    return render_template('sales.html',orders=orders)



# Page to visualize sales by item category
@app.route('/sales-by-item-category')
def sales_by_item_category():
    # Write your custom SQL query to fetch data for visualization
    sql_query = text('SELECT CategoryName, '
                     'COUNT(ItemName) AS ItemCount, '
                     'SUM(TotalAmount) AS TotalSales '
                     'FROM RestaurantCo.OrderMenuView '
                     'GROUP BY CategoryName')

    result = db.session.execute(sql_query)

    # Fetch the results and convert each row to a dictionary
    rows = result.fetchall()
    column_names = result.keys()
    sales_by_category = [dict(zip(column_names, row)) for row in rows]

    # Pass the prepared data to the template
    return render_template('sales_by_item_category.html', sales_by_category=sales_by_category)






if __name__ == '__main__':
    app.run(debug=True)
