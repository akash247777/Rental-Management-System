from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta, date
import bcrypt
import os
import mysql.connector
from dotenv import load_dotenv
import pandas as pd
import urllib.parse
from dateutil.relativedelta import relativedelta

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='../')
CORS(app)

# Database configuration
PRIMARY_DB_HOST = os.getenv('PRIMARY_DB_HOST', 'localhost')
PRIMARY_DB_DATABASE = os.getenv('PRIMARY_DB_DATABASE', 'AkashSG$Rental')
PRIMARY_DB_USER = os.getenv('PRIMARY_DB_USER', 'root')
PRIMARY_DB_PASSWORD = os.getenv('PRIMARY_DB_PASSWORD', 'Shivanadapg@7422')

# Create the connection string for SQLAlchemy
DB_HOST = PRIMARY_DB_HOST
DB_DATABASE = PRIMARY_DB_DATABASE
DB_USER = PRIMARY_DB_USER
DB_PASSWORD = PRIMARY_DB_PASSWORD
password = urllib.parse.quote_plus(DB_PASSWORD)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{password}@{DB_HOST}/{DB_DATABASE}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=12)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    __tablename__ = 'USERS'  # If your SQL Server table has a different name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')

# Column mapping for database to frontend field conversion
column_mapping = {
    'SITE': 'SITE',
    'STORE NAME': 'STORE NAME',
    'REGION': 'REGION',
    'DIV': 'DIV',
    'MANAGER': 'MANAGER',
    'ASST MANAGER': 'ASST MANAGER',
    'EXECUTIVE': 'EXECUTIVE',
    'D.O.O': 'D.O.O',
    'SQ.FT': 'SQ.FT',
    'AGREEMENT DATE': 'AGREEMENT DATE',
    'RENT POSITION DATE': 'RENT POSITION DATE',
    'RENT EFFECTIVE DATE': 'RENT EFFECTIVE DATE',
    'AGREEMENT VALID UPTO': 'AGREEMENT VALID UPTO',
    'CURRENT DATE': 'CURRENT DATE',
    'LEASE PERIOD': 'LEASE PERIOD',
    'RENT FREE PERIOD DAYS': 'RENT FREE PERIOD DAYS',
    'RENT EFFECTIVE AMOUNT': 'RENT EFFECTIVE AMOUNT',
    'PRESENT RENT': 'PRESENT RENT',
    'HIKE %': 'HIKE %',
    'HIKE YEAR': 'HIKE YEAR',
    'RENT DEPOSIT': 'RENT DEPOSIT',
    'OWNER NAME-1': 'OWNER NAME-1',
    'OWNER NAME-2': 'OWNER NAME-2',
    'OWNER NAME-3': 'OWNER NAME-3',
    'OWNER NAME-4': 'OWNER NAME-4',
    'OWNER NAME-5': 'OWNER NAME-5',
    'OWNER NAME-6': 'OWNER NAME-6',
    'OWNER MOBILE': 'OWNER MOBILE',
    'CURRENT DATE 1': 'CURRENT DATE 1',
    'VALIDITY DATE': 'VALIDITY DATE',
    'GST NUMBER': 'GST NUMBER',
    'PAN NUMBER': 'PAN NUMBER',
    'TDS PERCENTAGE': 'TDS PERCENTAGE',
    'MATURE': 'MATURE',
    'STATUS': 'STATUS',
    'REMARKS': 'REMARKS'
}

# Reverse mapping for frontend to database field conversion
field_mapping = {
    'SITE': '`SITE`',
    'STORE NAME': '`STORE NAME`',
    'REGION': '`REGION`',
    'DIV': '`DIV`',
    'MANAGER': '`MANAGER`',
    'ASST MANAGER': '`ASST MANAGER`',
    'EXECUTIVE': '`EXECUTIVE`',
    'D.O.O': '`D.O.O`',
    'SQ.FT': '`SQ.FT`',
    'AGREEMENT DATE': '`AGREEMENT DATE`',
    'RENT POSITION DATE': '`RENT POSITION DATE`',
    'RENT EFFECTIVE DATE': '`RENT EFFECTIVE DATE`',
    'AGREEMENT VALID UPTO': '`AGREEMENT VALID UPTO`',
    'CURRENT DATE': '`CURRENT DATE`',
    'LEASE PERIOD': '`LEASE PERIOD`',
    'RENT FREE PERIOD DAYS': '`RENT FREE PERIOD DAYS`',
    'RENT EFFECTIVE AMOUNT': '`RENT EFFECTIVE AMOUNT`',
    'PRESENT RENT': '`PRESENT RENT`',
    'HIKE %': '`HIKE %`',
    'HIKE YEAR': '`HIKE YEAR`',
    'RENT DEPOSIT': '`RENT DEPOSIT`',
    'OWNER NAME-1': '`OWNER NAME-1`',
    'OWNER NAME-2': '`OWNER NAME-2`',
    'OWNER NAME-3': '`OWNER NAME-3`',
    'OWNER NAME-4': '`OWNER NAME-4`',
    'OWNER NAME-5': '`OWNER NAME-5`',
    'OWNER NAME-6': '`OWNER NAME-6`',
    'OWNER MOBILE': '`OWNER MOBILE`',
    'CURRENT DATE 1': '`CURRENT DATE 1`',
    'VALIDITY DATE': '`VALIDITY DATE`',
    'GST NUMBER': '`GST NUMBER`',
    'PAN NUMBER': '`PAN NUMBER`',
    'TDS PERCENTAGE': '`TDS PERCENTAGE`',
    'MATURE': '`MATURE`',
    'STATUS': '`STATUS`',
    'REMARKS': '`REMARKS`',
    # Legacy mappings for backward compatibility
    'site_id': '`SITE`',
    'site': '`SITE`', 
    'store_name': '`STORE NAME`',
    'region': '`REGION`',
    'div': '`DIV`',
    'manager': '`MANAGER`',
    'asst_manager': '`ASST MANAGER`',
    'executive': '`EXECUTIVE`',
    'doo': '`D.O.O`',
    'sqft': '`SQ.FT`',
    'agreement_date': '`AGREEMENT DATE`',
    'rent_position_date': '`RENT POSITION DATE`',
    'rent_effective_date': '`RENT EFFECTIVE DATE`',
    'agreement_valid_upto': '`AGREEMENT VALID UPTO`',
    'current_date': '`CURRENT DATE`',
    'lease_period': '`LEASE PERIOD`',
    'rent_free_period_days': '`RENT FREE PERIOD DAYS`',
    'rent_effective_amount': '`RENT EFFECTIVE AMOUNT`',
    'present_rent': '`PRESENT RENT`',
    'hike_percentage': '`HIKE %`',
    'hike_year': '`HIKE YEAR`',
    'rent_deposit': '`RENT DEPOSIT`',
    'owner_name1': '`OWNER NAME-1`',
    'owner_name2': '`OWNER NAME-2`',
    'owner_name3': '`OWNER NAME-3`',
    'owner_name4': '`OWNER NAME-4`',
    'owner_name5': '`OWNER NAME-5`',
    'owner_name6': '`OWNER NAME-6`',
    'owner_mobile': '`OWNER MOBILE`',
    'current_date1': '`CURRENT DATE 1`',
    'validity_date': '`VALIDITY DATE`',
    'gst_number': '`GST NUMBER`',
    'pan_number': '`PAN NUMBER`',
    'tds_percentage': '`TDS PERCENTAGE`',
    'mature': '`MATURE`',
    'status': '`STATUS`',
    'remarks': '`REMARKS`'
}

