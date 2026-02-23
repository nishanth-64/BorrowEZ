from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os
import urllib.parse
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# MongoDB Atlas connection
MONGO_URI = "mongodb+srv://Nishanth:Nishi@cluster0.inph6za.mongodb.net/borrowez?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client.borrowez

# Collections
users_collection = db.users
items_collection = db.items
borrow_history_collection = db.borrow_history

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 10 * 1024  # 10KB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_google_maps_link(location):
    """Generate Google Maps search link using urllib for encoding"""
    if not location:
        return ""
    encoded_location = urllib.parse.quote_plus(location)
    return f"https://www.google.com/maps/search/?api=1&query={encoded_location}"

def generate_directions_link(from_location, to_location):
    """Generate Google Maps directions link between two locations"""
    if not from_location or not to_location:
        return ""
    encoded_from = urllib.parse.quote_plus(from_location)
    encoded_to = urllib.parse.quote_plus(to_location)
    return f"https://www.google.com/maps/dir/?api=1&origin={encoded_from}&destination={encoded_to}"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Public landing dashboard"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([name, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if users_collection.find_one({'email': email}):
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        hashed_password = generate_password_hash(password)
        user = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'created_at': datetime.utcnow()
        }
        
        result = users_collection.insert_one(user)
        session['user_id'] = str(result.inserted_id)
        session['user_name'] = name
        
        flash('Registration successful!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('login.html')
        
        user = users_collection.find_one({'email': email})
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['name']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard after login"""
    # Get all items for borrowing
    items = list(items_collection.find().sort('created_at', -1))
    
    # Convert ObjectId to string for template
    for item in items:
        item['_id'] = str(item['_id'])
        item['owner_id'] = str(item['owner_id'])
    
    return render_template('dashboard.html', items=items)

@app.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    """Add new item for lending"""
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        category = request.form.get('category')
        rent_amount = request.form.get('rent_amount')
        location = request.form.get('location')
        phone = request.form.get('phone')
        status = request.form.get('status', 'available')
        image = request.files.get('image')
        
        # Validation
        if not all([item_name, category, rent_amount, location, phone, status]):
            flash('All fields are required', 'error')
            return render_template('add_item.html')
        
        try:
            rent_amount = float(rent_amount)
            if rent_amount <= 0:
                flash('Rent amount must be positive', 'error')
                return render_template('add_item.html')
        except ValueError:
            flash('Invalid rent amount', 'error')
            return render_template('add_item.html')
        
        # Handle image upload
        image_path = ""
        if image and image.filename != '':
            if not allowed_file(image.filename):
                flash('Invalid file type. Allowed types: png, jpg, jpeg, gif', 'error')
                return render_template('add_item.html')
            
            # Check file size (10KB limit)
            image.seek(0, os.SEEK_END)
            file_size = image.tell()
            image.seek(0, os.SEEK_SET)
            
            if file_size > MAX_FILE_SIZE:
                flash('File size must be less than 10KB', 'error')
                return render_template('add_item.html')
            
            filename = secure_filename(image.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)
            image_path = filename
        
        # Generate Google Maps link
        google_maps_link = generate_google_maps_link(location)
        
        # Create item
        item = {
            'owner_id': ObjectId(session['user_id']),
            'owner_name': session['user_name'],
            'item_name': item_name,
            'category': category,
            'rent_per_hour': rent_amount,
            'location_name': location,
            'phone': phone,
            'status': status,
            'google_maps_link': google_maps_link,
            'image_path': image_path,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        items_collection.insert_one(item)
        flash('Item added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_item.html')

@app.route('/update_item/<item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    """Update existing item"""
    try:
        item = items_collection.find_one({'_id': ObjectId(item_id)})
        if not item:
            flash('Item not found', 'error')
            return redirect(url_for('dashboard'))
        
        # Check if current user is the owner
        if str(item['owner_id']) != session['user_id']:
            flash('You can only update your own items', 'error')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            item_name = request.form.get('item_name')
            category = request.form.get('category')
            rent_amount = request.form.get('rent_amount')
            location = request.form.get('location')
            phone = request.form.get('phone')
            status = request.form.get('status')
            image = request.files.get('image')
            
            # Validation
            if not all([item_name, category, rent_amount, location, phone, status]):
                flash('All fields are required', 'error')
                return render_template('update_item.html', item=item)
            
            try:
                rent_amount = float(rent_amount)
                if rent_amount <= 0:
                    flash('Rent amount must be positive', 'error')
                    return render_template('update_item.html', item=item)
            except ValueError:
                flash('Invalid rent amount', 'error')
                return render_template('update_item.html', item=item)
            
            # Handle image upload
            image_path = item.get('image_path', '')
            if image and image.filename != '':
                if not allowed_file(image.filename):
                    flash('Invalid file type. Allowed types: png, jpg, jpeg, gif', 'error')
                    return render_template('update_item.html', item=item)
                
                # Check file size (10KB limit)
                image.seek(0, os.SEEK_END)
                file_size = image.tell()
                image.seek(0, os.SEEK_SET)
                
                if file_size > MAX_FILE_SIZE:
                    flash('File size must be less than 10KB', 'error')
                    return render_template('update_item.html', item=item)
                
                # Delete old image if exists
                if item.get('image_path'):
                    old_image = os.path.join(app.config['UPLOAD_FOLDER'], item['image_path'])
                    if os.path.exists(old_image):
                        os.remove(old_image)
                
                filename = secure_filename(image.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                image_path = os.path.join(UPLOAD_FOLDER, filename)
                image.save(image_path)
                image_path = filename
            
            # Generate Google Maps link
            google_maps_link = generate_google_maps_link(location)
            
            # Update item
            items_collection.update_one(
                {'_id': ObjectId(item_id)},
                {'$set': {
                    'item_name': item_name,
                    'category': category,
                    'rent_per_hour': rent_amount,
                    'location_name': location,
                    'phone': phone,
                    'status': status,
                    'google_maps_link': google_maps_link,
                    'image_path': image_path,
                    'updated_at': datetime.utcnow()
                }}
            )
            
            flash('Item updated successfully!', 'success')
            return redirect(url_for('dashboard'))
        
        # Convert ObjectId to string for template
        item['_id'] = str(item['_id'])
        item['owner_id'] = str(item['owner_id'])
        
        return render_template('update_item.html', item=item)
    except:
        flash('Error loading item', 'error')
        return redirect(url_for('dashboard'))

@app.route('/delete_item/<item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    """Delete an item"""
    try:
        item = items_collection.find_one({'_id': ObjectId(item_id)})
        if not item:
            flash('Item not found', 'error')
            return redirect(url_for('dashboard'))
        
        # Check if the current user is the owner
        if str(item['owner_id']) != session['user_id']:
            flash('You can only delete your own items', 'error')
            return redirect(url_for('dashboard'))
        
        # Delete the item
        items_collection.delete_one({'_id': ObjectId(item_id)})
        
        # Delete associated image if exists
        if item.get('image_path'):
            image_file = os.path.join(app.config['UPLOAD_FOLDER'], item['image_path'])
            if os.path.exists(image_file):
                os.remove(image_file)
        
        flash('Item deleted successfully!', 'success')
        return redirect(url_for('dashboard'))
    except:
        flash('Error deleting item', 'error')
        return redirect(url_for('dashboard'))

@app.route('/borrow_item/<item_id>')
@login_required
def borrow_item(item_id):
    """View item details and get directions"""
    try:
        item = items_collection.find_one({'_id': ObjectId(item_id)})
        if not item:
            flash('Item not found', 'error')
            return redirect(url_for('dashboard'))
        
        item['_id'] = str(item['_id'])
        item['owner_id'] = str(item['owner_id'])
        
        return render_template('borrow_item.html', item=item)
    except:
        flash('Invalid item ID', 'error')
        return redirect(url_for('dashboard'))

@app.route('/get_directions/<item_id>', methods=['POST'])
@login_required
def get_directions(item_id):
    """Generate directions from borrower to lender location"""
    try:
        item = items_collection.find_one({'_id': ObjectId(item_id)})
        if not item:
            flash('Item not found', 'error')
            return redirect(url_for('dashboard'))
        
        borrower_location = request.form.get('borrower_location')
        lender_location = item['location_name']
        
        if not borrower_location:
            flash('Please enter your location', 'error')
            return render_template('borrow_item.html', item=item)
        
        directions_link = generate_directions_link(borrower_location, lender_location)
        
        # Add to borrow history
        borrow_record = {
            'borrower_id': ObjectId(session['user_id']),
            'borrower_name': session['user_name'],
            'item_id': ObjectId(item_id),
            'item_name': item['item_name'],
            'owner_id': item['owner_id'],
            'owner_name': item['owner_name'],
            'owner_phone': item['phone'],
            'borrower_location': borrower_location,
            'lender_location': lender_location,
            'rent_per_hour': item['rent_per_hour'],
            'directions_link': directions_link,
            'borrow_date': datetime.utcnow(),
            'status': 'requested'
        }
        
        borrow_history_collection.insert_one(borrow_record)
        flash('Borrow request recorded! Contact the lender to arrange pickup.', 'success')
        
        return render_template('directions.html', 
                             directions_link=directions_link,
                             borrower_location=borrower_location,
                             lender_location=lender_location,
                             item=item)
    except:
        flash('Error generating directions', 'error')
        return redirect(url_for('dashboard'))

@app.route('/history')
@login_required
def history():
    """View user's borrowing and lending history"""
    try:
        # Get user's posted items
        my_items = list(items_collection.find({'owner_id': ObjectId(session['user_id'])}).sort('created_at', -1))
        
        # Get user's borrow history
        borrow_history = list(borrow_history_collection.find({'borrower_id': ObjectId(session['user_id'])}).sort('borrow_date', -1))
        
        # Get lending history (items others borrowed from user)
        lending_history = list(borrow_history_collection.find({'owner_id': ObjectId(session['user_id'])}).sort('borrow_date', -1))
        
        # Convert ObjectId to string for templates
        for item in my_items:
            item['_id'] = str(item['_id'])
            item['owner_id'] = str(item['owner_id'])
        
        for record in borrow_history:
            record['_id'] = str(record['_id'])
            record['borrower_id'] = str(record['borrower_id'])
            record['item_id'] = str(record['item_id'])
            record['owner_id'] = str(record['owner_id'])
        
        for record in lending_history:
            record['_id'] = str(record['_id'])
            record['borrower_id'] = str(record['borrower_id'])
            record['item_id'] = str(record['item_id'])
            record['owner_id'] = str(record['owner_id'])
        
        return render_template('history.html', 
                           my_items=my_items, 
                           borrow_history=borrow_history,
                           lending_history=lending_history)
    except:
        flash('Error loading history', 'error')
        return redirect(url_for('dashboard'))

@app.route('/update_borrow_status/<record_id>', methods=['POST'])
@login_required
def update_borrow_status(record_id):
    """Update borrow status (approve/return)"""
    try:
        record = borrow_history_collection.find_one({'_id': ObjectId(record_id)})
        if not record:
            flash('Record not found', 'error')
            return redirect(url_for('history'))
        
        # Check if user is the item owner
        if str(record['owner_id']) != session['user_id']:
            flash('You can only update your own items', 'error')
            return redirect(url_for('history'))
        
        new_status = request.form.get('status')
        if new_status in ['approved', 'borrowed', 'returned']:
            borrow_history_collection.update_one(
                {'_id': ObjectId(record_id)},
                {'$set': {'status': new_status}}
            )
            flash(f'Status updated to {new_status}', 'success')
        
        return redirect(url_for('history'))
    except:
        flash('Error updating status', 'error')
        return redirect(url_for('history'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
