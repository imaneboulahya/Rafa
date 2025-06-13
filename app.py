from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FileField, validators
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rafa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

# Models (unchanged)
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

class GroupProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), nullable=False)
    documents_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group_profile.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    passport = db.Column(db.String(50))

# Forms (unchanged)
class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[validators.InputRequired()])
    last_name = StringField('Last Name', validators=[validators.InputRequired()])
    phone = StringField('Phone', validators=[validators.InputRequired()])
    email = StringField('Email')
    nationality = StringField('Nationality', validators=[validators.InputRequired()])
    passport = StringField('Passport Number')
    cin = StringField('CIN')
    service_type = SelectField('Service Type', choices=[
        ('visa', 'Visa'),
        ('hotel', 'Hotel'),
        ('billet', 'Billet'),
        ('hajj', 'Hajj'),
        ('omra', 'Omra'),
        ('other', 'Other (Please specify)')
    ], validators=[validators.InputRequired()])
    custom_service = StringField('Custom Service')
    photo = FileField('Profile Photo')
    documents = FileField('Documents')

class GroupForm(FlaskForm):
    group_name = StringField('Group/Organization Name', validators=[validators.InputRequired()])
    group_documents = FileField('Group Documents')

# Routes
@app.route('/')
def index():
    return render_template('index.html', now=datetime.now())

@app.route('/visa')
def visa():
    search_query = request.args.get('search', '').strip()
    search_by = request.args.get('search_by', 'name')
    
    # Start with base query for visa clients
    query = Profile.query.filter_by(service_type='visa')
    
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
    
    visa_clients = query.order_by(Profile.service_completed, Profile.created_at.desc()).all()
    
    return render_template(
        'visa.html',
        clients=visa_clients,
        search_query=search_query,
        search_by=search_by
    )

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

@app.route('/update_client/<int:client_id>', methods=['POST'])
def update_client(client_id):
    client = Profile.query.get_or_404(client_id)
    client.amount_paid = float(request.form.get('amount_paid', 0))
    client.total_amount = float(request.form.get('total_amount', 0))
    client.service_completed = 'service_completed' in request.form
    db.session.commit()
    flash('Client updated successfully!', 'success')
    return redirect(url_for('visa'))

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

@app.route('/hotel')
def hotel():
    return render_template('hotel.html')

@app.route('/billet')
def billet():
    return render_template('billet.html')

@app.route('/hajj')
def hajj():
    return render_template('hajj.html')

@app.route('/omra')
def omra():
    return render_template('omra.html')

@app.route('/autocar')
def autocar():
    return render_template('autocar.html')

@app.route('/bateau')
def bateau():
    return render_template('bateau.html')

@app.route('/traduction')
def traduction():
    return render_template('traduction.html')

@app.route('/assurance')
def assurance():
    return render_template('assurance.html')

@app.route('/voyages')
def voyages():
    return render_template('voyages.html')

@app.route('/transfert')
def transfert():
    return render_template('transfert.html')

@app.route('/statistics')
def statistics():
    return render_template('statistics.html')

@app.route('/factures')
def factures():
    return render_template('factures.html')

@app.route('/create', methods=['GET', 'POST'])
def create_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        photo_filename = save_file(form.photo.data) if form.photo.data else None
        documents_filename = save_file(form.documents.data) if form.documents.data else None
        
        profile = Profile(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            email=form.email.data,
            nationality=form.nationality.data,
            passport=form.passport.data,
            cin=form.cin.data,
            service_type=form.service_type.data,
            custom_service=form.custom_service.data if form.service_type.data == 'other' else None,
            photo_path=photo_filename,
            documents_path=documents_filename,
            amount_paid=0.0,  # Initialize payment fields
            total_amount=0.0,
            service_completed=False
        )
        
        db.session.add(profile)
        db.session.commit()
        flash('Profile created successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('create_profile.html', form=form)

@app.route('/group', methods=['GET', 'POST'])
def create_group():
    form = GroupForm()
    if form.validate_on_submit():
        documents_filename = save_file(form.group_documents.data) if form.group_documents.data else None
        group = GroupProfile(
            group_name=form.group_name.data,
            documents_path=documents_filename
        )
        db.session.add(group)
        db.session.commit()
        flash('Group created successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('create_group.html', form=form)

def save_file(file):
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return filename
    return None

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)