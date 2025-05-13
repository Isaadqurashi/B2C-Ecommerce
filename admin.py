from main import app, db
from models import * 


from flask import flash, render_template, request, session, redirect, url_for
import uuid
import logging # Not used in this snippet, but kept if used elsewhere
from werkzeug.utils import secure_filename
import os
from datetime import date 
import datetime 
import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
import firebase_admin
from firebase_admin import credentials, db as firebase_db
from sqlalchemy import inspect 

# Ensure these model names are correct as per your models.py
# Define the list of models you want to back up
# IMPORTANT: Replace these with your actual model classes from models.py
# Example: MODELS_TO_BACKUP = [User, Product, Invoice]
# For this example, I'm using the models mentioned or inferred from your code:
# Ensure these are the actual class names from your 'models.py' file
try:
    # Ensure these Model classes are correctly imported from your models.py
    MODELS_TO_BACKUP = [Admin, Product, Order, OrderItem, OrderInfo]
except NameError:
    print("WARNING: One or more model classes for backup (Admin, Product, Order, OrderItem, OrderInfo) not found directly. Ensure they are imported correctly from models.py.")
    MODELS_TO_BACKUP = []


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Routing for the admin login page
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_id = request.form.get('admin_id')
        entered_password = request.form.get('password')

        if admin_id and entered_password:
            # Ensure Admin model is available
            if 'Admin' not in globals():
                flash('Admin model not loaded. Server configuration error.', 'danger')
                return render_template('admin_login.html', error='Server configuration error.')

            admin = Admin.query.filter_by(admin_id=admin_id).first()
            # IMPORTANT: Replace admin.login_id == entered_password with a secure password check (e.g., Werkzeug's check_password_hash)
            if admin and admin.login_id == entered_password: # Example: and check_password_hash(admin.password_hash, entered_password)
                session['admin_id'] = admin.admin_id
                flash('Login successful!', 'success')
                return redirect(url_for('admin_dashboard')) # Redirect to the new dashboard route
            else:
                error = 'Invalid Credentials. Please try again.'
        else:
            error = 'Missing username or password. Please try again.'
        return render_template('admin_login.html', error=error)

    # For GET request, if already logged in, redirect to dashboard, else show login
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

# NEW: Dedicated route for the admin dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for('admin_login'))
    # You can pass any necessary data to the dashboard template here
    # For example, admin_user = Admin.query.get(session['admin_id'])
    return render_template('admin_dashboard.html')


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        category = request.form.get('category')
        unit_weight = request.form.get('weight')
        quantity = request.form.get('quantity')
        filename = None

        if not all([name, description, price, category, unit_weight, quantity]):
            flash('All product fields are required.', 'danger')
            return render_template('admin_dashboard.html', active_tab='add_product') # Assuming tabs or sections

        # Check if product already exists
        existing_product = Product.query.filter_by(product_name=name, category=category, unit_weight=unit_weight).first()
        if existing_product:
            flash("Product with similar core details already exists.", "warning")
            return render_template('admin_dashboard.html', active_tab='add_product', name=name, description=description, price=price, category=category, weight=unit_weight, quantity=quantity)


        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename != '' and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                try:
                    image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                except Exception as e:
                    flash(f'Error saving image: {e}', 'danger')
                    return redirect(url_for('admin_dashboard')) # Or stay on add product page
            elif image_file.filename != '':
                flash('Invalid image file type or file not allowed.', 'error')
                return render_template('admin_dashboard.html', active_tab='add_product')

        new_product = Product(product_id = str(uuid.uuid4())[:20], product_name=name, product_description=description, price=price, quantity_pu = quantity, product_image = filename, category = category, unit_weight=unit_weight)
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_dashboard')) # Redirect to dashboard (or a product list page)

    # For GET request, show the part of the dashboard for adding products
    # The admin_dashboard.html template would need to handle showing the add product form
    return render_template('admin_dashboard.html', active_tab='add_product')


