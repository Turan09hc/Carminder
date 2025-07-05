from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import mysql
from .models.oil_calculator import OilChangeEstimator
from datetime import date, datetime, timedelta
import functools

main = Blueprint('main', __name__)

def login_required(f):
    """Decorator to require login for routes"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or 'company_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current user information"""
    if 'user_id' not in session:
        return None
    
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT u.*, c.company_name 
        FROM users u 
        JOIN companies c ON u.company_id = c.id 
        WHERE u.id = %s AND u.is_active = TRUE
    """, (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    return user

@main.route('/')
def home():
    """Landing page - redirect based on login status"""
    if 'user_id' in session:
        return redirect(url_for('main.admin_dashboard'))
    return redirect(url_for('main.register'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    """Company and admin user registration"""
    if request.method == 'POST':
        try:
            # Get form data
            owner_name = request.form['owner_name'].strip()
            business_name = request.form['business_name'].strip()
            email = request.form['email'].strip().lower()
            phone = request.form['phone'].strip()
            country = request.form['country']
            language = request.form['language']
            business_size = request.form['business_size']
            primary_interest = request.form['primary_interest']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            # Validate required fields
            if not all([owner_name, business_name, email, phone, country, language, business_size, password]):
                flash('All fields are required!', 'error')
                return render_template('register.html')
            
            # Validate password
            if len(password) < 6:
                flash('Password must be at least 6 characters long!', 'error')
                return render_template('register.html')
                
            if password != confirm_password:
                flash('Passwords do not match!', 'error')
                return render_template('register.html')
            
            cursor = mysql.connection.cursor()
            
            # Check if email already exists
            cursor.execute("SELECT id FROM companies WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('A company with this email already exists!', 'error')
                cursor.close()
                return render_template('register.html')
            
            # Create company
            cursor.execute("""
                INSERT INTO companies (company_name, owner_name, email, phone, country, language, business_size, primary_interest)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (business_name, owner_name, email, phone, country, language, business_size, primary_interest))
            
            company_id = cursor.lastrowid
            
            # Create admin user with compatible password hashing
            username = email.split('@')[0]  # Use email prefix as username
            password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            
            cursor.execute("""
                INSERT INTO users (company_id, username, email, password_hash, full_name, role)
                VALUES (%s, %s, %s, %s, %s, 'admin')
            """, (company_id, username, email, password_hash, owner_name))
            
            mysql.connection.commit()
            cursor.close()
            
            flash(f'Welcome {owner_name}! Your company account has been created successfully.', 'success')
            flash('Please log in with your credentials to continue.', 'info')
            
            return redirect(url_for('main.login'))
            
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        try:
            email_or_username = request.form['email_or_username'].strip().lower()
            password = request.form['password']
            
            if not email_or_username or not password:
                flash('Please enter both email/username and password.', 'error')
                return render_template('login.html')
            
            cursor = mysql.connection.cursor()
            
            # Check by email or username
            cursor.execute("""
                SELECT u.*, c.company_name 
                FROM users u 
                JOIN companies c ON u.company_id = c.id 
                WHERE (u.email = %s OR u.username = %s) AND u.is_active = TRUE AND c.is_active = TRUE
            """, (email_or_username, email_or_username))
            
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password_hash'], password):
                # Create session
                session['user_id'] = user['id']
                session['company_id'] = user['company_id']
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                session['company_name'] = user['company_name']
                session['role'] = user['role']
                
                # Update last login
                cursor.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user['id'],))
                mysql.connection.commit()
                
                flash(f'Welcome back, {user["full_name"]}!', 'success')
                cursor.close()
                return redirect(url_for('main.admin_dashboard'))
            else:
                flash('Invalid email/username or password.', 'error')
                cursor.close()
                
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'error')
    
    return render_template('login.html')

@main.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.login'))

@main.route('/admin')
@login_required
def admin_dashboard():
    """Your existing dashboard logic with company isolation"""
    cursor = mysql.connection.cursor()
    
    # Get vehicles for current company only (enhanced your existing query)
    cursor.execute("""
        SELECT c.*, cm.brand, cm.model as model_name, cm.engine_size 
        FROM cars c 
        LEFT JOIN car_models cm ON c.car_model_id = cm.id 
        WHERE c.company_id = %s AND c.is_active = TRUE 
        ORDER BY c.created_at DESC
    """, (session['company_id'],))
    cars = cursor.fetchall()
    
    vehicles = []
    critical_count = 0
    good_count = 0
    
    for car in cars:
        # Your existing oil calculation logic (unchanged)
        distance_since_oil = car['mileage'] - car['last_oil_change_km']
        
        today = date.today()
        last_change_date = car['last_oil_change_date']
        if isinstance(last_change_date, str):
            last_change_date = datetime.strptime(last_change_date, '%Y-%m-%d').date()
        
        months_since = (today.year - last_change_date.year) * 12 + (today.month - last_change_date.month)
        
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
        
        if 'needed' in oil_status.lower() or 'now' in oil_status.lower():
            status = 'critical'
            critical_count += 1
        else:
            status = 'good'
            good_count += 1
        
        # Enhanced car model display
        if car['brand'] and car['model_name']:
            car_model_display = f"{car['brand']} {car['model_name']}"
            if car['engine_size']:
                car_model_display += f" ({car['engine_size']})"
        else:
            car_model_display = car['custom_model'] or 'Unknown Model'
            
        vehicles.append({
            'id': car['id'],
            'plate_number': car['plate_number'],
            'car_model': car_model_display,
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
                         good_count=good_count,
                         user=get_current_user())

@main.route('/api/car_models')
@login_required
def get_car_models():
    """API endpoint to get car models for AJAX requests"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT id, brand, model, engine_size, fuel_type 
            FROM car_models 
            WHERE is_active = TRUE 
            ORDER BY brand, model, engine_size
        """)
        models = cursor.fetchall()
        cursor.close()
        
        # Group by brand for better organization
        brands = {}
        for model in models:
            brand = model['brand']
            if brand not in brands:
                brands[brand] = []
            brands[brand].append({
                'id': model['id'],
                'model': model['model'],
                'engine_size': model['engine_size'],
                'fuel_type': model['fuel_type'],
                'display': f"{model['model']} ({model['engine_size']})" if model['engine_size'] else model['model']
            })
        
        return jsonify(brands)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/admin/add_vehicle', methods=['POST'])
