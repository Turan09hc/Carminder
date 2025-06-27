from flask import Blueprint, request, render_template, redirect, url_for, flash
from app import mysql
from .models.oil_calculator import OilChangeEstimator
from datetime import date, datetime

main = Blueprint('main', __name__)

@main.route('/')
def home():
    """Landing page - redirect to registration"""
    return redirect(url_for('main.register'))

@main.route('/admin')
def admin_dashboard():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM cars ORDER BY created_at DESC")
    cars = cursor.fetchall()
    
    vehicles = []
    critical_count = 0
    good_count = 0
    
    for car in cars:
        # Calculate distance since last oil change
        distance_since_oil = car['mileage'] - car['last_oil_change_km']
        
        # Calculate months since last oil change
        today = date.today()
        last_change_date = car['last_oil_change_date']
        if isinstance(last_change_date, str):
            last_change_date = datetime.strptime(last_change_date, '%Y-%m-%d').date()
        
        months_since = (today.year - last_change_date.year) * 12 + (today.month - last_change_date.month)
        
        # Use OilChangeEstimator to calculate status
        try:
            gas_type = int(car['gas_type']) if str(car['gas_type']).isdigit() else 95
        except (ValueError, TypeError):
            gas_type = 95
            
        estimator = OilChangeEstimator(
            distance_km=distance_since_oil,
            gas_type=gas_type,
            months_since_last=months_since,
            oil_brand=car['oil_type'] or 'standard'
        )
        
        oil_status = estimator.calculate_oil_change_need()
        
        # Determine status based on oil calculator result
        if 'needed' in oil_status.lower() or 'now' in oil_status.lower():
            status = 'critical'
            critical_count += 1
        else:
            status = 'good'
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
            'months_since_oil': months_since,
            'last_oil_change_km': car['last_oil_change_km'],
            'last_oil_change_date': car['last_oil_change_date']
        })
    
    cursor.close()
    return render_template('admin_dashboard.html', 
                         vehicles=vehicles,
                         total_vehicles=len(vehicles),
                         critical_count=critical_count,
                         good_count=good_count)

@main.route('/register', methods=['GET', 'POST'])
def register():
    """Business registration for fleet managers"""
    if request.method == 'POST':
        try:
            # Get form data
            owner_name = request.form['owner_name'].strip()
            business_name = request.form['business_name'].strip()
            email = request.form['email'].strip()
            phone = request.form['phone'].strip()
            country = request.form['country']
            language = request.form['language']
            business_size = request.form['business_size']
            primary_interest = request.form['primary_interest']
            
            # Validate required fields
            if not all([owner_name, business_name, email, phone, country, language, business_size]):
                flash('All fields are required!', 'error')
                return render_template('register.html')
            
            flash(f'Welcome {owner_name}! Your fleet management account has been created.', 'success')
            flash('You can now start adding vehicles to your fleet.', 'success')
            
            # Redirect to dashboard
            return redirect(url_for('main.admin_dashboard'))
            
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@main.route('/login')
def login():
    """Login redirect to dashboard"""
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/add_vehicle', methods=['POST'])
def add_vehicle():
    try:
        # Get form data
        plate_number = request.form['plate_number'].upper().strip()
        car_model = request.form['car_model'].strip()
        owner_name = request.form['owner_name'].strip()
        owner_phone = request.form['owner_phone'].strip()
        mileage = int(request.form['mileage'])
        last_oil_change_km = int(request.form['last_oil_change_km'])
        gas_type = request.form['gas_type']
        oil_type = request.form.get('oil_type', 'standard')
        last_oil_change_date = request.form['last_oil_change_date']
        
        # Validate that last oil change is not greater than current mileage
        if last_oil_change_km > mileage:
            flash('Last oil change distance cannot be greater than current mileage!', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        cursor = mysql.connection.cursor()
        
        # Check if plate number already exists
        cursor.execute("SELECT id FROM cars WHERE plate_number = %s", (plate_number,))
        if cursor.fetchone():
            flash('Vehicle with this plate number already exists!', 'error')
            cursor.close()
            return redirect(url_for('main.admin_dashboard'))
        
        # Insert new vehicle with proper oil change data
        cursor.execute("""
            INSERT INTO cars (plate_number, car_model, owner, tel_no, mileage,
                            production_date, gas_type, oil_type, last_oil_change_km, last_oil_change_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (plate_number, car_model, owner_name, owner_phone, mileage,
              date.today(), gas_type, oil_type, last_oil_change_km, last_oil_change_date))
        
        mysql.connection.commit()
        cursor.close()
        
        # Calculate initial status for the new vehicle
        distance_since_oil = mileage - last_oil_change_km
        last_change_date = datetime.strptime(last_oil_change_date, '%Y-%m-%d').date()
        months_since = (date.today().year - last_change_date.year) * 12 + (date.today().month - last_change_date.month)
        
        try:
            gas_type_int = int(gas_type) if str(gas_type).isdigit() else 95
        except:
            gas_type_int = 95
            
        estimator = OilChangeEstimator(distance_since_oil, gas_type_int, months_since, oil_type)
        oil_status = estimator.calculate_oil_change_need()
        
        if 'needed' in oil_status.lower():
            flash(f'Vehicle {plate_number} added successfully! ⚠️ Oil change needed!', 'warning')
        else:
            flash(f'Vehicle {plate_number} added successfully! ✅ Oil status: Good', 'success')
        
    except ValueError as e:
        flash('Invalid input values. Please check your entries.', 'error')
    except Exception as e:
        flash(f'Error adding vehicle: {str(e)}', 'error')
    
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/service/<int:vehicle_id>', methods=['POST'])
def service_vehicle(vehicle_id):
    try:
        cursor = mysql.connection.cursor()
        
        # Get current vehicle data
        cursor.execute("SELECT plate_number, mileage FROM cars WHERE id = %s", (vehicle_id,))
        car = cursor.fetchone()
        
        if not car:
            flash('Vehicle not found!', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        # Update last oil change to current mileage and today's date
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
        
        flash(f'Service completed for vehicle {car["plate_number"]}! Oil change recorded.', 'success')
        
    except Exception as e:
        flash(f'Error updating service: {str(e)}', 'error')
    
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/delete/<int:vehicle_id>', methods=['POST'])
def delete_vehicle(vehicle_id):
    try:
        cursor = mysql.connection.cursor()
        
        # Get vehicle info for confirmation
        cursor.execute("SELECT plate_number FROM cars WHERE id = %s", (vehicle_id,))
        car = cursor.fetchone()
        
        if not car:
            flash('Vehicle not found!', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        # Delete maintenance history first (foreign key constraint)
        cursor.execute("DELETE FROM maintenance_history WHERE car_id = %s", (vehicle_id,))
        
        # Delete vehicle
        cursor.execute("DELETE FROM cars WHERE id = %s", (vehicle_id,))
        
        mysql.connection.commit()
        cursor.close()
        
        flash(f'Vehicle {car["plate_number"]} deleted successfully!', 'success')
        
    except Exception as e:
        flash(f'Error deleting vehicle: {str(e)}', 'error')
    
    return redirect(url_for('main.admin_dashboard'))