class Site(db.Model):
    __tablename__ = 'rentdetails'  # Actual table name from the database
    SITE = db.Column('SITE', db.String(10), primary_key=True, nullable=False)
    STORE_NAME = db.Column('STORE NAME', db.String(100), nullable=False)
    REGION = db.Column(db.Date, nullable=False)
    DIV = db.Column(db.String(10), nullable=False)
    MANAGER = db.Column(db.String(100), nullable=False)
    ASST_MANAGER = db.Column('ASST MANAGER', db.String(100), nullable=False)
    EXECUTIVE = db.Column(db.String(100), nullable=False)
    DOO = db.Column('D.O.O', db.Date, nullable=False)
    SQFT = db.Column('SQ.FT', db.Integer, nullable=False)
    AGREEMENT_DATE = db.Column('AGREEMENT DATE', db.Date, nullable=False)
    RENT_POSITION_DATE = db.Column('RENT POSITION DATE', db.Date, nullable=False)
    RENT_EFFECTIVE_DATE = db.Column('RENT EFFECTIVE DATE', db.Date, nullable=False)
    AGREEMENT_VALID_UPTO = db.Column('AGREEMENT VALID UPTO', db.Date)
    CURRENT_DATE = db.Column('CURRENT DATE', db.Date)
    LEASE_PERIOD = db.Column('LEASE PERIOD', db.Integer, nullable=False)
    RENT_FREE_PERIOD_DAYS = db.Column('RENT FREE PERIOD DAYS', db.Integer, nullable=False)
    RENT_EFFECTIVE_AMOUNT = db.Column('RENT EFFECTIVE AMOUNT', db.Float, nullable=False)
    PRESENT_RENT = db.Column('PRESENT RENT', db.Float, nullable=False)
    HIKE_PERCENTAGE = db.Column('HIKE %', db.Float, nullable=False)
    HIKE_YEAR = db.Column('HIKE YEAR', db.Integer, nullable=False)
    RENT_DEPOSIT = db.Column('RENT DEPOSIT', db.Float, nullable=False)
    OWNER_NAME1 = db.Column('OWNER NAME-1', db.String(100), nullable=False)
    OWNER_NAME2 = db.Column('OWNER NAME-2', db.String(100))
    OWNER_NAME3 = db.Column('OWNER NAME-3', db.String(100))
    OWNER_NAME4 = db.Column('OWNER NAME-4', db.String(100))
    OWNER_NAME5 = db.Column('OWNER NAME-5', db.String(100))
    OWNER_NAME6 = db.Column('OWNER NAME-6', db.String(100))
    OWNER_MOBILE = db.Column('OWNER MOBILE', db.String(20))
    CURRENT_DATE1 = db.Column('CURRENT DATE 1', db.Date)
    VALIDITY_DATE = db.Column('VALIDITY DATE', db.Date)
    GST_NUMBER = db.Column('GST NUMBER', db.String(20), nullable=False)
    PAN_NUMBER = db.Column('PAN NUMBER', db.String(20), nullable=False)
    TDS_PERCENTAGE = db.Column('TDS PERCENTAGE', db.Float, nullable=False)
    MATURE = db.Column(db.String(3), nullable=False)
    STATUS = db.Column(db.String(10), nullable=False)
    REMARKS = db.Column(db.Text)

# Direct connection for custom queries
def get_db_connection(use_primary=True):
    """
    Get database connection using simple mysql.connector
    Returns None if connection fails
    """
    try:
        print(f"Connecting to database at {PRIMARY_DB_HOST}...")
        conn = mysql.connector.connect(
            host=PRIMARY_DB_HOST,
            user=PRIMARY_DB_USER,
            password=PRIMARY_DB_PASSWORD,
            database=PRIMARY_DB_DATABASE
        )
        print("Database connection successful!")
        return conn
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        return None

# Routes
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify({
        'status': 'ok',
        'message': 'API is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        print(f"Login attempt with username: {data['username']}")  # Debug print
        
        # First check fallback credentials
        if data['username'] in ['krishna', 'kuber'] and data['password'] in ['krishna@123', 'kuber@123']:
            access_token = create_access_token(identity=data['username'])
            return jsonify({
                'access_token': access_token,
                'user': {
                    'username': data['username'],
                    'role': 'admin'
                }
            }), 200
        
        # Then try database authentication
        conn = None
        cursor = None
        try:
            # Try to initialize tables if this is first time
            create_tables_if_needed()
            
            conn = get_db_connection()
            if conn is None:
                return jsonify({'message': 'Database connection failed. Using fallback credentials only.'}), 500
                
            cursor = conn.cursor()
            
            # Query for user
            cursor.execute("SELECT password, role FROM USERS WHERE username = %s", (data['username'],))
            user_data = cursor.fetchone()
            print(f"User data fetched: {user_data}")  # Debug print
            
            if user_data:
                stored_hash = user_data[0].encode('utf-8')
                input_password = data['password'].encode('utf-8')
                
                if bcrypt.checkpw(input_password, stored_hash):
                    access_token = create_access_token(identity=data['username'])
                    return jsonify({
                        'access_token': access_token,
                        'user': {
                            'username': data['username'],
                            'role': user_data[1]
                        }
                    }), 200
            
            print("Invalid credentials")  # Debug print
            return jsonify({'message': 'Invalid credentials'}), 401
            
        except Exception as e:
            print(f"Database error during login: {str(e)}")
            return jsonify({'message': 'Invalid credentials'}), 401
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'message': 'An error occurred during login'}), 500

