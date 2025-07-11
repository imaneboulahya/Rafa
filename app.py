from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FileField, DateField, FloatField, validators
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from wtforms.validators import InputRequired, Optional

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rafa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    nationality = db.Column(db.String(50), nullable=False)
    passport = db.Column(db.String(50))
    cin = db.Column(db.String(50))
    service_type = db.Column(db.String(50), nullable=False)
    custom_service = db.Column(db.String(100))
    photo_path = db.Column(db.String(200))
    documents_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_group = db.Column(db.Boolean, default=False)
    amount_paid = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    service_completed = db.Column(db.Boolean, default=False)
    
    # Autocar specific fields
    autocar_type = db.Column(db.String(50))
    seat_number = db.Column(db.String(20))
    departure_location = db.Column(db.String(100))
    arrival_location = db.Column(db.String(100))
    departure_date = db.Column(db.Date)
    arrival_date = db.Column(db.Date)
    bateau_type = db.Column(db.String(50))  # ferry, cruise, etc.
    bateau_company = db.Column(db.String(100))
    departure_port = db.Column(db.String(100))
    arrival_port = db.Column(db.String(100))
    departure_date_bateau = db.Column(db.Date)
    arrival_date_bateau = db.Column(db.Date)
    cabin_number = db.Column(db.String(20))
    assurance_type = db.Column(db.String(50))  # 'schengen' ou 'monde'
    assurance_company = db.Column(db.String(100))
    policy_number = db.Column(db.String(50))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    coverage_details = db.Column(db.Text)
    voyage_destination = db.Column(db.String(100))
    voyage_date_depart = db.Column(db.Date)
    voyage_date_retour = db.Column(db.Date)
    voyage_prix = db.Column(db.Float)
    voyage_statut = db.Column(db.String(20))
    university_name = db.Column(db.String(100))
    study_field = db.Column(db.String(100))
    service_type = db.Column(db.String(50), nullable=False)  # will be 'omra' for Omra clients
    departure_date = db.Column(db.Date)  # used for Omra departure
    arrival_date = db.Column(db.Date)    # used for Omra return
    amount_paid = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    service_completed = db.Column(db.Boolean, default=False)

# Forms
class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    phone = StringField('Phone', validators=[InputRequired()])
    email = StringField('Email')
    nationality = StringField('Nationality', validators=[InputRequired()])
    passport = StringField('Passport Number')
    cin = StringField('CIN')
    service_type = SelectField('Service Type', choices=[
        ('visa', 'Visa'),
        ('hotel', 'Hotel'),
        ('billet', 'Billet'),
        ('hajj', 'Hajj'),
        ('omra', 'Omra'),
        ('autocar', 'Autocar'),
        ('bateau', 'Bateau'),
        ('traduction', 'Traduction'),
        ('assurance', 'Assurance'),
        ('transfert', 'Transfert'),
        ('voyage', 'Voyage'),
        ('etudiant', 'Etudiant'),
        ('other', 'Other (Please specify)')
    ], validators=[InputRequired()])
    custom_service = StringField('Custom Service')
    photo = FileField('Profile Photo')
    documents = FileField('Documents')
    
    # Autocar specific fields (will be conditionally shown)
    autocar_type = SelectField('Autocar Type', choices=[
        ('', 'Select Type'),
        ('luxury', 'Luxury'),
        ('standard', 'Standard'),
        ('vip', 'VIP')
    ], validators=[Optional()])
    seat_number = StringField('Seat Number', validators=[Optional()])
    departure_location = StringField('Departure Location', validators=[Optional()])
    arrival_location = StringField('Destination', validators=[Optional()])
    departure_date = DateField('Departure Date', format='%Y-%m-%d', validators=[Optional()])
    arrival_date = DateField('Return Date', format='%Y-%m-%d', validators=[Optional()])
    
    # Payment fields
    total_amount = FloatField('Total Price (DH)', validators=[Optional()])
    amount_paid = FloatField('Amount Paid (DH)', default=0, validators=[Optional()])
    bateau_type = SelectField('Bateau Type', choices=[
        ('', 'Select Type'),
        ('ferry', 'Ferry'),
        ('cruise', 'Cruise'),
        ('speedboat', 'Speedboat')
    ], validators=[Optional()])
    bateau_company = StringField('Shipping Company', validators=[Optional()])
    departure_port = StringField('Departure Port', validators=[Optional()])
    arrival_port = StringField('Arrival Port', validators=[Optional()])
    departure_date_bateau = DateField('Departure Date', format='%Y-%m-%d', validators=[Optional()])
    arrival_date_bateau = DateField('Arrival Date', format='%Y-%m-%d', validators=[Optional()])
    cabin_number = StringField('Cabin/Seat Number', validators=[Optional()])
    assurance_type = SelectField('Assurance Type', choices=[
        ('', 'Select Type'),
        ('schengen', 'Assurance Schengen'),
        ('monde', 'Assurance Monde')
    ], validators=[Optional()])
    assurance_company = StringField('Insurance Company', validators=[Optional()])
    policy_number = StringField('Policy Number', validators=[Optional()])
    assurance_start_date = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    assurance_end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    coverage_details = StringField('Coverage Details', validators=[Optional()])

class HotelBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    hotel_name = db.Column(db.String(100))
    check_in_date = db.Column(db.Date)
    check_out_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    room_type = db.Column(db.String(50))
    booking_reference = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GroupProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), nullable=False)
    documents_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GroupForm(FlaskForm):
    group_name = StringField('Group Name', validators=[InputRequired()])
    group_documents = FileField('Group Documents')
    class Meta:
        csrf = False 

