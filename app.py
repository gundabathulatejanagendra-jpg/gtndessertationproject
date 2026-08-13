from flask import Flask, render_template, redirect, url_for, request, flash, session, send_file, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from database import db, User, Issue, StatusHistory, Feedback, Notification
from config import Config
import os, io

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def create_notification(user_id, message):
    notif = Notification(user_id=user_id, message=message)
    db.session.add(notif)
    db.session.commit()

#  INIT DB & DEFAULT ADMIN 
with app.app_context():
    db.create_all()
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            name='Admin Officer',
            email='admin@cityportal.com',
            password_hash=generate_password_hash('Admin@1234'),
            role='admin',
            phone='9999999999',
            area='City Hall'
        )
        db.session.add(admin)
        db.session.commit()

#  INDEX 
@app.route('/')
def index():
    total_issues = Issue.query.count()
    resolved = Issue.query.filter_by(status='Resolved').count() + Issue.query.filter_by(status='Closed').count()
    categories = ['Pothole', 'Streetlight', 'Garbage', 'Waterlogging', 'Other']
    return render_template('index.html', total_issues=total_issues, resolved=resolved, categories=categories)

#  AUTH 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('resident_dashboard') if current_user.role == 'resident' else url_for('admin_dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('resident_dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()
        area = request.form.get('area', '').strip()
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please log in.', 'warning')
            return redirect(url_for('login'))
        user = User(
            name=name, email=email,
            password_hash=generate_password_hash(password),
            role='resident', phone=phone, area=area
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

#  RESIDENT ROUTES 
@app.route('/resident/dashboard')
@login_required
def resident_dashboard():
    if current_user.role != 'resident':
        return redirect(url_for('admin_dashboard'))
    issues = Issue.query.filter_by(resident_id=current_user.id).order_by(Issue.created_at.desc()).all()
    total = len(issues)
    open_issues = sum(1 for i in issues if i.status not in ['Resolved', 'Closed'])
    resolved = sum(1 for i in issues if i.status in ['Resolved', 'Closed'])
    unread = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return render_template('resident/dashboard.html', issues=issues, total=total,
                           open_issues=open_issues, resolved=resolved, unread=unread)

@app.route('/resident/report', methods=['GET', 'POST'])
@login_required
def report_issue():
    if current_user.role != 'resident':
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '')
        location = request.form.get('location', '').strip()
        photo_path = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                photo_path = filename
        issue = Issue(
            resident_id=current_user.id,
            title=title, description=description,
            category=category, location_address=location,
            photo_path=photo_path
        )
        db.session.add(issue)
        db.session.commit()
        history = StatusHistory(issue_id=issue.id, old_status=None,
                                new_status='Submitted', changed_by=current_user.id,
                                note='Issue submitted by resident.')
        db.session.add(history)
        db.session.commit()
        flash('Your issue has been submitted successfully!', 'success')
        return redirect(url_for('resident_dashboard'))
    return render_template('resident/report.html')

@app.route('/resident/issue/<int:issue_id>')
@login_required
def resident_issue_detail(issue_id):
    if current_user.role != 'resident':
        return redirect(url_for('admin_dashboard'))
    issue = Issue.query.filter_by(id=issue_id, resident_id=current_user.id).first_or_404()
    history = StatusHistory.query.filter_by(issue_id=issue_id).order_by(StatusHistory.timestamp.asc()).all()
    return render_template('resident/issue_detail.html', issue=issue, history=history)

@app.route('/resident/feedback/<int:issue_id>', methods=['GET', 'POST'])
@login_required
def submit_feedback(issue_id):
    if current_user.role != 'resident':
        return redirect(url_for('admin_dashboard'))
    issue = Issue.query.filter_by(id=issue_id, resident_id=current_user.id).first_or_404()
    if issue.status not in ['Resolved', 'Closed']:
        flash('Feedback can only be submitted for resolved issues.', 'warning')
        return redirect(url_for('resident_issue_detail', issue_id=issue_id))
    existing = Feedback.query.filter_by(issue_id=issue_id, resident_id=current_user.id).first()
    if existing:
        flash('You have already submitted feedback for this issue.', 'info')
        return redirect(url_for('resident_issue_detail', issue_id=issue_id))
    if request.method == 'POST':
        rating = int(request.form.get('rating', 3))
        comment = request.form.get('comment', '').strip()
        fb = Feedback(issue_id=issue_id, resident_id=current_user.id, rating=rating, comment=comment)
        db.session.add(fb)
        issue.status = 'Closed'
        db.session.commit()
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('resident_dashboard'))
    return render_template('resident/feedback.html', issue=issue)

@app.route('/resident/notifications')
@login_required
def notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    for n in notifs:
        n.is_read = True
    db.session.commit()
    return render_template('resident/notifications.html', notifs=notifs)

@app.route('/api/unread-count')
@login_required
def unread_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})

