from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from app import mysql
from .models.oilcalc import OilChangeEstimator
from datetime import datetime, date

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        plate_number = request.form['plate_number'].upper()
        car_model = request.form['car_model']
        owner = request.form['owner']
        tel_no = request.form['tel_no']
        mileage = int(request.form['mileage'])
        production_date = request.form['production_date']
        gas_type = request.form['gas_type']
        oil_type = request.form['oil_type']
        
        cursor = mysql.connection.cursor()
        
        # Check if plate already exists
        cursor.execute("SELECT * FROM cars WHERE plate_number = %s", (plate_number,))
        if cursor.fetchone():
            flash('Car with this plate number already exists!', 'error')
            return render_template('register.html')
        
        # Insert new car
        cursor.execute("""
            INSERT INTO cars (plate_number, car_model, owner, tel_no, mileage, 
                            production_date, gas_type, oil_type, last_oil_change_km)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (plate_number, car_model, owner, tel_no, mileage, production_date, gas_type, oil_type, mileage))
        
        mysql.connection.commit()
        cursor.close()
        
        flash('Car registered successfully!', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        plate_number = request.form['plate_number'].upper()
        owner = request.form['owner']
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM cars WHERE plate_number = %s AND owner = %s", (plate_number, owner))
        car = cursor.fetchone()
        cursor.close()
        
        if car:
            session['loggedin'] = True
            session['car_id'] = car['id']
            session['plate_number'] = car['plate_number']
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid plate number or owner name!', 'error')
    
    return render_template('login.html')

@main.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('main.login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM cars WHERE id = %s", (session['car_id'],))
    car = cursor.fetchone()
    cursor.close()
    
    if not car:
        return redirect(url_for('main.login'))
    
    # Calculate oil change status using your OilChangeEstimator
    distance_since_oil = car['mileage'] - car['last_oil_change_km']
    
    # Calculate months since last oil change
    today = date.today()
    last_change_date = car['last_oil_change_date']
    months_since = (today.year - last_change_date.year) * 12 + (today.month - last_change_date.month)
    
    # Use your oil calculator
    estimator = OilChangeEstimator(
        distance_km=distance_since_oil,
        gas_type=int(car['gas_type']) if car['gas_type'].isdigit() else 95,
        months_since_last=months_since,
        oil_brand=car['oil_type']
    )
    
    oil_status = estimator.calculate_oil_change_need()
    
    return render_template('dashboard.html', car=car, oil_status=oil_status)

@main.route('/update_mileage', methods=['POST'])
def update_mileage():
    if 'loggedin' not in session:
        return redirect(url_for('main.login'))
    
    new_mileage = int(request.form['new_mileage'])
    
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE cars SET mileage = %s WHERE id = %s", (new_mileage, session['car_id']))
    mysql.connection.commit()
    cursor.close()
    
    flash('Mileage updated successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/oil_change_done', methods=['POST'])
def oil_change_done():
    if 'loggedin' not in session:
        return redirect(url_for('main.login'))
    
    cursor = mysql.connection.cursor()
    
    # Get current car data
    cursor.execute("SELECT mileage FROM cars WHERE id = %s", (session['car_id'],))
    car = cursor.fetchone()
    
    # Update last oil change
    cursor.execute("""
        UPDATE cars SET last_oil_change_km = %s, last_oil_change_date = %s 
        WHERE id = %s
    """, (car['mileage'], date.today(), session['car_id']))
    
    # Add to maintenance history
    cursor.execute("""
        INSERT INTO maintenance_history (car_id, maintenance_type, mileage_at_service, service_date)
        VALUES (%s, 'oil_change', %s, %s)
    """, (session['car_id'], car['mileage'], date.today()))
    
    mysql.connection.commit()
    cursor.close()
    
    flash('Oil change marked as complete!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))

# Your original estimate route for testing
@main.route('/estimate')
def estimate():
    try:
        distance = int(request.args.get('distance'))
        gas = int(request.args.get('gas'))
        months = int(request.args.get('months'))
        oil = request.args.get('oil')

        estimator = OilChangeEstimator(distance, gas, months, oil)
        result = estimator.calculate_oil_change_need()
        return result

    except Exception as e:
        return f"Error: {e}"