@app.route('/edit_product', methods=['GET', 'POST']) # Should ideally be /edit_product/<product_id> for GET
def edit_product():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        product_id = request.form.get('product_id')
        if not product_id:
            flash('Product ID is missing.', 'error')
            return redirect(url_for('admin_dashboard'))

        product = Product.query.filter_by(product_id=product_id).first()
        if not product:
            flash('Product not found.', 'error')
            return redirect(url_for('admin_dashboard'))

        product.product_name = request.form.get('new_name', product.product_name)
        product.product_description = request.form.get('new_description', product.product_description)
        new_price = request.form.get('new_price')
        if new_price is not None and new_price != '':
             try:
                 product.price = float(new_price) # ensure correct type
             except ValueError:
                 flash('Invalid price format.', 'error')
                 # return to an edit form for this product, prefilled
                 return redirect(url_for('admin_dashboard')) # Simplified for now

        # Add other fields as necessary
        # product.category = request.form.get('new_category', product.category)
        # Handle image update if needed

        db.session.commit()
        flash('Product updated successfully.', 'success')
        return redirect(url_for('admin_dashboard')) # Or a product list page

    # For GET: to show an edit form, you'd typically pass product_id in URL
    # e.g. @app.route('/edit_product/<product_id>', methods=['GET'])
    # and then fetch product and render an edit form.
    # For now, if accessed by GET, it will just redirect to dashboard.
    return redirect(url_for('admin_dashboard'))


@app.route('/remove_product', methods=['POST'])
def remove_product():
    if 'admin_id' not in session:
        flash('Please log in to remove products.', 'error')
        return redirect(url_for('admin_login'))

    product_id = request.form.get('product_id')
    if not product_id:
        flash('Product ID not provided.', 'error')
        return redirect(url_for('admin_dashboard'))

    product = Product.query.filter_by(product_id=product_id).first()
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(product)
    db.session.commit()

    flash('Product removed successfully.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/orders')
def admin_orders():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    if 'OrderInfo' not in globals():
        flash('OrderInfo model not loaded. Server configuration error.', 'danger')
        return redirect(url_for('admin_dashboard'))
    orders = OrderInfo.query.all()
    return render_template('orders.html', orders=orders) # Assuming you have an orders.html

@app.route('/analytics/')
def analytics():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return dash_app.index()


# --- Firebase initialization for backups ---
try:
    cred = credentials.Certificate('credentials.json')
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://kuchu-muchu-default-rtdb.firebaseio.com/'
        })
except Exception as e:
    logging.error(f"Failed to initialize Firebase Admin SDK: {e}")
    # flash("Firebase connection error. Backup functionality may be unavailable.", "danger") # Flashing here might be tricky before app context
    print(f"WARNING: Failed to initialize Firebase Admin SDK: {e}") # Print to console during startup
    pass


@app.route('/backup_database', methods=['POST'])
def backup_database_to_firebase():
    if 'admin_id' not in session:
        flash('Authentication required.', 'error')
        return redirect(url_for('admin_login'))

    if not firebase_admin._apps:
        flash('Firebase Admin SDK not initialized. Backup failed.', 'error')
        return redirect(url_for('admin_dashboard'))

    if not MODELS_TO_BACKUP:
        flash('No models configured for backup. Please check server configuration.', 'error')
        return redirect(url_for('admin_dashboard'))

    try:
        timestamp_str = datetime.datetime.utcnow().isoformat().replace(":", "_").replace(".", "-")
        backup_root_path = f'/postgresql_model_backups/{timestamp_str}'

        for model_class in MODELS_TO_BACKUP:
            if not hasattr(model_class, '__tablename__'):
                logging.warning(f"Model class {model_class} does not seem to be a valid SQLAlchemy model. Skipping.")
                continue
            table_name = model_class.__tablename__
            table_ref = firebase_db.reference(f'{backup_root_path}/{table_name}')
            
            with app.app_context(): # Ensure app context for db operations if any model access triggers it
                records = model_class.query.all()

            if not records:
                logging.info(f"No records found for table {table_name}. Skipping.")
                continue

            for record in records:
                record_dict = {}
                for column in inspect(model_class).columns:
                    value = getattr(record, column.name)
                    if isinstance(value, (datetime.datetime, datetime.date)):
                        value = value.isoformat()
                    elif isinstance(value, uuid.UUID):
                        value = str(value)
                    elif hasattr(value, 'quantize'): # Basic check for Decimal
                        value = str(value)
                    record_dict[column.name] = value
                table_ref.push().set(record_dict)
        
        flash('Database backup to Firebase successful!', 'success')
    except Exception as e:
        logging.error(f"Firebase backup failed: {e}", exc_info=True) # Log full traceback
        flash(f'Database backup to Firebase failed: {str(e)}', 'error')

    return redirect(url_for('admin_dashboard'))