@login_required
def add_vehicle():
    """Enhanced add vehicle with car model selection"""
    try:
        # Get form data
        plate_number = request.form['plate_number'].upper().strip()
        car_model_id = request.form.get('car_model_id')
        custom_model = request.form.get('custom_model', '').strip()
        owner_name = request.form['owner_name'].strip()
        owner_phone = request.form['owner_phone'].strip()
        mileage = int(request.form['mileage'])
        last_oil_change_km = int(request.form['last_oil_change_km'])
        gas_type = request.form['gas_type']
        oil_type = request.form.get('oil_type', 'standard')
        last_oil_change_date = request.form['last_oil_change_date']
        
        # Validate car model selection
        if not car_model_id and not custom_model:
            flash('Please select a car model or enter a custom model!', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        car_model_id = int(car_model_id) if car_model_id else None
        
        # Your existing validation logic
        if last_oil_change_km > mileage:
            flash('Last oil change distance cannot be greater than current mileage!', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        cursor = mysql.connection.cursor()
        
        # Check if plate number already exists in this company
        cursor.execute("""
            SELECT id FROM cars 
            WHERE plate_number = %s AND company_id = %s AND is_active = TRUE
        """, (plate_number, session['company_id']))
        if cursor.fetchone():
            flash('Vehicle with this plate number already exists in your fleet!', 'error')
            cursor.close()
            return redirect(url_for('main.admin_dashboard'))
        
        # Enhanced insert with company isolation
        cursor.execute("""
            INSERT INTO cars (company_id, plate_number, car_model_id, custom_model, owner, tel_no, mileage,
                            production_date, gas_type, oil_type, last_oil_change_km, last_oil_change_date, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (session['company_id'], plate_number, car_model_id, custom_model, owner_name, owner_phone, mileage,
              date.today(), gas_type, oil_type, last_oil_change_km, last_oil_change_date, session['user_id']))
        
        mysql.connection.commit()
        cursor.close()
        
        # Your existing oil status calculation (unchanged)
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
@login_required
def service_vehicle(vehicle_id):
    """Your existing service logic with company isolation"""
    try:
        cursor = mysql.connection.cursor()
        
        # Enhanced to ensure vehicle belongs to current company
        cursor.execute("""
            SELECT plate_number, mileage FROM cars 
            WHERE id = %s AND company_id = %s AND is_active = TRUE
        """, (vehicle_id, session['company_id']))
        car = cursor.fetchone()
        
        if not car:
            flash('Vehicle not found or access denied!', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        # Your existing service logic
        cursor.execute("""
            UPDATE cars 
            SET last_oil_change_km = %s, last_oil_change_date = %s 
            WHERE id = %s AND company_id = %s
        """, (car['mileage'], date.today(), vehicle_id, session['company_id']))
        
        # Enhanced maintenance history with company isolation
        cursor.execute("""
            INSERT INTO maintenance_history (car_id, company_id, maintenance_type, mileage_at_service, service_date, notes, performed_by)
            VALUES (%s, %s, 'oil_change', %s, %s, %s, %s)
        """, (vehicle_id, session['company_id'], car['mileage'], date.today(), 
              f'Oil change completed by {session["full_name"]}', session['user_id']))
        
        mysql.connection.commit()
        cursor.close()
        
        flash(f'Service completed for vehicle {car["plate_number"]}! Oil change recorded.', 'success')
        
    except Exception as e:
        flash(f'Error updating service: {str(e)}', 'error')
    
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/delete/<int:vehicle_id>', methods=['POST'])
@login_required
def delete_vehicle(vehicle_id):
    """Your existing delete logic with company isolation"""
    try:
        cursor = mysql.connection.cursor()
        
        # Enhanced to ensure vehicle belongs to current company
        cursor.execute("""
            SELECT plate_number FROM cars 
            WHERE id = %s AND company_id = %s AND is_active = TRUE
        """, (vehicle_id, session['company_id']))
        car = cursor.fetchone()
        
        if not car:
            flash('Vehicle not found or access denied!', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        # Soft delete - mark as inactive
        cursor.execute("""
            UPDATE cars SET is_active = FALSE 
            WHERE id = %s AND company_id = %s
        """, (vehicle_id, session['company_id']))
        
        mysql.connection.commit()
        cursor.close()
        
        flash(f'Vehicle {car["plate_number"]} removed from fleet successfully!', 'success')
        
    except Exception as e:
        flash(f'Error removing vehicle: {str(e)}', 'error')
    
    return redirect(url_for('main.admin_dashboard'))