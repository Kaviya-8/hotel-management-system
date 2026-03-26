from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import random
import datetime

# Function to generate Booking ID
def generate_booking_id():
    today = datetime.datetime.now().strftime("%Y%m%d")  # Format: YYYYMMDD
    unique_number = random.randint(1000, 9999)  # Random 4-digit number
    return f"B{today}-{unique_number}"  # Booking ID format: BYYYYMMDD-xxxx

app = Flask(__name__)

# MySQL Database Configuration (using flask-mysqldb)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'               # Replace with your MySQL username
app.config['MYSQL_PASSWORD'] = 'Kiruthika0104!' # Replace with your MySQL password
app.config['MYSQL_DB'] = 'hotel_management'     # Replace with your database name

# Initialize MySQL
mysql = MySQL(app)

# Homepage Route
@app.route('/')
def homepage():
    return render_template('index.html')

# View Available Rooms Route
@app.route('/available')
def available_rooms():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM rooms WHERE available = TRUE")
    rooms = cursor.fetchall()
    cursor.close()

    return render_template('available.html', rooms=rooms)

# Book Room Route
@app.route('/book', methods=['GET', 'POST'])
def book_room():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        room_id = request.form.get('room_id')
        check_in = request.form.get('check_in')
        check_out = request.form.get('check_out')

        # Debugging: Print received data
        print(f"Form Data: Name={name}, Email={email}, Phone={phone}, Room ID={room_id}, Check-in={check_in}, Check-out={check_out}")

        try:
            cursor = mysql.connection.cursor()
            
            # Check if the room is available
            cursor.execute("SELECT available FROM rooms WHERE room_id = %s", (room_id,))
            room_status = cursor.fetchone()
            
            if not room_status or room_status[0] == 0:
                cursor.close()
                return "Error: Selected room is not available."

            # Insert booking into the bookings table
            query = """INSERT INTO bookings (customer_name, email, phone, room_id, check_in, check_out, status) 
                       VALUES (%s, %s, %s, %s, %s, %s, 'active')"""
            cursor.execute(query, (name, email, phone, room_id, check_in, check_out))
            mysql.connection.commit()

            # Fetch the last inserted booking ID
            booking_id = cursor.lastrowid

            # Mark the room as unavailable
            cursor.execute("UPDATE rooms SET available = FALSE WHERE room_id = %s", (room_id,))
            mysql.connection.commit()
            cursor.close()

            # Render the confirmation page with the correct booking ID
            return render_template('confirmation.html', name=name, email=email, booking_id=booking_id)
        
        except Exception as e:
            print(f"Error inserting booking data: {e}")
            return f"Error processing booking: {e}"

    # For GET request, display available rooms
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT room_id, room_type, price FROM rooms WHERE available = TRUE")
    rooms = cursor.fetchall()
    cursor.close()

    return render_template('book.html', rooms=rooms)


@app.route('/cancel', methods=['GET', 'POST'])
def cancel_booking():
    if request.method == 'POST':
        # Get the booking ID and reason from user input
        booking_id = request.form.get('booking_id')
        reason = request.form.get('reason')

        try:
            cursor = mysql.connection.cursor()

            # Retrieve the room_id for the booking being canceled
            cursor.execute("SELECT room_id FROM bookings WHERE booking_id = %s", (booking_id,))
            room_id = cursor.fetchone()

            if not room_id:
                cursor.close()
                return "Error: Booking ID not found."

            # Update the room status to available again
            cursor.execute("UPDATE rooms SET available = TRUE WHERE room_id = %s", (room_id[0],))
            mysql.connection.commit()

            # Delete the booking from the bookings table
            cursor.execute("DELETE FROM bookings WHERE booking_id = %s", (booking_id,))
            mysql.connection.commit()

            cursor.close()

            # Render success page
            return render_template('cancel_success.html', booking_id=booking_id, reason=reason)
        
        except Exception as e:
            print(f"Error processing cancellation: {e}")
            return f"Error processing cancellation: {e}"

    # Render cancellation form for GET requests
    return render_template('cancel.html')


# Feedback Route
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        customer_name = request.form['name']
        message = request.form['message']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO feedback (customer_name, message) VALUES (%s, %s)", 
                       (customer_name, message))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('homepage'))
    return render_template('feedback.html')

# Payment Page Route
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        booking_id = request.form['booking_id']
        amount = request.form['amount']
        card_number = request.form['card_number']
        expiry_date = request.form['expiry_date']
        cvv = request.form['cvv']

        # Logic to store or validate payment (this is just for demonstration)
        print(f"Payment received: {name}, {email}, Booking ID: {booking_id}, Amount: {amount}")

        return redirect(url_for('homepage'))
    return render_template('payment.html')

if __name__ == '__main__':
    app.run(debug=True)