class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group_profile.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    passport = db.Column(db.String(50))

class Transfert(db.Model):
    __tablename__ = 'transferts'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    transfer_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_completed = db.Column(db.Boolean, default=False)
    
    # Relationship
    profile = db.relationship('Profile', backref=db.backref('transferts', lazy=True))

# In your forms.py (add to existing forms)
class TransfertForm(FlaskForm):
    from_location = StringField('From', validators=[InputRequired()])
    to_location = StringField('To', validators=[InputRequired()])
    transfer_date = DateField('Transfer Date', format='%Y-%m-%d', validators=[InputRequired()])
    total_amount = FloatField('Total Amount (DH)', validators=[InputRequired()])
    amount_paid = FloatField('Amount Paid (DH)', default=0.0)

# Routes
@app.route('/')
def index():
    return render_template('index.html', now=datetime.now())


@app.route('/visa')
def visa():
    search_query = request.args.get('search', '').strip()
    search_by = request.args.get('search_by', 'name')
    query = Profile.query.filter_by(service_type='visa')
    
    if search_query:
        if search_by == 'name':
            query = query.filter(db.or_(
                Profile.first_name.ilike(f'%{search_query}%'),
                Profile.last_name.ilike(f'%{search_query}%')
            ))
        elif search_by == 'passport':
            query = query.filter(Profile.passport.ilike(f'%{search_query}%'))
        elif search_by == 'phone':
            query = query.filter(Profile.phone.ilike(f'%{search_query}%'))
        elif search_by == 'nationality':
            query = query.filter(Profile.nationality.ilike(f'%{search_query}%'))
    
    visa_clients = query.order_by(Profile.service_completed, Profile.created_at.desc()).all()
    return render_template('visa.html', clients=visa_clients, search_query=search_query, search_by=search_by)

@app.route('/billet')
def billet():
    search_query = request.args.get('search', '').strip()
    search_by = request.args.get('search_by', 'name')
    
    query = Profile.query.filter_by(service_type='billet')
    
    if search_query:
        if search_by == 'name':
            query = query.filter(db.or_(
                Profile.first_name.ilike(f'%{search_query}%'),
                Profile.last_name.ilike(f'%{search_query}%')
            ))
        elif search_by == 'passport':
            query = query.filter(Profile.passport.ilike(f'%{search_query}%'))
        elif search_by == 'phone':
            query = query.filter(Profile.phone.ilike(f'%{search_query}%'))
        elif search_by == 'transport':
            query = query.filter(db.or_(
                Profile.transport_name.ilike(f'%{search_query}%'),
                Profile.departure_location.ilike(f'%{search_query}%'),
                Profile.arrival_location.ilike(f'%{search_query}%')
            ))
    
    billet_clients = query.order_by(Profile.service_completed, Profile.arrival_date).all()
    return render_template('billet.html', clients=billet_clients, search_query=search_query, search_by=search_by)

@app.route('/update_billet_client/<int:client_id>', methods=['POST'])
def update_billet_client(client_id):
    client = Profile.query.get_or_404(client_id)
    
    try:
        client.amount_paid = float(request.form.get('amount_paid', 0))
        client.total_amount = float(request.form.get('total_amount', 0))
        client.transport_type = request.form.get('transport_type')
        client.transport_name = request.form.get('transport_name')
        client.departure_location = request.form.get('departure_location')
        client.arrival_location = request.form.get('arrival_location')
        client.travel_date = datetime.strptime(request.form['travel_date'], '%Y-%m-%d')
        client.service_completed = 'service_completed' in request.form
        
        db.session.commit()
        flash('Billet client updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating billet client: {str(e)}', 'danger')
    
    return redirect(url_for('billet'))

@app.route('/delete_billet_client/<int:client_id>')
def delete_billet_client(client_id):
    client = Profile.query.get_or_404(client_id)
    
    try:
        db.session.delete(client)
        db.session.commit()
        flash('Billet client deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting billet client: {str(e)}', 'danger')
    
    return redirect(url_for('billet'))

@app.route('/clients')
def clients():
    search_query = request.args.get('search', '').strip()
    search_by = request.args.get('search_by', 'name')
    service_filter = request.args.get('service_type', 'all')
    
    query = Profile.query
    
    # Apply search filter
    if search_query:
        if search_by == 'name':
            query = query.filter(
                db.or_(
                    Profile.first_name.ilike(f'%{search_query}%'),
                    Profile.last_name.ilike(f'%{search_query}%')
                )
            )
        elif search_by == 'passport':
            query = query.filter(Profile.passport.ilike(f'%{search_query}%'))
        elif search_by == 'phone':
            query = query.filter(Profile.phone.ilike(f'%{search_query}%'))
        elif search_by == 'nationality':
            query = query.filter(Profile.nationality.ilike(f'%{search_query}%'))
    
    # Apply service type filter
    if service_filter != 'all':
        query = query.filter_by(service_type=service_filter)
    
    clients = query.order_by(Profile.created_at.desc()).all()
    
    service_types = [
        ('visa', 'Visa'),
        ('hotel', 'Hotel'),
        ('billet', 'Billet'),
        ('hajj', 'Hajj'),
        ('omra', 'Omra'),
        ('other', 'Other')
    ]
    
    return render_template(
        'clients.html',
        clients=clients,
        search_query=search_query,
        search_by=search_by,
        service_filter=service_filter,
        service_types=service_types
    )

@app.route('/client/<int:client_id>')
def client_detail(client_id):
    client = Profile.query.get_or_404(client_id)
    return render_template('client.html', client=client)