# Modified site search to use direct SQL connection if ORM fails
@app.route('/api/sites', methods=['GET'])
@jwt_required()
def get_sites():
    site_id = request.args.get('site_id')
    
    # Use primary DB when fetching a specific site
    use_primary = site_id is not None
    print(f"get_sites called with site_id={site_id}, using primary DB: {use_primary}")
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection(use_primary=use_primary)
        if conn is None:
            print("Error: Failed to get database connection")
            return jsonify({'message': 'Database connection failed. Please try again later.'}), 503
            
        cursor = conn.cursor()
        
        if site_id:
            # First try exact case match
            print(f"Fetching site with ID: {site_id}")
            query = "SELECT * FROM rentdetails WHERE SITE = %s"
            cursor.execute(query, [site_id])
            rows = cursor.fetchall()
            
            # If no results, try case-insensitive match
            if not rows:
                print(f"No exact match for site ID '{site_id}', trying case-insensitive search")
                query = "SELECT * FROM rentdetails WHERE UPPER(SITE) = UPPER(%s)"
                cursor.execute(query, [site_id])
                rows = cursor.fetchall()
                
            if not rows:
                print(f"Site ID '{site_id}' not found in database")
                return jsonify({'message': f'Site ID "{site_id}" not found'}), 404
                
            # Process just the one site
            site_data = process_site_data(rows[0], cursor.description)
            print(f"Returning site data for {site_id}")
            print(f"GST NUMBER value: {site_data.get('gst_number')}")
            print(f"PAN NUMBER value: {site_data.get('pan_number')}")
            return jsonify(site_data), 200
        else:
            # Return list of all sites (simplified data)
            query = "SELECT SITE, `STORE NAME`, REGION, DIV, `GST NUMBER`, `PAN NUMBER` FROM rentdetails LIMIT 100"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            sites = []
            for row in rows:
                sites.append({
                    'site_id': row[0] if len(row) > 0 else '',
                    'store_name': row[1] if len(row) > 1 else '',
                    'region': row[2] if len(row) > 2 else '',
                    'div': row[3] if len(row) > 3 else '',
                    'gst_number': row[4] if len(row) > 4 and row[4] is not None else '',
                    'pan_number': row[5] if len(row) > 5 and row[5] is not None else ''
                })
            
            print(f"Returning list of {len(sites)} sites")
            print(f"Sample site GST NUMBER: {sites[0].get('gst_number') if sites else 'No sites'}")
            print(f"Sample site PAN NUMBER: {sites[0].get('pan_number') if sites else 'No sites'}")
            return jsonify({'sites': sites}), 200
    
    except Exception as e:
        print(f"Error in get_sites: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Error fetching site data: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def process_site_data(row, description):
    """Process a database row into a site data dictionary"""
    # Get column names
    columns = [col[0] for col in description]
    print(f"Site data columns: {columns}")
    print(f"Raw row data: {row}")
    
    # Create a dictionary mapping column names to their indices
    column_map = {col.upper(): i for i, col in enumerate(columns)}
    print(f"Column map: {column_map}")
    
    # Log specific columns we're having issues with
    print(f"Looking for 'ASST MANAGER' in columns, found: {'ASST MANAGER' in column_map}")
    print(f"Looking for 'GST NUMBER' in columns, found: {'GST NUMBER' in column_map}")
    print(f"Looking for 'PAN NUMBER' in columns, found: {'PAN NUMBER' in column_map}")
    
    # Get indices for special columns
    asst_manager_idx = column_map.get('ASST MANAGER')
    gst_number_idx = column_map.get('GST NUMBER')
    pan_number_idx = column_map.get('PAN NUMBER')
    tds_percentage_idx = column_map.get('TDS PERCENTAGE')
    
    # Log what indices were found
    print(f"Indices found - ASST MANAGER: {asst_manager_idx}, GST NUMBER: {gst_number_idx}, PAN NUMBER: {pan_number_idx}, TDS PERCENTAGE: {tds_percentage_idx}")
    
    # Get the site value to use in multiple fields
    site_value = row[column_map.get('SITE', 0)] if 'SITE' in column_map else row[0]
    print(f"Site value found: {site_value}")
    
    # Build the site data dictionary with appropriate field mappings
    site_data = {
        'SITE': site_value,  # Use actual MySQL column name
        'site_id': site_value,  # Include site_id for backward compatibility
        'site': site_value,     # Include site for backward compatibility
        'STORE NAME': row[column_map.get('STORE NAME', 1)] if 'STORE NAME' in column_map else row[1],
        'REGION': row[column_map.get('REGION', 2)] if 'REGION' in column_map else row[2],
        'DIV': row[column_map.get('DIV', 3)] if 'DIV' in column_map else row[3],
        'MANAGER': row[column_map.get('MANAGER', 4)] if 'MANAGER' in column_map and len(row) > column_map.get('MANAGER', 4) else '',
        'ASST MANAGER': row[asst_manager_idx] if asst_manager_idx is not None and len(row) > asst_manager_idx else '',
        'EXECUTIVE': row[column_map.get('EXECUTIVE', 6)] if 'EXECUTIVE' in column_map and len(row) > column_map.get('EXECUTIVE', 6) else '',
        'D.O.O': format_date(row[column_map.get('D.O.O', 7)]) if 'D.O.O' in column_map and len(row) > column_map.get('D.O.O', 7) else '',
        'SQ.FT': row[column_map.get('SQ.FT', 8)] if 'SQ.FT' in column_map and len(row) > column_map.get('SQ.FT', 8) else 0,
        'AGREEMENT DATE': format_date(row[column_map.get('AGREEMENT DATE', 9)]) if 'AGREEMENT DATE' in column_map and len(row) > column_map.get('AGREEMENT DATE', 9) else '',
        'RENT POSITION DATE': format_date(row[column_map.get('RENT POSITION DATE', 10)]) if 'RENT POSITION DATE' in column_map and len(row) > column_map.get('RENT POSITION DATE', 10) else '',
        'RENT EFFECTIVE DATE': format_date(row[column_map.get('RENT EFFECTIVE DATE', 11)]) if 'RENT EFFECTIVE DATE' in column_map and len(row) > column_map.get('RENT EFFECTIVE DATE', 11) else '',
        'AGREEMENT VALID UPTO': format_date(row[column_map.get('AGREEMENT VALID UPTO', 12)]) if 'AGREEMENT VALID UPTO' in column_map and len(row) > column_map.get('AGREEMENT VALID UPTO', 12) else '',
        'CURRENT DATE': format_date(row[column_map.get('CURRENT DATE', 13)]) if 'CURRENT DATE' in column_map and len(row) > column_map.get('CURRENT DATE', 13) else '',
        'LEASE PERIOD': row[column_map.get('LEASE PERIOD', 14)] if 'LEASE PERIOD' in column_map and len(row) > column_map.get('LEASE PERIOD', 14) else 0,
        'RENT FREE PERIOD DAYS': row[column_map.get('RENT FREE PERIOD DAYS', 15)] if 'RENT FREE PERIOD DAYS' in column_map and len(row) > column_map.get('RENT FREE PERIOD DAYS', 15) else 0,
        'RENT EFFECTIVE AMOUNT': row[column_map.get('RENT EFFECTIVE AMOUNT', 16)] if 'RENT EFFECTIVE AMOUNT' in column_map and len(row) > column_map.get('RENT EFFECTIVE AMOUNT', 16) else 0,
        'PRESENT RENT': row[column_map.get('PRESENT RENT', 17)] if 'PRESENT RENT' in column_map and len(row) > column_map.get('PRESENT RENT', 17) else 0,
        'HIKE %': row[column_map.get('HIKE %', 18)] if 'HIKE %' in column_map and len(row) > column_map.get('HIKE %', 18) else 0,
        'HIKE YEAR': row[column_map.get('HIKE YEAR', 19)] if 'HIKE YEAR' in column_map and len(row) > column_map.get('HIKE YEAR', 19) else 0,
        'RENT DEPOSIT': row[column_map.get('RENT DEPOSIT', 20)] if 'RENT DEPOSIT' in column_map and len(row) > column_map.get('RENT DEPOSIT', 20) else 0,
        'OWNER NAME-1': row[column_map.get('OWNER NAME-1', 21)] if 'OWNER NAME-1' in column_map and len(row) > column_map.get('OWNER NAME-1', 21) else '',
        'OWNER NAME-2': row[column_map.get('OWNER NAME-2', 22)] if 'OWNER NAME-2' in column_map and len(row) > column_map.get('OWNER NAME-2', 22) else '',
        'OWNER NAME-3': row[column_map.get('OWNER NAME-3', 23)] if 'OWNER NAME-3' in column_map and len(row) > column_map.get('OWNER NAME-3', 23) else '',
        'OWNER NAME-4': row[column_map.get('OWNER NAME-4', 24)] if 'OWNER NAME-4' in column_map and len(row) > column_map.get('OWNER NAME-4', 24) else '',
        'OWNER NAME-5': row[column_map.get('OWNER NAME-5', 25)] if 'OWNER NAME-5' in column_map and len(row) > column_map.get('OWNER NAME-5', 25) else '',
        'OWNER NAME-6': row[column_map.get('OWNER NAME-6', 26)] if 'OWNER NAME-6' in column_map and len(row) > column_map.get('OWNER NAME-6', 26) else '',
        'OWNER MOBILE': row[column_map.get('OWNER MOBILE', 27)] if 'OWNER MOBILE' in column_map and len(row) > column_map.get('OWNER MOBILE', 27) else '',
        'CURRENT DATE 1': format_date(row[column_map.get('CURRENT DATE 1', 28)]) if 'CURRENT DATE 1' in column_map and len(row) > column_map.get('CURRENT DATE 1', 28) else '',
        'VALIDITY DATE': format_date(row[column_map.get('VALIDITY DATE', 29)]) if 'VALIDITY DATE' in column_map and len(row) > column_map.get('VALIDITY DATE', 29) else '',
        'GST NUMBER': row[gst_number_idx] if gst_number_idx is not None and len(row) > gst_number_idx and row[gst_number_idx] is not None else '',
        'PAN NUMBER': row[pan_number_idx] if pan_number_idx is not None and len(row) > pan_number_idx and row[pan_number_idx] is not None else '',
        'TDS PERCENTAGE': row[tds_percentage_idx] if tds_percentage_idx is not None and len(row) > tds_percentage_idx and row[tds_percentage_idx] is not None else 0,
        'MATURE': row[column_map.get('MATURE', 33)] if 'MATURE' in column_map and len(row) > column_map.get('MATURE', 33) else '',
        'STATUS': row[column_map.get('STATUS', 34)] if 'STATUS' in column_map and len(row) > column_map.get('STATUS', 34) else '',
        'REMARKS': row[column_map.get('REMARKS', 35)] if 'REMARKS' in column_map and len(row) > column_map.get('REMARKS', 35) else ''
    }
    
    # Add backward compatibility fields
    site_data.update({
        'store_name': site_data['STORE NAME'],
        'region': site_data['REGION'],
        'div': site_data['DIV'],
        'manager': site_data['MANAGER'],
        'asst_manager': site_data['ASST MANAGER'],
        'executive': site_data['EXECUTIVE'],
        'doo': site_data['D.O.O'],
        'sqft': site_data['SQ.FT'],
        'agreement_date': site_data['AGREEMENT DATE'],
        'rent_position_date': site_data['RENT POSITION DATE'],
        'rent_effective_date': site_data['RENT EFFECTIVE DATE'],
        'agreement_valid_upto': site_data['AGREEMENT VALID UPTO'],
        'current_date': site_data['CURRENT DATE'],
        'lease_period': site_data['LEASE PERIOD'],
        'rent_free_period_days': site_data['RENT FREE PERIOD DAYS'],
        'rent_effective_amount': site_data['RENT EFFECTIVE AMOUNT'],
        'present_rent': site_data['PRESENT RENT'],
        'hike_percentage': site_data['HIKE %'],
        'hike_year': site_data['HIKE YEAR'],
        'rent_deposit': site_data['RENT DEPOSIT'],
        'owner_name1': site_data['OWNER NAME-1'],
        'owner_name2': site_data['OWNER NAME-2'],
        'owner_name3': site_data['OWNER NAME-3'],
        'owner_name4': site_data['OWNER NAME-4'],
        'owner_name5': site_data['OWNER NAME-5'],
        'owner_name6': site_data['OWNER NAME-6'],
        'owner_mobile': site_data['OWNER MOBILE'],
        'current_date1': site_data['CURRENT DATE 1'],
        'validity_date': site_data['VALIDITY DATE'],
        'gst_number': site_data['GST NUMBER'],
        'pan_number': site_data['PAN NUMBER'],
        'tds_percentage': site_data['TDS PERCENTAGE'],
        'mature': site_data['MATURE'],
        'status': site_data['STATUS'],
        'remarks': site_data['REMARKS']
    })
    
    # Calculate CURRENT DATE 1 (time elapsed since RENT POSITION DATE)
    if row[column_map.get('RENT POSITION DATE')] is not None:
        try:
            rpd = row[column_map.get('RENT POSITION DATE')]
            if isinstance(rpd, str):
                rpd = datetime.strptime(rpd, '%Y-%m-%d').date()
            current_date = datetime.now().date()
            
            # Calculate the difference between current date and rent position date
            diff = relativedelta(current_date, rpd)
            
            site_data['CURRENT DATE 1'] = (
                f"{diff.years} {'Years' if diff.years != 1 else 'Year'}, "
                f"{diff.months} {'Months' if diff.months != 1 else 'Month'}, "
                f"{diff.days} {'Days' if diff.days != 1 else 'Day'}"
            )
        except Exception as e:
            print(f"Error calculating CURRENT DATE 1: {str(e)}")
            site_data['CURRENT DATE 1'] = ''

    # Calculate VALIDITY DATE (time remaining until AGREEMENT VALID UPTO)
    if row[column_map.get('AGREEMENT VALID UPTO')] is not None:
        try:
            avu = row[column_map.get('AGREEMENT VALID UPTO')]
            if isinstance(avu, str):
                avu = datetime.strptime(avu, '%Y-%m-%d').date()
            current_date = datetime.now().date()
            
            # Calculate the difference between agreement valid upto and current date
            diff = relativedelta(avu, current_date)
            
            site_data['VALIDITY DATE'] = (
                f"{diff.years} {'Years' if diff.years != 1 else 'Year'}, "
                f"{diff.months} {'Months' if diff.months != 1 else 'Month'}, "
                f"{diff.days} {'Days' if diff.days != 1 else 'Day'}"
            )
        except Exception as e:
            print(f"Error calculating VALIDITY DATE: {str(e)}")
            site_data['VALIDITY DATE'] = ''

    # Print what fields are available for debugging
    print(f"Processed site data keys: {site_data.keys()}")
    print(f"ASST MANAGER value: {site_data.get('ASST MANAGER')}")
    print(f"GST NUMBER value: {site_data.get('GST NUMBER')}")
    print(f"PAN NUMBER value: {site_data.get('PAN NUMBER')}")
    
    return site_data

def format_date(date_value):
    """Format a date value as a string"""
    if not date_value:
        return ""
    try:
        if isinstance(date_value, str):
            return date_value
        return date_value.strftime('%Y-%m-%d')
    except Exception as e:
        print(f"Error formatting date {date_value}: {str(e)}")
        return str(date_value) if date_value else ""

@app.route('/api/sites', methods=['POST'])
@jwt_required()
def create_site():
    data = request.get_json()
    print("Received data for site creation:", data)
    
    # Normalize site_id field - accept either 'site' or 'site_id'
    if 'site' in data and not 'site_id' in data:
        print(f"Using 'site' field as site_id: {data['site']}")
        data['site_id'] = data['site']
    
    # Validate required fields
    required_fields = ['site_id', 'store_name', 'region', 'div', 'manager', 'asst_manager', 
                      'executive', 'doo', 'sqft', 'agreement_date', 'rent_position_date',
                      'rent_effective_date', 'lease_period', 'rent_free_period_days',
                      'rent_effective_amount', 'present_rent', 'hike_percentage', 'hike_year',
                      'rent_deposit', 'owner_name1', 'gst_number', 'pan_number',
                      'tds_percentage', 'mature', 'status']
    
    for field in required_fields:
        if field not in data:
            print(f"Missing required field: {field}")
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'message': 'Database connection failed. Please try again later.'}), 503
            
        cursor = conn.cursor()
        
        # Check if site ID already exists
        cursor.execute("SELECT COUNT(*) FROM rentdetails WHERE `SITE` = %s", (data['site_id'],))
        count = cursor.fetchone()[0]
        if count > 0:
            return jsonify({'message': f"Site ID {data['site_id']} already exists"}), 400
        
        # Prepare the SQL query
        columns = [
            "`SITE`", "`STORE NAME`", "`REGION`", "`DIV`", "`MANAGER`", "`ASST MANAGER`", "`EXECUTIVE`", 
            "`D.O.O`", "`SQ.FT`", "`AGREEMENT DATE`", "`RENT POSITION DATE`", "`RENT EFFECTIVE DATE`", 
            "`LEASE PERIOD`", "`RENT FREE PERIOD DAYS`", "`RENT EFFECTIVE AMOUNT`", "`PRESENT RENT`", 
            "`HIKE %`", "`HIKE YEAR`", "`RENT DEPOSIT`", "`OWNER NAME-1`", "`OWNER NAME-2`", 
            "`OWNER NAME-3`", "`OWNER NAME-4`", "`OWNER NAME-5`", "`OWNER NAME-6`", 
            "`OWNER MOBILE`", "`GST NUMBER`", "`PAN NUMBER`", "`TDS PERCENTAGE`", "`MATURE`", 
            "`STATUS`", "`REMARKS`"
        ]
        
        # Optional fields
        if 'agreement_valid_upto' in data and data['agreement_valid_upto']:
            columns.append("`AGREEMENT VALID UPTO`")
        
        if 'current_date' in data and data['current_date']:
            columns.append("`CURRENT DATE`")
            
        if 'current_date1' in data and data['current_date1']:
            columns.append("`CURRENT DATE 1`")
            
        if 'validity_date' in data and data['validity_date']:
            columns.append("`VALIDITY DATE`")
        
        # Create placeholders for values
        placeholders = ['%s'] * len(columns)
        
        # Prepare values
        values = [
            data['site_id'], data['store_name'], data['region'], data['div'], 
            data['manager'], data['asst_manager'], data['executive'], 
            data['doo'], data['sqft'], data['agreement_date'], data['rent_position_date'], 
            data['rent_effective_date'], data['lease_period'], data['rent_free_period_days'], 
            data['rent_effective_amount'], data['present_rent'], data['hike_percentage'], 
            data['hike_year'], data['rent_deposit'], data['owner_name1'],
            data.get('owner_name2'), data.get('owner_name3'), data.get('owner_name4'),
            data.get('owner_name5'), data.get('owner_name6'), data.get('owner_mobile'),
            data['gst_number'], data['pan_number'], data['tds_percentage'], 
            data['mature'], data['status'], data.get('remarks')
        ]
        
        # Add optional values
        if 'agreement_valid_upto' in data and data['agreement_valid_upto']:
            values.append(data['agreement_valid_upto'])
        
        if 'current_date' in data and data['current_date']:
            values.append(data['current_date'])
            
        if 'current_date1' in data and data['current_date1']:
            values.append(data['current_date1'])
            
        if 'validity_date' in data and data['validity_date']:
            values.append(data['validity_date'])
        
        # Build and execute the INSERT query
        column_names = ', '.join(columns)
        placeholder_str = ', '.join(placeholders)
        query = f"INSERT INTO rentdetails ({column_names}) VALUES ({placeholder_str})"
        print(f"Insert query: {query}")
        print(f"Insert values: {values}")
        cursor.execute(query, values)
        conn.commit()
        
        return jsonify({'message': 'Site created successfully'}), 201
    except Exception as e:
        print(f"Error creating site: {str(e)}")
        return jsonify({'message': f"Error creating site: {str(e)}"}), 400
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/sites/<site_id>', methods=['PUT'])
@jwt_required()
def update_site(site_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'message': 'Database connection failed. Please try again later.'}), 503
            
        cursor = conn.cursor()
        
        data = request.get_json()
        print("Received update data:", data)  # Debug print

        # CRITICAL: Add site_id to the data
        if 'site_id' not in data and 'SITE' not in data:
            print("Missing site_id. Setting from URL parameter.")
            data['site_id'] = site_id
        elif 'SITE' in data and data['SITE'] != site_id:
            print(f"Site ID mismatch: URL={site_id}, data={data['SITE']} - Using URL parameter")
            data['SITE'] = site_id
        elif 'site_id' in data and data['site_id'] != site_id:
            print(f"Site ID mismatch: URL={site_id}, data={data['site_id']} - Using URL parameter")
            data['site_id'] = site_id
            
        print(f"Using site_id: {site_id}")
        
        # Handle direct MySQL column names - We need to do this because the frontend
        # is now using the exact MySQL column names
        set_clauses = []
        values = []
        
        # List of date fields to process
        date_fields = [
            'AGREEMENT DATE', 
            'RENT POSITION DATE', 
            'RENT EFFECTIVE DATE',
            'AGREEMENT VALID UPTO',
            'CURRENT DATE',
            'CURRENT DATE 1',
            'VALIDITY DATE',
            'D.O.O'
        ]
        
        for key, value in data.items():
            if key != 'site_id' and key != 'SITE':  # Skip site_id in the update
                db_field = None
                
                # Check if it's a direct MySQL column name
                if key in column_mapping.keys():
                    db_field = f"`{key}`"
                    print(f"Direct MySQL column name: {key}")
                # Otherwise check if it has a mapping
                elif key in field_mapping:
                    db_field = field_mapping[key]
                    print(f"Mapped field {key} to {db_field}")
                
                if db_field and value is not None:
                    # Handle date fields
                    if key in date_fields and value:
                        try:
                            # Convert date string to SQL format (YYYY-MM-DD)
                            date_str = str(value).strip()
                            print(f"Processing date field {key}: {date_str}")
                            
                            # Skip empty values
                            if not date_str or date_str == 'N/A':
                                print(f"Skipping empty date value for {key}")
                                continue
                                
                            formatted_date = None
                            
                            # Check if the format is DD-MM-YYYY
                            if date_str.count('-') == 2:
                                date_parts = date_str.split('-')
                                
                                # If format is DD-MM-YYYY (first part is 1 or 2 digits)
                                if len(date_parts) == 3 and len(date_parts[0]) <= 2 and len(date_parts[2]) == 4:
                                    # Convert from DD-MM-YYYY to YYYY-MM-DD
                                    formatted_date = f"{date_parts[2]}-{date_parts[1].zfill(2)}-{date_parts[0].zfill(2)}"
                                    print(f"Converted date from DD-MM-YYYY to YYYY-MM-DD: {formatted_date}")
                                # If format is already YYYY-MM-DD
                                elif len(date_parts) == 3 and len(date_parts[0]) == 4:
                                    formatted_date = date_str
                                    print(f"Date already in YYYY-MM-DD format: {formatted_date}")
                            
                            # Try parsing with multiple formats if not yet formatted
                            if not formatted_date:
                                formats_to_try = ['%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']
                                for fmt in formats_to_try:
                                    try:
                                        dt = datetime.strptime(date_str, fmt)
                                        formatted_date = dt.strftime('%Y-%m-%d')
                                        print(f"Parsed date with format {fmt}: {formatted_date}")
                                        break
                                    except ValueError:
                                        continue
                            
                            if formatted_date:
                                value = formatted_date
                                print(f"Final date value for {key}: {value}")
                            else:
                                print(f"Could not parse date for {key}: {date_str}, skipping")
                                continue
                        except Exception as e:
                            print(f"Error formatting date for {key}: {str(e)}")
                            continue
                    
                    # Clean numeric values
                    elif key in ['SQ.FT', 'LEASE PERIOD', 'RENT FREE PERIOD DAYS', 'HIKE %', 'HIKE YEAR', 'RENT DEPOSIT', 'TDS PERCENTAGE']:
                        try:
                            cleaned_value = str(value).replace('₹', '').replace(',', '').replace('%', '').strip()
                            if cleaned_value:
                                if key in ['SQ.FT', 'LEASE PERIOD', 'RENT FREE PERIOD DAYS', 'HIKE YEAR']:
                                    value = int(float(cleaned_value))
                                else:
                                    value = float(cleaned_value)
                            print(f"Cleaned numeric value for {key}: {value}")
                        except Exception as e:
                            print(f"Error cleaning numeric field {key}: {str(e)}")
                            continue
                    
                    set_clauses.append(f"{db_field} = %s")
                    values.append(value)
                    print(f"Adding field to update: {db_field} = {value}")
        
        if not set_clauses:
            return jsonify({'message': 'No fields to update'}), 400
        
        values.append(site_id)  # Add site_id for WHERE clause
        
        query = f"UPDATE rentdetails SET {', '.join(set_clauses)} WHERE SITE = %s"
        print("Executing query:", query)
        print("With values:", values)
        
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            return jsonify({'message': 'No records were updated'}), 404
        
        conn.commit()
        return jsonify({'message': 'Site updated successfully'}), 200
        
    except Exception as e:
        print(f"Error updating site: {str(e)}")
        return jsonify({'message': f"Error updating site: {str(e)}"}), 400
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/reports', methods=['GET'])
@jwt_required()
def get_report():
    report_type = request.args.get('type')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    div = request.args.get('div')
    status = request.args.get('status')
    
    print(f"Received report request - Type: {report_type}, DIV: {div}, Status: {status}")
    
    if not report_type:
        return jsonify({'message': 'Report type is required'}), 400
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'message': 'Database connection failed'}), 503
            
        cursor = conn.cursor(dictionary=True)
        
        # Build the base query with filters
        query = "SELECT * FROM rentdetails WHERE 1=1"
        params = []
        
        # Add DIV filter if provided and not 'ALL'
        if div and div != 'ALL':
            query += " AND `DIV` = %s"
            params.append(div)
            print(f"Added DIV filter: {div}")
        
        # Add Status filter if provided and not 'ALL'
        if status and status != 'ALL':
            query += " AND `STATUS` = %s"
            params.append(status)
            print(f"Added Status filter: {status}")
        
        # Add date range filter if provided
        if from_date and to_date:
            query += " AND `AGREEMENT DATE` BETWEEN %s AND %s"
            params.extend([from_date, to_date])
        
        print(f"Executing query: {query}")
        print(f"With parameters: {params}")
        
        cursor.execute(query, params)
        sites = cursor.fetchall()
        
        print(f"Found {len(sites)} matching records")
        
        if report_type == 'ALL SITES DATA REPORTS':
            data = []
            for site in sites:
                try:
                    record = {
                        'site_id': site['SITE'],
                        'store_name': site['STORE NAME'],
                        'region': site['REGION'],
                        'div': site['DIV'],
                        'manager': site['MANAGER'],
                        'asst_manager': site['ASST MANAGER'],
                        'executive': site['EXECUTIVE'],
                        'doo': format_date(site['D.O.O']),
                        'sqft': site['SQ.FT'],
                        'agreement_date': format_date(site['AGREEMENT DATE']),
                        'rent_position_date': format_date(site['RENT POSITION DATE']),
                        'rent_effective_date': format_date(site['RENT EFFECTIVE DATE']),
                        'lease_period': site['LEASE PERIOD'],
                        'rent_free_period_days': site['RENT FREE PERIOD DAYS'],
                        'rent_effective_amount': site['RENT EFFECTIVE AMOUNT'],
                        'present_rent': site['PRESENT RENT'],
                        'hike_percentage': site['HIKE %'],
                        'hike_year': site['HIKE YEAR'],
                        'rent_deposit': site['RENT DEPOSIT'],
                        'owner_name1': site['OWNER NAME-1'],
                        'gst_number': site['GST NUMBER'],
                        'pan_number': site['PAN NUMBER'],
                        'tds_percentage': site['TDS PERCENTAGE'],
                        'mature': site['MATURE'],
                        'status': site['STATUS'],
                        'remarks': site.get('REMARKS', '')
                    }
                    data.append(record)
                except Exception as e:
                    print(f"Error processing site {site.get('SITE', 'Unknown')}: {str(e)}")
                    continue
            
            print(f"Returning {len(data)} processed records")
            return jsonify({'data': data}), 200
            
    except Exception as e:
        print(f"Report generation error: {str(e)}")
        return jsonify({'message': f'Error generating report: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_excel():
    if 'file' not in request.files:
        return jsonify({'message': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'message': 'Invalid file format'}), 400
    
    conn = None
    cursor = None
    try:
        # Initialize database connection first
        conn = get_db_connection()
        if conn is None:
            return jsonify({'message': 'Database connection failed. Please try again later.'}), 503
            
        cursor = conn.cursor()
        
        # Read the Excel file
        df = pd.read_excel(file)
        
        # Define required fields with default values
        required_fields = {
            'SITE': None,
            'STORE NAME': None,
            'REGION': None,
            'DIV': None,
            'MANAGER': None,
            'ASST MANAGER': None,
            'EXECUTIVE': None,
            'D.O.O': None,
            'SQ.FT': 0,
            'AGREEMENT DATE': None,
            'RENT POSITION DATE': None,
            'RENT EFFECTIVE DATE': None,
            'LEASE PERIOD': 0,
            'RENT FREE PERIOD DAYS': 0,
            'RENT EFFECTIVE AMOUNT': 0,
            'PRESENT RENT': 0,
            'HIKE %': 0,
            'HIKE YEAR': 0,
            'RENT DEPOSIT': 0,
            'OWNER NAME-1': None,
            'GST NUMBER': 'NA',
            'PAN NUMBER': 'NA',
            'TDS PERCENTAGE': 0,
            'MATURE': 'NO',
            'STATUS': 'ACTIVE'
        }
        
        # Skip calculated fields
        skip_fields = ['CURRENT DATE 1', 'VALIDITY DATE']
        
        inserted_count = 0
        
        for _, row in df.iterrows():
            # Process each row...
            try:
                # Rest of your existing row processing code...
                site_id = str(row['SITE'])
                cursor.execute("SELECT COUNT(*) FROM rentdetails WHERE `SITE` = %s", (site_id,))
                count = cursor.fetchone()[0]
                
                if count > 0:
                    continue
                
                columns = []
                placeholders = []
                values = []
                
                # Process all required fields
                for field, default in required_fields.items():
                    value = row.get(field, default)
                    
                    # Handle empty values
                    if pd.isna(value) or value == '':
                        value = default
                    
                    # Skip if still None and field is required
                    if value is None:
                        raise ValueError(f"Missing required field: {field}")
                    
                    # Format column name for SQL
                    sql_col = f"`{field}`"
                    columns.append(sql_col)
                    placeholders.append('%s')
                    
                    # Handle date objects
                    if isinstance(value, pd.Timestamp):
                        value = value.to_pydatetime().date()
                    
                    values.append(value)
                
                # Build and execute the INSERT query
                column_names = ', '.join(columns)
                placeholder_str = ', '.join(placeholders)
                query = f"INSERT INTO rentdetails ({column_names}) VALUES ({placeholder_str})"
                cursor.execute(query, values)
                inserted_count += 1
                
            except Exception as row_error:
                print(f"Error processing row for site {site_id}: {str(row_error)}")
                continue
        
        conn.commit()
        return jsonify({
            'message': f'Data uploaded successfully. {inserted_count} new records inserted.'
        }), 200
        
    except ValueError as ve:
        print(f"Validation error: {str(ve)}")
        if conn:
            conn.rollback()
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        print(f"Upload error: {str(e)}")
        if conn:
            conn.rollback()
        return jsonify({'message': f'Error uploading data: {str(e)}'}), 400
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/search', methods=['GET'])
@jwt_required()
def search_sites():
    search_term = request.args.get('term', '')
    site_id_search = request.args.get('site_id_search', 'false') == 'true'
    
    # Get current date for calculations
    current_date = datetime.now().date()
    
    # Clean up search term
    search_term = search_term.strip().upper() if search_term else ''
    
    if not search_term:
        return jsonify({'message': 'Search term is required'}), 400
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'message': 'Database connection failed'}), 503
            
        cursor = conn.cursor(dictionary=True)
        
        if site_id_search:
            query = """
                SELECT 
                    `SITE` as site_id,
                    `SITE`,
                    `STORE NAME`,
                    `REGION`,
                    `DIV`,
                    `RENT POSITION DATE`,
                    `AGREEMENT VALID UPTO`,
                    `CURRENT DATE`,
                    `GST NUMBER`,
                    `PAN NUMBER`
                FROM rentdetails 
                WHERE `SITE` = %s
                LIMIT 1
            """
            cursor.execute(query, [search_term])
        else:
            search_pattern = f"%{search_term}%"
            query = """
                SELECT 
                    `SITE` as site_id,
                    `SITE`,
                    `STORE NAME`,
                    `REGION`,
                    `DIV`,
                    `RENT POSITION DATE`,
                    `AGREEMENT VALID UPTO`,
                    `CURRENT DATE`,
                    `GST NUMBER`,
                    `PAN NUMBER`
                FROM rentdetails 
                WHERE `SITE` LIKE %s 
                OR `STORE NAME` LIKE %s
                OR `REGION` LIKE %s
                LIMIT 50
            """
            cursor.execute(query, [search_pattern, search_pattern, search_pattern])
        
        results = cursor.fetchall()
        
        if not results:
            return jsonify({'message': 'No results found'}), 404
        
        processed_results = []
        for result in results:
            # Get required dates for calculations
            rent_position_date = result.get('RENT POSITION DATE')
            agreement_valid_upto = result.get('AGREEMENT VALID UPTO')
            
            site_data = {
                'site_id': result.get('site_id'),
                'SITE': result.get('SITE'),
                'STORE NAME': result.get('STORE NAME'),
                'REGION': result.get('REGION'),
                'DIV': result.get('DIV'),
                'GST NUMBER': result.get('GST NUMBER', ''),
                'PAN NUMBER': result.get('PAN NUMBER', '')
            }
            
            # Calculate CURRENT DATE 1 (time elapsed since RENT POSITION DATE)
            if rent_position_date:
                try:
                    # Convert rent position date to datetime
                    rpd = datetime.strptime(str(rent_position_date), '%Y-%m-%d').date()
                    
                    # Calculate the difference between current date and rent position date
                    diff = relativedelta(current_date, rpd)
                    
                    # Format as "X Years, Y Months, Z Days"
                    site_data['CURRENT DATE 1'] = (
                        f"{diff.years} {'Years' if diff.years != 1 else 'Year'}, "
                        f"{diff.months} {'Months' if diff.months != 1 else 'Month'}, "
                        f"{diff.days} {'Days' if diff.days != 1 else 'Day'}"
                    )
                except Exception as e:
                    print(f"Error calculating CURRENT DATE 1: {str(e)}")
                    site_data['CURRENT DATE 1'] = ''

            # Calculate VALIDITY DATE (time remaining until AGREEMENT VALID UPTO)
            if agreement_valid_upto:
                try:
                    # Convert agreement valid upto date to datetime
                    avu = datetime.strptime(str(agreement_valid_upto), '%Y-%m-%d').date()
                    
                    # Calculate the difference between agreement valid upto and current date
                    diff = relativedelta(avu, current_date)
                    
                    # Format as "X Years, Y Months, Z Days"
                    site_data['VALIDITY DATE'] = (
                        f"{diff.years} {'Years' if diff.years != 1 else 'Year'}, "
                        f"{diff.months} {'Months' if diff.months != 1 else 'Month'}, "
                        f"{diff.days} {'Days' if diff.days != 1 else 'Day'}"
                    )
                except Exception as e:
                    print(f"Error calculating VALIDITY DATE: {str(e)}")
                    site_data['VALIDITY DATE'] = ''

            processed_results.append(site_data)
        
        return jsonify({'results': processed_results}), 200
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({'message': f'Error during search: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def create_tables_if_needed():
    """Creates necessary database tables if they don't exist"""
    conn = None
    cursor = None
    try:
        # Create USERS table if it doesn't exist
        conn = get_db_connection()
        if conn is None:
            print("Failed to create tables: Database connection failed")
            return False
            
        cursor = conn.cursor()
        
        # Check if USERS table exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS USERS (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password VARCHAR(120) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'user'
        )
        """)
        conn.commit()

        # Create default admin user if not exists
        cursor.execute("SELECT COUNT(*) FROM USERS WHERE username = 'admin'")
        admin_exists = cursor.fetchone()[0]
        
        if not admin_exists:
            hashed = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
            "INSERT INTO USERS (username, password, role) VALUES (%s, %s, %s)",
                ('admin', hashed.decode('utf-8'), 'admin')
            )
            conn.commit()
        
        return True
    except Exception as e:
        print(f"Database initialization error: {str(e)}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
if __name__ == '__main__':
    # Don't try to connect to database at startup
    app.run(debug=True, host='0.0.0.0')
