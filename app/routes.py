from flask import Blueprint, request, render_template, redirect, url_for, session, flash, jsonify
from app import mysql
from .models.oilcalc import OilChangeEstimator
from datetime import datetime, date
import json

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/admin')
def admin_dashboard():
    """Admin dashboard with all fleet management features"""
    cursor = mysql.connection.cursor()
    
    # Get all vehicles with calculated status
    cursor.execute("""
        SELECT id, plate_number, car_model, owner, tel_no, mileage, 
               production_date, gas_type, oil_type, last_oil_change_km, 
               last_oil_change_date
        FROM cars 
        ORDER BY created_at DESC
    """)
    cars = cursor.fetchall()
    
    vehicles = []
    critical_count = 0
    good_count = 0
    
    for car in cars:
        # Calculate oil change status
        distance_since_oil = car['mileage'] - car['last_oil_change_km']
        
        # Calculate months since last oil change
        today = date.today()
        last_change_date = car['last_oil_change_date']
        if isinstance(last_change_date, str):
            last_change_date = datetime.strptime(last_change_date, '%Y-%m-%d').date()
        
        months_since = (today.year - last_change_date.year) * 12 + (today.month - last_change_date.month)
        
        # Use oil calculator
        estimator = OilChangeEstimator(
            distance_km=distance_since_oil,
            gas_type=int(car['gas_type']) if str(car['gas_type']).isdigit() else 95,
            months_since_last=months_since,
            oil_brand=car['oil_type']
        )
        
        oil_status = estimator.calculate_oil_change_need()
        status = 'critical' if 'needed' in oil_status.lower() else 'good'
        
        if status == 'critical':
            critical_count += 1
        else:
            good_count += 1
        
        vehicles.append({
            'id': car['id'],
            'plate_number': car['plate_number'],
            'car_model': car['car_model'],
            'owner_name': car['owner'],
            'owner_phone': car['tel_no'],
            'mileage': car['mileage'],
            'gas_type': car['gas_type'],
            'oil_type': car['oil_type'],
            'status': status,
            'oil_status': oil_status,
            'distance_since_oil': distance_since_oil,
            'months_since_oil': months_since
        })
    
    cursor.close()
    
    return render_template('admin_dashboard.html', 
                         vehicles=vehicles,
                         total_vehicles=len(vehicles),
                         critical_count=critical_count,
                         good_count=good_count)