@app.route('/update_client/<int:client_id>', methods=['GET', 'POST'])
def update_client(client_id):
    client = Profile.query.get_or_404(client_id)
    
    if request.method == 'POST':
        # Handle form submission
        client.amount_paid = float(request.form.get('amount_paid', 0))
        client.total_amount = float(request.form.get('total_amount', 0))
        client.service_completed = 'service_completed' in request.form
        db.session.commit()
        flash('Client updated successfully!', 'success')
        return redirect(url_for('visa'))
    
    # For GET requests, show the edit form
    return render_template('update_client.html', client=client)

@app.route('/completed-visas')
def completed_visas():
    completed_clients = Profile.query.filter_by(
        service_type='visa',
        service_completed=True
    ).all()
    return render_template('completed_visas.html', clients=completed_clients)

@app.route('/delete_client/<int:client_id>')
def delete_client(client_id):
    client = Profile.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    flash('Client deleted successfully!', 'success')
    return redirect(url_for('visa'))

@app.route('/hotel', methods=['GET', 'POST'])
def hotel():
    search_query = request.args.get('search', '').strip()
    search_by = request.args.get('search_by', 'name')
    
    # Get profiles with hotel service and their bookings
    query = Profile.query.filter_by(service_type='hotel')
    
    if search_query:
        if search_by == 'name':
            query = query.filter(db.or_(
                Profile.first_name.ilike(f'%{search_query}%'),
                Profile.last_name.ilike(f'%{search_query}%')
            ))
        elif search_by == 'passport':
            query = query.filter(Profile.passport.ilike(f'%{search_query}%'))
        elif search_by == 'phone':
            query = query.filter(Profile.phone.ilike(f'%{search_query}%'))
        elif search_by == 'hotel':
            # Search in related hotel bookings
            query = query.join(HotelBooking).filter(
                HotelBooking.hotel_name.ilike(f'%{search_query}%')
            )
    
    clients = query.order_by(Profile.created_at.desc()).all()
    
    return render_template(
        'hotel.html',
        clients=clients,
        search_query=search_query,
        search_by=search_by
    )

