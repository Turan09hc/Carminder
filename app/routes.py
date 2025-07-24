from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import mysql
from .models.oil_calculator import MaintenanceEstimator, TireChangeEstimator, OilChangeEstimator
from datetime import date, datetime, timedelta
import functools
import os

main = Blueprint('main', __name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'app/static/uploads/logos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        SELECT u.*, c.company_name, c.logo_filename 
        FROM users u 
        JOIN companies c ON u.company_id = c.id 
        WHERE u.id = %s AND u.is_active = TRUE
    """, (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    return user

def determine_vehicle_type(car_model_info):
    """Determine vehicle type from car model information"""
    if not car_model_info:
        return 'gasoline'
    
    fuel_type = car_model_info.get('fuel_type', 'gasoline').lower()
    return fuel_type

@main.route('/')
def home():
    """Landing page - redirect based on login status"""
    if 'user_id' in session:
        return redirect(url_for('main.admin_dashboard'))
    return redirect(url_for('main.register'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    """Company and admin user registration with logo upload"""
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
            
            # Handle logo upload
            logo_filename = None
            if 'logo' in request.files:
                file = request.files['logo']
                if file and file.filename and allowed_file(file.filename):
                    # Create upload directory if it doesn't exist
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    
                    # Generate secure filename
                    original_filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    logo_filename = f"{timestamp}_{original_filename}"
                    
                    # Save file
                    file_path = os.path.join(UPLOAD_FOLDER, logo_filename)
                    file.save(file_path)
            
            cursor = mysql.connection.cursor()
            
            # Check if email already exists
            cursor.execute("SELECT id FROM companies WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('A company with this email already exists!', 'error')
                cursor.close()
                return render_template('register.html')
            
            # Create company with logo
            cursor.execute("""
                INSERT INTO companies (company_name, owner_name, email, phone, country, language, 
                                     business_size, primary_interest, logo_filename)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (business_name, owner_name, email, phone, country, language, 
                  business_size, primary_interest, logo_filename))
            
            company_id = cursor.lastrowid
            
            # Create admin user
            username = email.split('@')[0]
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
            
            cursor.execute("""
                SELECT u.*, c.company_name, c.logo_filename 
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
                session['logo_filename'] = user['logo_filename']
                
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
    """Enhanced dashboard with electric car and tire tracking support"""
    cursor = mysql.connection.cursor()
    
    # Get vehicles with car model information
    cursor.execute("""
        SELECT c.*, cm.brand, cm.model as model_name, cm.engine_size, cm.fuel_type 
        FROM cars c 
        LEFT JOIN car_models cm ON c.car_model_id = cm.id 
        WHERE c.company_id = %s AND c.is_active = TRUE 
        ORDER BY c.created_at DESC
    """, (session['company_id'],))
    cars = cursor.fetchall()
    
    vehicles = []
    critical_count = 0
    good_count = 0
    tire_critical_count = 0
    
    for car in cars:
        # Determine vehicle type
        vehicle_type = determine_vehicle_type(car)
        
        # Calculate maintenance needs (oil/battery service)
        distance_since_service = car['mileage'] - car['last_oil_change_km']
        
        today = date.today()
        last_change_date = car['last_oil_change_date']
        if isinstance(last_change_date, str):
            last_change_date = datetime.strptime(last_change_date, '%Y-%m-%d').date()
        
        months_since = (today.year - last_change_date.year) * 12 + (today.month - last_change_date.month)
        
        # Determine fuel type for estimator
        if vehicle_type == 'electric':
            fuel_type = 'electric'
        elif vehicle_type == 'diesel':
            fuel_type = 'diesel'
        elif vehicle_type == 'hybrid':
            fuel_type = 'hybrid'
        else:
            try:
                fuel_type = int(car['gas_type']) if str(car['gas_type']).isdigit() else 95
            except (ValueError, TypeError):
                fuel_type = 95
        
        # Calculate maintenance status
        estimator = MaintenanceEstimator(
            distance_km=distance_since_service,
            fuel_type=fuel_type,
            months_since_last=months_since,
            oil_brand=car['oil_type'] or 'standard',
            vehicle_type=vehicle_type
        )
        
        maintenance_status = estimator.calculate_maintenance_need()
        
        # Calculate tire status
        tire_distance = car['mileage'] - (car['last_tire_change_km'] or 0)
        tire_last_change = car['last_tire_change_date']
        tire_months = 0
        
        if tire_last_change:
            if isinstance(tire_last_change, str):
                tire_last_change = datetime.strptime(tire_last_change, '%Y-%m-%d').date()
            tire_months = (today.year - tire_last_change.year) * 12 + (today.month - tire_last_change.month)
        else:
            tire_months = 48  # Assume old tires if no data
        
        tire_estimator = TireChangeEstimator(
            distance_km=tire_distance,
            months_since_last=tire_months,
            tire_brand=car['tire_brand'] or 'standard'
        )
        
        tire_status = tire_estimator.calculate_tire_change_need()
        
        # Determine overall status
        maintenance_critical = 'needed' in maintenance_status.lower() or 'now' in maintenance_status.lower()
        tire_critical = 'needed' in tire_status.lower() or 'now' in tire_status.lower()
        
        if maintenance_critical or tire_critical:
            status = 'critical'
            critical_count += 1
            if tire_critical:
                tire_critical_count += 1
        else:
            status = 'good'
            good_count += 1
        
        # Enhanced car model display
        if car['brand'] and car['model_name']:
            car_model_display = f"{car['brand']} {car['model_name']}"
            if car['engine_size'] and car['engine_size'] != '0.0L':
                car_model_display += f" ({car['engine_size']})"
            if vehicle_type == 'electric':
                car_model_display += " ⚡"
            elif vehicle_type == 'hybrid':
                car_model_display += " 🔋"
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
            'vehicle_type': vehicle_type,
            'status': status,
            'maintenance_status': maintenance_status,
            'tire_status': tire_status,
            'distance_since_service': distance_since_service,
            'months_since_service': months_since,
            'tire_distance': tire_distance,
            'tire_months': tire_months,
            'last_oil_change_km': car['last_oil_change_km'],
            'last_oil_change_date': car['last_oil_change_date'],
            'last_tire_change_km': car['last_tire_change_km'],
            'last_tire_change_date': car['last_tire_change_date']
        })
    
    cursor.close()
    return render_template('admin_dashboard.html', 
                         vehicles=vehicles,
                         total_vehicles=len(vehicles),
                         critical_count=critical_count,
                         good_count=good_count,
                         tire_critical_count=tire_critical_count,
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
            
            display_name = model['model']
            if model['engine_size'] and model['engine_size'] != '0.0L':
                display_name += f" ({model['engine_size']})"
            
            # Add fuel type indicator
            if model['fuel_type'] == 'electric':
                display_name += " ⚡"
            elif model['fuel_type'] == 'hybrid':
                display_name += " 🔋"
            elif model['fuel_type'] == 'diesel':
                display_name += " 🛢️"
            
            brands[brand].append({
                'id': model['id'],
                'model': model['model'],
                'engine_size': model['engine_size'],
                'fuel_type': model['fuel_type'],
                'display': display_name
            })
        
        return jsonify(brands)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/admin/add_vehicle', methods=['POST'])
@login_required
def add_vehicle():
    """Enhanced add vehicle with electric car and tire tracking support"""
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
        
        # Tire tracking fields
        last_tire_change_km = int(request.form.get('last_tire_change_km', 0))
        last_tire_change_date = request.form.get('last_tire_change_date')
        tire_brand = request.form.get('tire_brand', 'standard')
        
        # Validate car model selection
        if not car_model_id and not custom_model:
            flash('Please select a car model or enter a custom model!', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        car_model_id = int(car_model_id) if car_model_id else None
        
        # Validate distances
        if last_oil_change_km > mileage:
            flash('Last service distance cannot be greater than current mileage!', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        if last_tire_change_km > mileage:
            flash('Last tire change distance cannot be greater than current mileage!', 'error')
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
        
        # Get vehicle type for proper messaging
        vehicle_type = 'gasoline'
        if car_model_id:
            cursor.execute("SELECT fuel_type FROM car_models WHERE id = %s", (car_model_id,))
            model_info = cursor.fetchone()
            if model_info:
                vehicle_type = model_info['fuel_type']
        
        # Insert vehicle with tire tracking
        cursor.execute("""
            INSERT INTO cars (company_id, plate_number, car_model_id, custom_model, owner, tel_no, mileage,
                            production_date, gas_type, oil_type, last_oil_change_km, last_oil_change_date, 
                            last_tire_change_km, last_tire_change_date, tire_brand, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (session['company_id'], plate_number, car_model_id, custom_model, owner_name, owner_phone, mileage,
              date.today(), gas_type, oil_type, last_oil_change_km, last_oil_change_date, 
              last_tire_change_km, last_tire_change_date, tire_brand, session['user_id']))
        
        mysql.connection.commit()
        cursor.close()
        
        # Calculate status for success message
        distance_since_service = mileage - last_oil_change_km
        last_change_date = datetime.strptime(last_oil_change_date, '%Y-%m-%d').date()
        months_since = (date.today().year - last_change_date.year) * 12 + (date.today().month - last_change_date.month)
        
        # Determine fuel type for estimator
        if vehicle_type == 'electric':
            fuel_type = 'electric'
        elif vehicle_type == 'diesel':
            fuel_type = 'diesel'
        elif vehicle_type == 'hybrid':
            fuel_type = 'hybrid'
        else:
            try:
                fuel_type = int(gas_type) if str(gas_type).isdigit() else 95
            except:
                fuel_type = 95
        
        estimator = MaintenanceEstimator(
            distance_km=distance_since_service,
            fuel_type=fuel_type,
            months_since_last=months_since,
            oil_brand=oil_type,
            vehicle_type=vehicle_type
        )
        maintenance_status = estimator.calculate_maintenance_need()
        
        # Success message based on vehicle type
        service_type = "Battery/brake service" if vehicle_type == 'electric' else "Oil change"
        
        if 'needed' in maintenance_status.lower():
            flash(f'Vehicle {plate_number} added successfully! ⚠️ {service_type} needed!', 'warning')
        else:
            flash(f'Vehicle {plate_number} added successfully! ✅ Maintenance status: Good', 'success')
        
    except ValueError as e:
        flash('Invalid input values. Please check your entries.', 'error')
    except Exception as e:
        flash(f'Error adding vehicle: {str(e)}', 'error')
    
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/service/<int:vehicle_id>', methods=['POST'])
@login_required
def service_vehicle(vehicle_id):
    """Enhanced service with support for oil change and tire change"""
    try:
        service_type = request.form.get('service_type', 'oil_change')
        
        cursor = mysql.connection.cursor()
        
        # Get vehicle info with model details
        cursor.execute("""
            SELECT c.*, cm.fuel_type 
            FROM cars c 
            LEFT JOIN car_models cm ON c.car_model_id = cm.id 
            WHERE c.id = %s AND c.company_id = %s AND c.is_active = TRUE
        """, (vehicle_id, session['company_id']))
        car = cursor.fetchone()
        
        if not car:
            flash('Vehicle not found or access denied!', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        vehicle_type = determine_vehicle_type(car)
        
        if service_type == 'oil_change':
            # Update maintenance service
            cursor.execute("""
                UPDATE cars 
                SET last_oil_change_km = %s, last_oil_change_date = %s 
                WHERE id = %s AND company_id = %s
            """, (car['mileage'], date.today(), vehicle_id, session['company_id']))
            
            service_name = "Battery/brake service" if vehicle_type == 'electric' else "Oil change"
            maintenance_type = 'battery_service' if vehicle_type == 'electric' else 'oil_change'
            
        elif service_type == 'tire_change':
            # Update tire change
            cursor.execute("""
                UPDATE cars 
                SET last_tire_change_km = %s, last_tire_change_date = %s 
                WHERE id = %s AND company_id = %s
            """, (car['mileage'], date.today(), vehicle_id, session['company_id']))
            
            service_name = "Tire change"
            maintenance_type = 'tire_change'
        
        # Add to maintenance history
        cursor.execute("""
            INSERT INTO maintenance_history (car_id, company_id, maintenance_type, mileage_at_service, service_date, notes, performed_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (vehicle_id, session['company_id'], maintenance_type, car['mileage'], date.today(), 
              f'{service_name} completed by {session["full_name"]}', session['user_id']))
        
        mysql.connection.commit()
        cursor.close()
        
        flash(f'{service_name} completed for vehicle {car["plate_number"]}!', 'success')
        
    except Exception as e:
        flash(f'Error updating service: {str(e)}', 'error')
    
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/delete/<int:vehicle_id>', methods=['POST'])
@login_required
def delete_vehicle(vehicle_id):
    """Delete vehicle with company isolation"""
    try:
        cursor = mysql.connection.cursor()
        
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

@main.route('/admin/upload_logo', methods=['POST'])
@login_required
def upload_logo():
    """Upload company logo"""
    try:
        if 'logo' not in request.files:
            flash('No logo file selected!', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        file = request.files['logo']
        if file.filename == '':
            flash('No logo file selected!', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        if file and allowed_file(file.filename):
            # Create upload directory if it doesn't exist
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Generate secure filename
            original_filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            logo_filename = f"{timestamp}_{original_filename}"
            
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                flash('Logo file too large! Maximum size is 5MB.', 'error')
                return redirect(url_for('main.admin_dashboard'))
            
            # Save file
            file_path = os.path.join(UPLOAD_FOLDER, logo_filename)
            file.save(file_path)
            
            # Update database
            cursor = mysql.connection.cursor()
            cursor.execute("""
                UPDATE companies 
                SET logo_filename = %s 
                WHERE id = %s
            """, (logo_filename, session['company_id']))
            mysql.connection.commit()
            cursor.close()
            
            # Update session
            session['logo_filename'] = logo_filename
            
            flash('Company logo uploaded successfully!', 'success')
        else:
            flash('Invalid file type! Please upload PNG, JPG, JPEG, GIF, or SVG files only.', 'error')
        
    except Exception as e:
        flash(f'Error uploading logo: {str(e)}', 'error')
    
    return redirect(url_for('main.admin_dashboard'))