@main.route('/admin/add_vehicle', methods=['POST'])
def admin_add_vehicle():
    """Add vehicle from admin dashboard"""
    try:
        plate_number = request.form['plate_number'].upper().strip()
        car_model = request.form['car_model'].strip()
        owner_name = request.form['owner_name'].strip()
        owner_phone = request.form['owner_phone'].strip()
        mileage = int(request.form['mileage'])
        gas_type = request.form['gas_type']
        oil_type = request.form.get('oil_type', 'generic')
        
        cursor = mysql.connection.cursor()
        
        # Check if plate already exists
        cursor.execute("SELECT id FROM cars WHERE plate_number = %s", (plate_number,))
        if cursor.fetchone():
            flash('Vehicle with this plate number already exists!', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        # Insert new vehicle
        cursor.execute("""
            INSERT INTO cars (plate_number, car_model, owner, tel_no, mileage,
                            production_date, gas_type, oil_type, last_oil_change_km, last_oil_change_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (plate_number, car_model, owner_name, owner_phone, mileage,
              date.today(), gas_type, oil_type, mileage, date.today()))
        
        mysql.connection.commit()
        cursor.close()
        
        flash('Vehicle added successfully!', 'success')
        
    except Exception as e:
        flash(f'Error adding vehicle: {str(e)}', 'error')
    
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/vehicle/<int:vehicle_id>')
def admin_view_vehicle(vehicle_id):
    """View individual vehicle details"""
    cursor = mysql.connection.cursor()
    
    # Get vehicle details
    cursor.execute("""
        SELECT * FROM cars WHERE id = %s
    """, (vehicle_id,))
    car = cursor.fetchone()
    
    if not car:
        flash('Vehicle not found!', 'error')
        return redirect(url_for('main.admin_dashboard'))
    
    # Get maintenance history
    cursor.execute("""
        SELECT * FROM maintenance_history 
        WHERE car_id = %s 
        ORDER BY service_date DESC
    """, (vehicle_id,))
    maintenance_history = cursor.fetchall()
    
    cursor.close()
    
    # Calculate current oil status
    distance_since_oil = car['mileage'] - car['last_oil_change_km']
    today = date.today()
    last_change_date = car['last_oil_change_date']
    if isinstance(last_change_date, str):
        last_change_date = datetime.strptime(last_change_date, '%Y-%m-%d').date()
    
    months_since = (today.year - last_change_date.year) * 12 + (today.month - last_change_date.month)
    
    estimator = OilChangeEstimator(
        distance_km=distance_since_oil,
        gas_type=int(car['gas_type']) if str(car['gas_type']).isdigit() else 95,
        months_since_last=months_since,
        oil_brand=car['oil_type']
    )
    
    oil_status = estimator.calculate_oil_change_need()
    
    return render_template('vehicle_detail.html', 
                         car=car,
                         oil_status=oil_status,
                         maintenance_history=maintenance_history)

@main.route('/admin/service/<int:vehicle_id>', methods=['POST'])
def admin_service_vehicle(vehicle_id):
    """Mark vehicle as serviced"""
    try:
        cursor = mysql.connection.cursor()
        
        # Get current vehicle data
        cursor.execute("SELECT mileage FROM cars WHERE id = %s", (vehicle_id,))
        car = cursor.fetchone()
        
        if not car:
            flash('Vehicle not found!', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        # Update last oil change
        cursor.execute("""
            UPDATE cars 
            SET last_oil_change_km = %s, last_oil_change_date = %s 
            WHERE id = %s
        """, (car['mileage'], date.today(), vehicle_id))
        
        # Add to maintenance history
        cursor.execute("""
            INSERT INTO maintenance_history (car_id, maintenance_type, mileage_at_service, service_date, notes)
            VALUES (%s, 'oil_change', %s, %s, %s)
        """, (vehicle_id, car['mileage'], date.today(), 'Oil change completed via admin dashboard'))
        
        mysql.connection.commit()
        cursor.close()
        
        flash('Vehicle service completed successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating service: {str(e)}', 'error')
    
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/delete/<int:vehicle_id>', methods=['POST'])
def admin_delete_vehicle(vehicle_id):
    """Delete vehicle from admin dashboard"""
    try:
        cursor = mysql.connection.cursor()
        
        # Delete maintenance history first (foreign key constraint)
        cursor.execute("DELETE FROM maintenance_history WHERE car_id = %s", (vehicle_id,))
        
        # Delete vehicle
        cursor.execute("DELETE FROM cars WHERE id = %s", (vehicle_id,))
        
        mysql.connection.commit()
        cursor.close()
        
        flash('Vehicle deleted successfully!', 'success')
        
    except Exception as e:
        flash(f'Error deleting vehicle: {str(e)}', 'error')
    
    return redirect(url_for('main.admin_dashboard'))

@main.route('/api/oil_calculator', methods=['POST'])
def api_oil_calculator():
    """API endpoint for oil calculator"""
    try:
        data = request.get_json()
        
        distance = int(data.get('distance', 0))
        gas_type = int(data.get('gas_type', 95))
        months = int(data.get('months', 0))
        oil_brand = data.get('oil_brand', 'generic')
        
        estimator = OilChangeEstimator(distance, gas_type, months, oil_brand)
        result = estimator.calculate_oil_change_need()
        
        return jsonify({
            'success': True,
            'result': result,
            'details': estimator.get_calculation_details()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# Original user routes (keep these for user interface)
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        plate_number = request.form['plate_number'].upper()
        car_model = request.form['car_model']
        owner = request.form['owner']
        tel_no = request.form['tel_no']
        mileage = int(request.form['mileage'])
        production_date = request.form['production_date']
        gas_type = request.form['gas_type']
        oil_type = request.form['oil_type']
        
        cursor = mysql.connection.cursor()
        
        cursor.execute("SELECT * FROM cars WHERE plate_number = %s", (plate_number,))
        if cursor.fetchone():
            flash('Car with this plate number already exists!', 'error')
            return render_template('register.html')
        
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
    
    distance_since_oil = car['mileage'] - car['last_oil_change_km']
    
    today = date.today()
    last_change_date = car['last_oil_change_date']
    months_since = (today.year - last_change_date.year) * 12 + (today.month - last_change_date.month)
    
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
    
    cursor.execute("SELECT mileage FROM cars WHERE id = %s", (session['car_id'],))
    car = cursor.fetchone()
    
    cursor.execute("""
        UPDATE cars SET last_oil_change_km = %s, last_oil_change_date = %s 
        WHERE id = %s
    """, (car['mileage'], date.today(), session['car_id']))
    
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