@app.route('/add_hotel_booking/<int:profile_id>', methods=['GET', 'POST'])
def add_hotel_booking(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    
    if request.method == 'POST':
        try:
            booking = HotelBooking(
                profile_id=profile_id,
                hotel_name=request.form.get('hotel_name'),
                check_in_date=datetime.strptime(request.form['check_in_date'], '%Y-%m-%d'),
                check_out_date=datetime.strptime(request.form['check_out_date'], '%Y-%m-%d'),
                notes=request.form.get('notes'),
                room_type=request.form.get('room_type'),
                booking_reference=request.form.get('booking_reference')
            )
            db.session.add(booking)
            db.session.commit()
            flash('Hotel booking added successfully!', 'success')
            return redirect(url_for('hotel'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding booking: {str(e)}', 'danger')
    
    return render_template('add_hotel_booking.html', profile=profile)

@app.route('/update_hotel_booking/<int:booking_id>', methods=['POST'])
def update_hotel_booking(booking_id):
    booking = HotelBooking.query.get_or_404(booking_id)
    
    try:
        booking.hotel_name = request.form.get('hotel_name')
        booking.check_in_date = datetime.strptime(request.form['check_in_date'], '%Y-%m-%d')
        booking.check_out_date = datetime.strptime(request.form['check_out_date'], '%Y-%m-%d')
        booking.notes = request.form.get('notes')
        booking.room_type = request.form.get('room_type')
        booking.booking_reference = request.form.get('booking_reference')
        
        # Update payment in profile
        profile = booking.profile
        profile.amount_paid = float(request.form.get('amount_paid', 0))
        profile.total_amount = float(request.form.get('total_amount', 0))
        profile.service_completed = 'service_completed' in request.form
        
        db.session.commit()
        flash('Booking updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating booking: {str(e)}', 'danger')
    
    return redirect(url_for('hotel'))

@app.route('/update_hotel_client/<int:client_id>', methods=['POST'])
def update_hotel_client(client_id):
    client = Profile.query.get_or_404(client_id)
    
    try:
        # Get form data
        hotel_name = request.form.get('hotel_name')
        check_in_date_str = request.form.get('check_in_date')
        check_out_date_str = request.form.get('check_out_date')
        
        # Validate required fields
        if not all([hotel_name, check_in_date_str, check_out_date_str]):
            flash('Please fill all required fields', 'danger')
            return redirect(url_for('hotel'))
        
        # Convert dates
        try:
            check_in_date = datetime.strptime(check_in_date_str, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD', 'danger')
            return redirect(url_for('hotel'))
        
        # Update client record
        client.hotel_name = hotel_name
        client.check_in_date = check_in_date
        client.check_out_date = check_out_date
        client.hotel_notes = request.form.get('hotel_notes', '')
        
        # Update payment info
        client.amount_paid = float(request.form.get('amount_paid', 0))
        client.total_amount = float(request.form.get('total_amount', 0))
        client.service_completed = 'service_completed' in request.form
        
        db.session.commit()
        flash('Hotel booking updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating booking: {str(e)}', 'danger')
    
    return redirect(url_for('hotel'))

@app.route('/delete_hotel_client/<int:client_id>', methods=['POST'])
def delete_hotel_client(client_id):
    client = Profile.query.get_or_404(client_id)
    
    try:
        db.session.delete(client)
        db.session.commit()
        flash('Hotel booking deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting hotel booking: {str(e)}', 'danger')
    
    return redirect(url_for('hotel'))

@app.route('/hajj')
def hajj():
    search_query = request.args.get('search', '').strip()
    search_by = request.args.get('search_by', 'name')
    completed_filter = request.args.get('completed', 'false') == 'true'
    
    query = Profile.query.filter_by(service_type='hajj')
    
    if not completed_filter:
        query = query.filter(Profile.service_completed == False)
    
    if search_query:
        if search_by == 'name':
            query = query.filter(db.or_(
                Profile.first_name.ilike(f'%{search_query}%'),
                Profile.last_name.ilike(f'%{search_query}%')
            ))
        elif search_by == 'passport':
            query = query.filter(Profile.passport.ilike(f'%{search_query}%'))
        elif search_by == 'phone':
            query = query.filter(Profile.phone.ilike(f'%{search_query}%'))
        elif search_by == 'nationality':
            query = query.filter(Profile.nationality.ilike(f'%{search_query}%'))
    
    hajj_clients = query.order_by(Profile.departure_date).all()
    
    # Calculate statistics
    total_clients = len(hajj_clients)
    completed_clients = len([c for c in hajj_clients if c.service_completed])
    total_revenue = sum(c.total_amount for c in hajj_clients if c.total_amount)
    paid_amount = sum(c.amount_paid for c in hajj_clients if c.amount_paid)
    
    return render_template(
        'hajj.html',
        clients=hajj_clients,
        search_query=search_query,
        search_by=search_by,
        completed_filter=completed_filter,
        total_clients=total_clients,
        completed_clients=completed_clients,
        total_revenue=total_revenue,
        paid_amount=paid_amount
    )

@app.route('/update_hajj_client/<int:client_id>', methods=['POST'])
def update_hajj_client(client_id):
    client = Profile.query.get_or_404(client_id)
    
    try:
        client.amount_paid = float(request.form.get('amount_paid', 0))
        client.total_amount = float(request.form.get('total_amount', 0))
        client.service_completed = 'service_completed' in request.form
        
        # Handle Hajj specific dates
        if 'departure_date' in request.form and request.form['departure_date']:
            client.departure_date = datetime.strptime(request.form['departure_date'], '%Y-%m-%d')
        if 'arrival_date' in request.form and request.form['arrival_date']:
            client.arrival_date = datetime.strptime(request.form['arrival_date'], '%Y-%m-%d')
        
        db.session.commit()
        flash('Hajj client updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating Hajj client: {str(e)}', 'danger')
    
    return redirect(url_for('hajj'))

@app.route('/delete_hajj_client/<int:client_id>')
def delete_hajj_client(client_id):
    client = Profile.query.get_or_404(client_id)
    
    try:
        db.session.delete(client)
        db.session.commit()
        flash('Hajj client deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting Hajj client: {str(e)}', 'danger')
    
    return redirect(url_for('hajj'))

@app.route('/omra')
def omra():
    search_query = request.args.get('search', '').strip()
    search_by = request.args.get('search_by', 'name')
    completed_filter = request.args.get('completed', 'false') == 'true'
    
    query = Profile.query.filter_by(service_type='omra')
    
    if not completed_filter:
        query = query.filter(Profile.service_completed == False)
    
    if search_query:
        if search_by == 'name':
            query = query.filter(db.or_(
                Profile.first_name.ilike(f'%{search_query}%'),
                Profile.last_name.ilike(f'%{search_query}%')
            ))
        elif search_by == 'passport':
            query = query.filter(Profile.passport.ilike(f'%{search_query}%'))
        elif search_by == 'phone':
            query = query.filter(Profile.phone.ilike(f'%{search_query}%'))
        elif search_by == 'nationality':
            query = query.filter(Profile.nationality.ilike(f'%{search_query}%'))
    
    omra_clients = query.order_by(Profile.created_at.desc()).all()
    
    # Calculate statistics
    total_clients = len(omra_clients)
    completed_clients = len([c for c in omra_clients if c.service_completed])
    total_revenue = sum(c.total_amount for c in omra_clients if c.total_amount)
    paid_amount = sum(c.amount_paid for c in omra_clients if c.amount_paid)
    
    return render_template(
        'omra.html',
        clients=omra_clients,
        search_query=search_query,
        search_by=search_by,
        completed_filter=completed_filter,
        total_clients=total_clients,
        completed_clients=completed_clients,
        total_revenue=total_revenue,
        paid_amount=paid_amount
    )

@app.route('/update_omra_client/<int:client_id>', methods=['POST'])
def update_omra_client(client_id):
    client = Profile.query.get_or_404(client_id)
    
    try:
        client.amount_paid = float(request.form.get('amount_paid', 0))
        client.total_amount = float(request.form.get('total_amount', 0))
        client.service_completed = 'service_completed' in request.form
        
        # Handle Omra specific dates if needed
        if 'departure_date' in request.form and request.form['departure_date']:
            client.departure_date = datetime.strptime(request.form['departure_date'], '%Y-%m-%d')
        if 'arrival_date' in request.form and request.form['arrival_date']:
            client.arrival_date = datetime.strptime(request.form['arrival_date'], '%Y-%m-%d')
        
        db.session.commit()
        flash('Omra client updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating Omra client: {str(e)}', 'danger')
    
    return redirect(url_for('omra'))

@app.route('/delete_omra_client/<int:client_id>')
def delete_omra_client(client_id):
    client = Profile.query.get_or_404(client_id)
    
    try:
        db.session.delete(client)
        db.session.commit()
        flash('Omra client deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting Omra client: {str(e)}', 'danger')
    
    return redirect(url_for('omra'))

@app.route('/autocar')
def autocar():
    search_query = request.args.get('search', '').strip()
    search_by = request.args.get('search_by', 'name')
    
    query = Profile.query.filter_by(service_type='autocar')
    
    if search_query:
        if search_by == 'name':
            query = query.filter(db.or_(
                Profile.first_name.ilike(f'%{search_query}%'),
                Profile.last_name.ilike(f'%{search_query}%')
            ))
        elif search_by == 'phone':
            query = query.filter(Profile.phone.ilike(f'%{search_query}%'))
        elif search_by == 'departure':
            query = query.filter(Profile.departure_location.ilike(f'%{search_query}%'))
        elif search_by == 'destination':
            query = query.filter(Profile.arrival_location.ilike(f'%{search_query}%'))
    
    clients = query.order_by(Profile.departure_date, Profile.service_completed).all()
    return render_template('autocar.html', clients=clients, search_query=search_query, search_by=search_by)

@app.route('/update/autocar/<int:client_id>', methods=['POST'])
def update_autocar_client(client_id):
    client = Profile.query.get_or_404(client_id)
    
    try:
        client.amount_paid = float(request.form.get('amount_paid', 0))
        client.total_amount = float(request.form.get('total_amount', 0))
        client.service_completed = 'service_completed' in request.form
        
        # Update autocar specific fields if they exist in the form
        if 'departure_location' in request.form:
            client.departure_location = request.form['departure_location']
        if 'arrival_location' in request.form:
            client.arrival_location = request.form['arrival_location']
        if 'departure_date' in request.form:
            client.departure_date = datetime.strptime(request.form['departure_date'], '%Y-%m-%d')
        if 'arrival_date' in request.form:
            client.arrival_date = datetime.strptime(request.form['arrival_date'], '%Y-%m-%d') if request.form['arrival_date'] else None
        if 'autocar_type' in request.form:
            client.autocar_type = request.form['autocar_type']
        if 'seat_number' in request.form:
            client.seat_number = request.form['seat_number']
        
        db.session.commit()
        flash('Autocar client updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating autocar client: {str(e)}', 'danger')
    
    return redirect(url_for('autocar'))

@app.route('/delete/autocar/<int:client_id>')
def delete_autocar_client(client_id):
    client = Profile.query.get_or_404(client_id)
    
    try:
        db.session.delete(client)
        db.session.commit()
        flash('Autocar client deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting autocar client: {str(e)}', 'danger')
    
    return redirect(url_for('autocar'))

@app.route('/bateau')
def bateau():
    search_query = request.args.get('search', '').strip()
    search_by = request.args.get('search_by', 'name')
    query = Profile.query.filter_by(service_type='bateau')
    
    if search_query:
        if search_by == 'name':
            query = query.filter(db.or_(
                Profile.first_name.ilike(f'%{search_query}%'),
                Profile.last_name.ilike(f'%{search_query}%')
            ))
        elif search_by == 'passport':
            query = query.filter(Profile.passport.ilike(f'%{search_query}%'))
        elif search_by == 'phone':
            query = query.filter(Profile.phone.ilike(f'%{search_query}%'))
        elif search_by == 'nationality':
            query = query.filter(Profile.nationality.ilike(f'%{search_query}%'))
    
    bateau_clients = query.order_by(Profile.service_completed, Profile.created_at.desc()).all()
    return render_template('bateau.html', clients=bateau_clients, search_query=search_query, search_by=search_by)

@app.route('/update_bateau_client/<int:client_id>', methods=['POST'])
def update_bateau_client(client_id):
    client = Profile.query.get_or_404(client_id)
    
    try:
        client.amount_paid = float(request.form.get('amount_paid', 0))
        client.total_amount = float(request.form.get('total_amount', 0))
        client.service_completed = 'service_completed' in request.form
        
        db.session.commit()
        flash('Bateau client updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating bateau client: {str(e)}', 'danger')
    
    return redirect(url_for('bateau'))

@app.route('/delete_bateau_client/<int:client_id>')
def delete_bateau_client(client_id):
    client = Profile.query.get_or_404(client_id)
    
    try:
        db.session.delete(client)
        db.session.commit()
        flash('Bateau client deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting bateau client: {str(e)}', 'danger')
    
    return redirect(url_for('bateau'))

@app.route('/traduction')
def traduction():
    search_query = request.args.get('search', '').strip()
    search_by = request.args.get('search_by', 'name')
    
    # Base query for traduction clients
    query = Profile.query.filter_by(service_type='traduction')
    
    # Apply search filters
    if search_query:
        if search_by == 'name':
            query = query.filter(db.or_(
                Profile.first_name.ilike(f'%{search_query}%'),
                Profile.last_name.ilike(f'%{search_query}%')
            ))
        elif search_by == 'phone':
            query = query.filter(Profile.phone.ilike(f'%{search_query}%'))
        elif search_by == 'language':
            query = query.filter(db.or_(
                Profile.translation_language_from.ilike(f'%{search_query}%'),
                Profile.translation_language_to.ilike(f'%{search_query}%')
            ))
    
    # Get clients ordered by completion status and date
    clients = query.order_by(Profile.service_completed, Profile.created_at.desc()).all()
    
    return render_template('traduction.html', 
                         clients=clients,
                         search_query=search_query,
                         search_by=search_by)

@app.route('/update_traduction_client/<int:client_id>', methods=['POST'])
def update_traduction_client(client_id):
    client = Profile.query.get_or_404(client_id)
    
    try:
        # Update completion status
        client.service_completed = 'service_completed' in request.form
        
        # Handle document upload if provided
        if 'translation_docs' in request.files:
            file = request.files['translation_docs']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                client.translation_docs_path = filename
        
        db.session.commit()
        flash('Client updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating client: {str(e)}', 'danger')
    
    return redirect(url_for('traduction'))

@app.route('/delete_traduction_client/<int:client_id>')
def delete_traduction_client(client_id):
    client = Profile.query.get_or_404(client_id)
    
    try:
        # Delete associated documents if they exist
        if client.translation_docs_path:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], client.translation_docs_path))
            except:
                pass
        
        db.session.delete(client)
        db.session.commit()
        flash('Client deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting client: {str(e)}', 'danger')
    
    return redirect(url_for('traduction'))

@app.route('/assurance')
def assurance():
    search_query = request.args.get('search', '').strip()
    search_by = request.args.get('search_by', 'name')
    
    query = Profile.query.filter_by(service_type='assurance')
    
    if search_query:
        if search_by == 'name':
            query = query.filter(db.or_(
                Profile.first_name.ilike(f'%{search_query}%'),
                Profile.last_name.ilike(f'%{search_query}%')
            ))
        elif search_by == 'policy':
            query = query.filter(Profile.policy_number.ilike(f'%{search_query}%'))
        elif search_by == 'company':
            query = query.filter(Profile.assurance_company.ilike(f'%{search_query}%'))
    
    clients = query.order_by(Profile.service_completed, Profile.start_date).all()
    return render_template('assurance.html', 
                         clients=clients,
                         search_query=search_query,
                         search_by=search_by)

@app.route('/voyage')
def voyage():
    search_query = request.args.get('search', '').strip()
    statut_filter = request.args.get('statut', 'tous')
    
    query = Profile.query.filter_by(service_type='voyage')
    
    if statut_filter != 'tous':
        query = query.filter(Profile.voyage_statut == statut_filter)
    
    if search_query:
        query = query.filter(
            db.or_(
                Profile.first_name.ilike(f'%{search_query}%'),
                Profile.last_name.ilike(f'%{search_query}%'),
                Profile.phone.ilike(f'%{search_query}%'),
                Profile.voyage_destination.ilike(f'%{search_query}%')
            )
        )
    
    voyages = query.order_by(Profile.voyage_date_depart).all()
    
    return render_template(
        'voyage.html',
        voyages=voyages,
        search_query=search_query,
        statut_filter=statut_filter
    )

# Route pour mettre à jour un voyage
@app.route('/update_voyage/<int:voyage_id>', methods=['POST'])
def update_voyage(voyage_id):
    voyage = Profile.query.get_or_404(voyage_id)
    
    try:
        voyage.voyage_destination = request.form['destination']
        voyage.voyage_date_depart = datetime.strptime(request.form['date_depart'], '%Y-%m-%d')
        voyage.voyage_date_retour = datetime.strptime(request.form['date_retour'], '%Y-%m-%d')
        voyage.voyage_prix = float(request.form['prix'])
        voyage.voyage_statut = request.form['statut']
        
        db.session.commit()
        flash('Voyage mis à jour avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la mise à jour: {str(e)}', 'danger')
    
    return redirect(url_for('voyage'))

@app.route('/delete_voyage/<int:voyage_id>')
def delete_voyage(voyage_id):
    voyage = Profile.query.get_or_404(voyage_id)
    try:
        db.session.delete(voyage)
        db.session.commit()
        flash('Voyage supprimé avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'danger')
    return redirect(url_for('voyage'))

@app.route('/transfert')
def transfert():
    search_query = request.args.get('search', '').strip()
    completed = request.args.get('completed', 'false') == 'true'
    
    # Get all Profile records with service_type='transfert'
    query = Profile.query.filter_by(service_type='transfert')
    
    if not completed:
        query = query.filter(Profile.service_completed == False)
    
    if search_query:
        query = query.filter(
            db.or_(
                Profile.first_name.ilike(f'%{search_query}%'),
                Profile.last_name.ilike(f'%{search_query}%'),
                Profile.phone.ilike(f'%{search_query}%')
            )
        )
    
    clients = query.order_by(Profile.created_at.desc()).all()
    
    # Convert Profile objects to a format that matches your template expectations
    transfers = []
    for client in clients:
        transfers.append({
            'profile': client,
            'from_location': "Default From",  # You should store this in your Profile model
            'to_location': "Default To",      # You should store this in your Profile model
            'transfer_date': datetime.utcnow().date(),  # You should store this in your Profile model
            'is_completed': client.service_completed,
            'amount_paid': client.amount_paid,
            'total_amount': client.total_amount,
            'id': client.id  # Needed for update/delete operations
        })
    
    return render_template(
        'transfert.html',
        transfers=transfers,
        search_query=search_query,
        completed=completed
    )

@app.route('/transfert/<int:transfer_id>', methods=['POST'])
def update_transfert(transfer_id):
    transfer = Transfert.query.get_or_404(transfer_id)
    transfer.amount_paid = float(request.form.get('amount_paid', 0))
    transfer.total_amount = float(request.form.get('total_amount', 0))
    transfer.is_completed = 'is_completed' in request.form
    db.session.commit()
    flash('Transfer updated successfully!', 'success')
    return redirect(url_for('transfert'))

@app.route('/transfert/delete/<int:transfer_id>')
def delete_transfert(transfer_id):
    transfer = Transfert.query.get_or_404(transfer_id)
    db.session.delete(transfer)
    db.session.commit()
    flash('Transfer deleted successfully!', 'success')
    return redirect(url_for('transfert'))

@app.route('/statistics')
def statistics():
    """Generate statistics for client progress throughout the year"""
    # Get current year
    current_year = datetime.now().year
    
    # Monthly client counts
    monthly_counts = db.session.query(
        db.func.strftime('%m', Profile.created_at).label('month'),
        db.func.count(Profile.id).label('count')
    ).filter(
        db.func.strftime('%Y', Profile.created_at) == str(current_year)
    ).group_by('month').all()
    
    # Convert to dictionary for easier processing
    monthly_data = {int(month): count for month, count in monthly_counts}
    
    # Fill in missing months with 0
    complete_monthly_data = [
        monthly_data.get(month, 0) for month in range(1, 13)
    ]
    
    # Service type distribution
    service_distribution = db.session.query(
        Profile.service_type,
        db.func.count(Profile.id).label('count')
    ).group_by(Profile.service_type).all()
    
    # Completion rates
    total_clients = db.session.query(Profile).count()
    completed_clients = db.session.query(Profile).filter_by(service_completed=True).count()
    completion_rate = (completed_clients / total_clients * 100) if total_clients > 0 else 0
    
    # Revenue statistics
    revenue_stats = {
        'total': db.session.query(db.func.sum(Profile.total_amount)).scalar() or 0,
        'paid': db.session.query(db.func.sum(Profile.amount_paid)).scalar() or 0,
        'pending': db.session.query(
            db.func.sum(Profile.total_amount - Profile.amount_paid)
        ).scalar() or 0
    }
    
    # Top services - FIXED THIS SECTION
    top_services = db.session.query(
        Profile.service_type,
        db.func.count(Profile.id).label('count')
    ).group_by(Profile.service_type) \
     .order_by(db.desc('count')) \
     .limit(5).all()
    
    # Recent clients
    recent_clients = db.session.query(Profile) \
        .order_by(Profile.created_at.desc()) \
        .limit(5).all()
    
    return render_template('statistics.html',
                         monthly_data=complete_monthly_data,
                         service_distribution=service_distribution,
                         completion_rate=round(completion_rate, 2),
                         revenue_stats=revenue_stats,
                         top_services=top_services,
                         recent_clients=recent_clients,
                         current_year=current_year,
                         total_clients=total_clients,
                         completed_clients=completed_clients)

@app.route('/etudiant')
def etudiant():
    search_query = request.args.get('search', '').strip()
    search_by = request.args.get('search_by', 'name')
    query = Profile.query.filter_by(service_type='etudiant')
    
    if search_query:
        if search_by == 'name':
            query = query.filter(db.or_(
                Profile.first_name.ilike(f'%{search_query}%'),
                Profile.last_name.ilike(f'%{search_query}%')
            ))
        elif search_by == 'passport':
            query = query.filter(Profile.passport.ilike(f'%{search_query}%'))
        elif search_by == 'phone':
            query = query.filter(Profile.phone.ilike(f'%{search_query}%'))
        elif search_by == 'nationality':
            query = query.filter(Profile.nationality.ilike(f'%{search_query}%'))
        elif search_by == 'university':
            query = query.filter(Profile.university_name.ilike(f'%{search_query}%'))
    
    clients = query.order_by(Profile.service_completed, Profile.created_at.desc()).all()
    return render_template('etudiant.html', 
                         clients=clients, 
                         search_query=search_query, 
                         search_by=search_by)

@app.route('/update_etudiant_client/<int:client_id>', methods=['POST'])
def update_etudiant_client(client_id):
    client = Profile.query.get_or_404(client_id)
    
    try:
        client.amount_paid = float(request.form.get('amount_paid', 0))
        client.total_amount = float(request.form.get('total_amount', 0))
        client.university_name = request.form.get('university_name', '')
        client.study_field = request.form.get('study_field', '')
        client.service_completed = 'service_completed' in request.form
        
        db.session.commit()
        flash('Student client updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating student client: {str(e)}', 'danger')
    
    return redirect(url_for('etudiant'))

@app.route('/delete_etudiant_client/<int:client_id>')
def delete_etudiant_client(client_id):
    client = Profile.query.get_or_404(client_id)
    
    try:
        db.session.delete(client)
        db.session.commit()
        flash('Student client deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting student client: {str(e)}', 'danger')
    
    return redirect(url_for('etudiant'))

@app.route('/create', methods=['GET', 'POST'])
def create_profile():
    form = ProfileForm()
    
    if request.method == 'GET' and 'service_type' in request.args:
        form.service_type.data = request.args.get('service_type')
    
    if form.validate_on_submit():
        try:
            # Common fields for all service types
            profile_data = {
                'first_name': form.first_name.data,
                'last_name': form.last_name.data,
                'phone': form.phone.data,
                'email': form.email.data,
                'nationality': form.nationality.data,
                'passport': form.passport.data,
                'cin': form.cin.data,
                'service_type': form.service_type.data,
                'custom_service': form.custom_service.data if form.service_type.data == 'other' else None,
                'amount_paid': float(form.amount_paid.data or 0),
                'total_amount': float(form.total_amount.data or 0),
                'service_completed': False,
                'created_at': datetime.utcnow()
            }
            
            # Handle file uploads
            if form.photo.data:
                filename = secure_filename(form.photo.data.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                form.photo.data.save(file_path)
                profile_data['photo_path'] = filename
            
            if form.documents.data:
                filename = secure_filename(form.documents.data.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                form.documents.data.save(file_path)
                profile_data['documents_path'] = filename
            
            # Create profile
            profile = Profile(**profile_data)
            db.session.add(profile)
            db.session.flush()  # Assigns ID without committing
            
            # SPECIAL HANDLING FOR TRANSFERT
            if form.service_type.data == 'transfert':
                transfer = Transfert(
                    profile_id=profile.id,
                    from_location="Location 1",  # Set default or get from form
                    to_location="Location 2",    # Set default or get from form
                    transfer_date=datetime.utcnow().date(),
                    total_amount=float(form.total_amount.data or 0),
                    amount_paid=float(form.amount_paid.data or 0)
                )
                db.session.add(transfer)
            
            db.session.commit()
            
            flash('Profile created successfully!', 'success')
            return redirect(url_for('transfert' if form.service_type.data == 'transfert' else 'clients'))
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating profile: {str(e)}', 'danger')
    
    return render_template('create_profile.html', form=form)

@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    form = GroupForm()
    
    if request.method == 'POST':
        try:
            # Handle group creation
            group_name = form.group_name.data
            documents = form.group_documents.data
            
            # Save group
            group = GroupProfile(
                group_name=group_name,
                documents_path=save_file(documents) if documents else None
            )
            db.session.add(group)
            db.session.flush()  # Get the group ID
            
            # Handle selected members
            member_ids = request.form.getlist('group_members[]')
            for member_id in member_ids:
                member = Profile.query.get(member_id)
                if member:
                    group_member = GroupMember(
                        group_id=group.id,
                        first_name=member.first_name,
                        last_name=member.last_name,
                        phone=member.phone,
                        passport=member.passport
                    )
                    db.session.add(group_member)
            
            db.session.commit()
            flash('Group created successfully!', 'success')
            return redirect(url_for('clients'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating group: {str(e)}', 'danger')
    
    return render_template('create_group.html', form=form)

@app.route('/search_clients')
def search_clients():
    search_term = request.args.get('q', '').strip()
    
    if not search_term:
        return {'results': []}  # Return empty if no search term
    
    try:
        # Search by name or phone number
        clients = Profile.query.filter(
            db.or_(
                db.func.concat(Profile.first_name, ' ', Profile.last_name).ilike(f'%{search_term}%'),
                Profile.phone.ilike(f'%{search_term}%')
            )
        ).limit(10).all()
        
        # Format results for Select2
        results = [{
            'id': client.id,
            'text': f"{client.first_name} {client.last_name} - {client.phone}"
        } for client in clients]
        
        return {'results': results}
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        return {'results': []}
    
@app.route('/groups')
def groups():
    """Display all groups with search functionality"""
    search_query = request.args.get('search', '').strip()
    
    # Start with base query
    query = GroupProfile.query
    
    # Apply search filter if provided
    if search_query:
        query = query.filter(GroupProfile.group_name.ilike(f'%{search_query}%'))
    
    # Get groups ordered by creation date (newest first)
    groups = query.order_by(GroupProfile.created_at.desc()).all()
    
    # Get member counts for each group
    groups_with_counts = []
    for group in groups:
        member_count = db.session.query(GroupMember).filter_by(group_id=group.id).count()
        groups_with_counts.append({
            'group': group,
            'member_count': member_count
        })
    
    return render_template('groups.html', 
                         groups=groups_with_counts, 
                         search_query=search_query)

@app.route('/delete_group/<int:group_id>')
def delete_group(group_id):
    """Delete a group and all its members"""
    group = GroupProfile.query.get_or_404(group_id)
    
    try:
        # Delete all members first
        GroupMember.query.filter_by(group_id=group_id).delete()
        
        # Then delete the group
        db.session.delete(group)
        db.session.commit()
        flash('Group deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting group: {str(e)}', 'danger')
    
    return redirect(url_for('groups'))

@app.route('/group/<int:group_id>', methods=['GET', 'POST'])
def group_detail(group_id):
    group = GroupProfile.query.get_or_404(group_id)
    members = GroupMember.query.filter_by(group_id=group_id).all()
    
    # Enrich member data with profile information if available
    member_details = []
    for member in members:
        profile = Profile.query.filter(
            db.and_(
                Profile.first_name == member.first_name,
                Profile.last_name == member.last_name,
                Profile.phone == member.phone
            )
        ).first()
        
        member_details.append({
            'member': member,
            'profile': profile
        })
    
    return render_template('group_detail.html', 
                         group=group, 
                         members=member_details)

@app.route('/update_group/<int:group_id>', methods=['POST'])
def update_group(group_id):
    """Handle group updates"""
    group = GroupProfile.query.get_or_404(group_id)
    
    try:
        # Update group name from form data
        if 'group_name' in request.form:
            group.group_name = request.form['group_name']
        
        # Handle document upload if provided
        if 'group_documents' in request.files:
            file = request.files['group_documents']
            if file.filename != '':
                # Delete old document if exists
                if group.documents_path:
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], group.documents_path))
                    except:
                        pass
                
                # Save new document
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                group.documents_path = filename
        
        db.session.commit()
        flash('Group updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating group: {str(e)}', 'danger')
    
    return redirect(url_for('group_detail', group_id=group_id))

@app.route('/add_group_member/<int:group_id>', methods=['POST'])
def add_group_member(group_id):
    """Add a new member to a group"""
    group = GroupProfile.query.get_or_404(group_id)
    
    try:
        # Create new group member from form data
        member = GroupMember(
            group_id=group_id,
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            phone=request.form['phone'],
            passport=request.form.get('passport', '')  # Optional field
        )
        
        db.session.add(member)
        db.session.commit()
        flash('Member added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding member: {str(e)}', 'danger')
    
    return redirect(url_for('group_detail', group_id=group_id))

@app.route('/delete_group_member/<int:member_id>')
def delete_group_member(member_id):
    """Remove a member from a group"""
    member = GroupMember.query.get_or_404(member_id)
    group_id = member.group_id  # Remember group_id before deletion
    
    try:
        db.session.delete(member)
        db.session.commit()
        flash('Member removed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing member: {str(e)}', 'danger')
    
    return redirect(url_for('group_detail', group_id=group_id))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)