# create Dash app
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/analytics/')

# Helper functions for Dash (data fetching)
def get_product_sales():
    with app.app_context():
        product_sales_data = []
        if 'Product' not in globals() or 'Order' not in globals() or 'OrderItem' not in globals():
            logging.error("One or more models (Product, Order, OrderItem) not available for get_product_sales.")
            return [] # Return empty list if models aren't loaded

        products = Product.query.all()
        for product in products:
            order_dates, quantity_sold, revenue = [], [], []
            sales_query = db.session.query(
                Order.order_date,
                db.func.sum(OrderItem.quantity).label('total_quantity'),
                db.func.sum(OrderItem.unit_price * OrderItem.quantity).label('total_revenue')
            ).join(OrderItem, Order.order_id == OrderItem.order_id)\
             .filter(OrderItem.product_id == product.product_id)\
             .group_by(Order.order_date)\
             .order_by(Order.order_date)\
             .all()
            for sale in sales_query:
                order_dates.append(sale.order_date.isoformat() if sale.order_date else None)
                quantity_sold.append(float(sale.total_quantity) if sale.total_quantity is not None else 0)
                revenue.append(float(sale.total_revenue) if sale.total_revenue is not None else 0)
            product_sales_data.append({
                'product_name': product.product_name,
                'order_dates': order_dates,
                'quantity_sold': quantity_sold,
                'revenue': revenue
            })
        return product_sales_data

def get_revenue_by_date():
    with app.app_context():
        revenue_by_date_data = []
        if 'Order' not in globals() or 'OrderItem' not in globals():
            logging.error("One or more models (Order, OrderItem) not available for get_revenue_by_date.")
            return []

        query_results = db.session.query(
            Order.order_date,
            db.func.sum(OrderItem.unit_price * OrderItem.quantity).label('daily_total_revenue')
        ).join(OrderItem, Order.order_id == OrderItem.order_id)\
         .group_by(Order.order_date)\
         .order_by(Order.order_date)\
         .all()
        for result in query_results:
            revenue_by_date_data.append({
                'order_date': result.order_date.isoformat() if result.order_date else None,
                'total_revenue': float(result.daily_total_revenue) if result.daily_total_revenue is not None else 0
            })
        return revenue_by_date_data

# Pre-fetch data for Dash layout (runs on app start)
# Consider using callbacks for dynamic updates if needed
_product_sales_for_dash = get_product_sales()
_revenue_by_date_for_dash = get_revenue_by_date()

dash_app.layout = html.Div(children=[
    html.H1(children='Product Sales Analytics'),
    html.H2(children='Quantity of each Product Sold Over Time'),
    dcc.Graph(
        id='product-sales-quantity-graph',
        figure={
            'data': [
                go.Scatter(
                    x=ps_data['order_dates'], y=ps_data['quantity_sold'],
                    mode='lines+markers', name=ps_data['product_name']
                ) for ps_data in _product_sales_for_dash
            ],
            'layout': go.Layout(xaxis={'title': 'Date'}, yaxis={'title': 'Quantity Sold'}, title='Quantity of each Product Sold')
        }
    ),
    html.H2(children='Revenue Generated by each Product Over Time'),
    dcc.Graph(
        id='product-sales-revenue-graph',
        figure={
            'data': [
                go.Scatter(
                    x=ps_data['order_dates'], y=ps_data['revenue'],
                    mode='lines+markers', name=ps_data['product_name']
                ) for ps_data in _product_sales_for_dash
            ],
            'layout': go.Layout(xaxis={'title': 'Date'}, yaxis={'title': 'Revenue'}, title='Revenue Generated by each Product')
        }
    ),
    html.H2(children='Total Revenue by Date'),
    dcc.Graph(
        id='total-revenue-by-date-graph',
        figure={
            'data': [
                go.Scatter(
                    x=[rbd['order_date'] for rbd in _revenue_by_date_for_dash],
                    y=[rbd['total_revenue'] for rbd in _revenue_by_date_for_dash],
                    mode='lines+markers'
                )
            ],
            'layout': go.Layout(title='Total Revenue by Date', xaxis={'title': 'Date'}, yaxis={'title': 'Total Revenue'})
        }
    )
])