#  ADMIN ROUTES 
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('resident_dashboard'))

    total = Issue.query.count()
    submitted = Issue.query.filter_by(status='Submitted').count()
    in_progress = Issue.query.filter_by(status='In Progress').count()
    resolved = Issue.query.filter(Issue.status.in_(['Resolved', 'Closed'])).count()

    recent = Issue.query.order_by(Issue.created_at.desc()).limit(10).all()

    now = datetime.utcnow()

    overdue = Issue.query.filter(
        Issue.status.notin_(['Resolved', 'Closed']),
        Issue.created_at < now - timedelta(days=7)
    ).count()

    avg_feedback = db.session.query(db.func.avg(Feedback.rating)).scalar()
    avg_feedback = round(avg_feedback, 1) if avg_feedback else 0

    return render_template(
        'admin/dashboard.html',
        total=total,
        submitted=submitted,
        in_progress=in_progress,
        resolved=resolved,
        recent=recent,
        overdue=overdue,
        avg_feedback=avg_feedback,
        now=now
    )

@app.route('/admin/issues')
@login_required
def admin_issues():
    if current_user.role != 'admin':
        return redirect(url_for('resident_dashboard'))
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    priority_filter = request.args.get('priority', '')
    search = request.args.get('search', '')
    query = Issue.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    if search:
        query = query.filter(Issue.title.ilike(f'%{search}%'))
    issues = query.order_by(Issue.created_at.desc()).all()
    now = datetime.utcnow()
    return render_template('admin/issues.html', issues=issues, now=now,
                           status_filter=status_filter, category_filter=category_filter,
                           priority_filter=priority_filter, search=search)

@app.route('/admin/issue/<int:issue_id>', methods=['GET', 'POST'])
@login_required
def admin_issue_detail(issue_id):
    if current_user.role != 'admin':
        return redirect(url_for('resident_dashboard'))
    issue = Issue.query.get_or_404(issue_id)
    if request.method == 'POST':
        new_status = request.form.get('status', issue.status)
        new_priority = request.form.get('priority', issue.priority)
        public_note = request.form.get('admin_note_public', '').strip()
        internal_note = request.form.get('admin_note_internal', '').strip()
        old_status = issue.status
        issue.status = new_status
        issue.priority = new_priority
        issue.admin_note_public = public_note
        issue.admin_note_internal = internal_note
        issue.updated_at = datetime.utcnow()
        if new_status in ['Resolved'] and not issue.resolved_at:
            issue.resolved_at = datetime.utcnow()
        history = StatusHistory(issue_id=issue.id, old_status=old_status,
                                new_status=new_status, changed_by=current_user.id,
                                note=public_note or internal_note)
        db.session.add(history)
        if old_status != new_status:
            create_notification(issue.resident_id,
                f'Your issue "{issue.title}" status changed to {new_status}.')
        db.session.commit()
        flash('Issue updated successfully.', 'success')
        return redirect(url_for('admin_issue_detail', issue_id=issue_id))
    history = StatusHistory.query.filter_by(issue_id=issue_id).order_by(StatusHistory.timestamp.asc()).all()
    feedback = Feedback.query.filter_by(issue_id=issue_id).first()
    return render_template('admin/issue_detail.html', issue=issue, history=history, feedback=feedback)

@app.route('/admin/analytics')
@login_required
def admin_analytics():
    if current_user.role != 'admin':
        return redirect(url_for('resident_dashboard'))
    categories = ['Pothole', 'Streetlight', 'Garbage', 'Waterlogging', 'Other']
    cat_counts = [Issue.query.filter_by(category=c).count() for c in categories]
    statuses = ['Submitted', 'Under Review', 'In Progress', 'Resolved', 'Closed']
    status_counts = [Issue.query.filter_by(status=s).count() for s in statuses]
    weekly_data = []
    weekly_labels = []
    for i in range(7, -1, -1):
        week_start = datetime.utcnow() - timedelta(weeks=i+1)
        week_end = datetime.utcnow() - timedelta(weeks=i)
        count = Issue.query.filter(Issue.created_at >= week_start, Issue.created_at < week_end).count()
        weekly_data.append(count)
        weekly_labels.append(week_start.strftime('%b %d'))
    avg_rating = db.session.query(db.func.avg(Feedback.rating)).scalar()
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    total_feedback = Feedback.query.count()
    return render_template('admin/analytics.html',
                           categories=categories, cat_counts=cat_counts,
                           statuses=statuses, status_counts=status_counts,
                           weekly_labels=weekly_labels, weekly_data=weekly_data,
                           avg_rating=avg_rating, total_feedback=total_feedback)

@app.route('/admin/export-pdf')
@login_required
def export_pdf():
    if current_user.role != 'admin':
        return redirect(url_for('resident_dashboard'))
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("Community Issue Portal - Analytics Report", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC", styles['Normal']))
    elements.append(Spacer(1, 12))
    total = Issue.query.count()
    resolved = Issue.query.filter(Issue.status.in_(['Resolved', 'Closed'])).count()
    elements.append(Paragraph(f"Total Issues Reported: {total}", styles['Normal']))
    elements.append(Paragraph(f"Total Resolved: {resolved}", styles['Normal']))
    elements.append(Spacer(1, 12))
    data = [['Category', 'Count']]
    for cat in ['Pothole', 'Streetlight', 'Garbage', 'Waterlogging', 'Other']:
        data.append([cat, Issue.query.filter_by(category=cat).count()])
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
                     download_name='analytics_report.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
