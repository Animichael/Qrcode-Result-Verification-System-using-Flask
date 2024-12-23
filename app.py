from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from functools import wraps
from datetime import datetime, timedelta
import bcrypt
import secrets
from flask_sqlalchemy import SQLAlchemy
import random
import uuid


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.permanent_session_lifetime = timedelta(minutes=3)

# Mock admin credentials (In production, use database)
ADMIN_EMAIL = "admin@fpn.com"
ADMIN_PASSWORD = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())

# short code for departments
DEPARTMENT_CODES = {
    'Computer Science': 'CMP',
    'Statistics': 'STA',
    'Mathematics': 'MTH',
    'Accountancy': 'ACC',
    'Business Administration': 'BUS',
    'Office Technology': 'OTM',
    'Architecture': 'ARC',
    'Building Technology': 'BLD',
    'Quantity Surveying': 'QTS',
    'Estate Management': 'EST',
    'Surveying and Geo-Informatics': 'SGI',
    'Urban and Regional Planning': 'URP',
    'Agricultural Technology': 'AGT',
    'Agricultural Engineering': 'AGE',
    'Mechanical Engineering': 'MEC',
    'Electrical Engineering': 'ELE',
    'Civil Engineering': 'CIV',
    'Chemical Engineering': 'CHE',
    'Science Laboratory Technology': 'SLT',
    'Food Technology': 'FTH',
    'Hospitality Management': 'HMT',
    'Mass Communication': 'MAC',
    'Library and Information Science': 'LIS'
}

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fpn.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Faculty Model
class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.String(10), unique=True, nullable=False)
    faculty_name = db.Column(db.String(100), nullable=False)
    dean_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'faculty_id': self.faculty_id,
            'faculty_name': self.faculty_name,
            'dean_name': self.dean_name,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }

# Department Model
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(100), nullable=False, unique=True)
    hod_name = db.Column(db.String(100), nullable=False)
    hod_email = db.Column(db.String(100), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    faculty = db.relationship('Faculty', backref='departments') 
    programs = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'department_name': self.department_name,
            'hod_name': self.hod_name,
            'hod_email': self.hod_email,
            'faculty_id': self.faculty_id,
            'faculty_name': self.faculty.faculty_name if self.faculty else None,  
            'programs': self.programs,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }


# Student Model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matric_number = db.Column(db.String(20), unique=True, nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    othernames = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    level = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    faculty = db.relationship('Faculty', backref='students')
    department = db.relationship('Department', backref='students')
    
    def to_dict(self):
        return {
            'id': self.id,
            'matric_number': self.matric_number,
            'surname': self.surname,
            'othernames': self.othernames,
            'email': self.email,
            'faculty_id': self.faculty_id,
            'department_id': self.department_id,
            'faculty_name': self.faculty.faculty_name if self.faculty else 'N/A',
            'department_name': self.department.department_name if self.department else 'N/A',
            'level': self.level,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }


# Result Model
class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matric_number = db.Column(db.String(20), nullable=False)
    student_name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    programme = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='generated')  # generated, printed
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'matric_number': self.matric_number,
            'student_name': self.student_name,
            'department': self.department,
            'programme': self.programme,
            'grade': self.grade,
            'cgpa': self.cgpa,
            'status': self.status,
            'content': f"This is to certify that <strong>{self.student_name}</strong> with the Regno(<strong>{self.matric_number}</strong>), having completed an approved course of study and passed the prescribed examinations, has, by the authority of the Academic Board, been awarded the {self.programme} of the Federal Polytechnic, Nasarawa in <strong>{self.department}</strong> with a grade of <strong>{self.grade}</strong>, <strong>{self.cgpa}</strong> CGPA in {datetime.now().year} Academic Session. The effective date of the award is {self.created_at.strftime('%d/%m/%Y')}. The certificate will be issued in due course.",
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


# Verified Result Model
class VerifiedResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matric_number = db.Column(db.String(20), nullable=False)
    student_name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    verification_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='verified')
    
    def to_dict(self):
        return {
            'id': self.id,
            'matric_number': self.matric_number,
            'student_name': self.student_name,
            'department': self.department,
            'grade': self.grade,
            'cgpa': self.cgpa,
            'verification_date': self.verification_date.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status
        }
    



# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('index'))
        session.modified = True  # Reset session timer
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/login', methods=['POST'])
def admin_login():
    email = request.form.get('email')
    password = request.form.get('password')

    if email == ADMIN_EMAIL and bcrypt.checkpw(password.encode('utf-8'), ADMIN_PASSWORD):
        session.permanent = True
        session['admin_id'] = email
        session['last_activity'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({'success': True, 'message': 'Login successful!'})
    return jsonify({'success': False, 'message': 'Invalid credentials!'})


# route
#####################################################################################################
#dashbaord route
@app.route('/dashboard')
@login_required
def dashboard():
    faculties = Faculty.query.count()
    department_count = Department.query.count()
    total_students = Student.query.count()
    content = render_template('dashboard_content.html',
                              faculties=faculties,
                              department_count=department_count,
                              total_students=total_students
                              
                              )
    return render_template('dashboard.html', content=content, active_page='dashboard')

   


#################################################################################
# Everything about student registration
################################################################################
@app.route('/dashboard/register-student')
@login_required
def register_student():
    faculties = Faculty.query.all()
    content = render_template('register_student.html', faculties=faculties)
    return render_template('dashboard.html', content=content, active_page='register_student')

@app.route('/api/student/add', methods=['POST'])
@login_required
def add_student():
    try:
        data = request.form
        
        # Get department name
        department = Department.query.get(data.get('department_id'))
        if not department:
            return jsonify({'success': False, 'message': 'Invalid department'}), 400
            
        # Get department code
        dept_code = DEPARTMENT_CODES.get(department.department_name, 'GEN')  # GEN as fallback
        
        # Generate unique matric number
        year = datetime.now().year
        last_student = Student.query.filter(
            Student.matric_number.like(f'FPN/{year}/{dept_code}/%')
        ).order_by(Student.id.desc()).first()
        
        if last_student:
            last_number = int(last_student.matric_number.split('/')[-1])
            seq_num = f"{(last_number + 1):03d}"
        else:
            seq_num = "001"
            
        matric_number = f"FPN/{year}/{dept_code}/{seq_num}"
        
        # Check if matric number already exists
        if Student.query.filter_by(matric_number=matric_number).first():
            return jsonify({'success': False, 'message': 'Matric number already exists'}), 400
        
        new_student = Student(
            matric_number=matric_number,
            surname=data.get('surname'),
            othernames=data.get('othernames'),
            email=data.get('email'),
            faculty_id=data.get('faculty_id'),
            department_id=data.get('department_id'),
            level=data.get('level'),
            status='active'
        )
        
        db.session.add(new_student)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Student registered successfully',
            'student': new_student.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/student/list', methods=['GET'])
@login_required
def get_student_list():
    try:
        students = Student.query.all()
        return jsonify({
            'success': True,
            'data': [student.to_dict() for student in students]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500



@app.route('/api/student/delete/<int:id>', methods=['POST'])
@login_required
def delete_student(id):
    try:
        student = Student.query.get_or_404(id)
        db.session.delete(student)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Student deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
####################################Student registration ends here#################################




#####################################################################################
# Everything about faculty
#####################################################################################
# Main faculty dashboard route
@app.route('/dashboard/faculty')
@login_required
def faculty():
    faculties = Faculty.query.all()
    content = render_template('faculty.html', faculties=faculties)
    return render_template('dashboard.html', content=content, active_page='faculty')

# API routes for faculty CRUD operations
@app.route('/api/faculty/list', methods=['GET'])
@login_required
def get_faculty_list():
    try:
        faculties = Faculty.query.all()
        print(f"Loading faculties: {[f.faculty_name for f in faculties]}")
        return jsonify({
            'success': True,
            'data': [faculty.to_dict() for faculty in faculties]
        })
    except Exception as e:
        print(f"Error loading faculties: {str(e)}") 
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/faculty/add', methods=['POST'])
@login_required
def add_faculty():
    try:
        data = request.form
        # Generate unique faculty ID
        faculty_id = 'FPN' + ''.join([str(random.randint(0, 9)) for _ in range(5)])
        
        new_faculty = Faculty(
            faculty_id=faculty_id,
            faculty_name=data.get('facultyName'),
            dean_name=data.get('deanName'),
            description=data.get('description'),
            status=data.get('status', 'active')
        )
        
        db.session.add(new_faculty)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Faculty added successfully',
            'faculty': new_faculty.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        print('Error:', str(e))  
        return jsonify({'success': False, 'message': str(e)}), 500



@app.route('/api/faculty/edit/<int:id>', methods=['GET'])
@login_required
def get_faculty(id):
    try:
        faculty = Faculty.query.get_or_404(id)
        return jsonify({
            'success': True,
            'faculty': faculty.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/faculty/update/<int:id>', methods=['POST'])
@login_required
def update_faculty(id):
    try:
        faculty = Faculty.query.get_or_404(id)
        data = request.form
        
        faculty.faculty_name = data.get('facultyName')
        faculty.dean_name = data.get('deanName')
        faculty.description = data.get('description')
        faculty.status = data.get('status')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'faculty': faculty.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/faculty/delete/<int:id>', methods=['POST'])
@login_required
def delete_faculty(id):
    try:
        faculty = Faculty.query.get_or_404(id)
        db.session.delete(faculty)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Faculty deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
        
 ####################### faculty ends here
@app.route('/api/departments/by-faculty/<int:faculty_id>', methods=['GET'])
@login_required
def get_departments_by_faculty(faculty_id):
    try:
        departments = Department.query.filter_by(faculty_id=faculty_id).all()
        print(f"Found departments for faculty {faculty_id}: {[d.department_name for d in departments]}")  # Debug print
        return jsonify({
            'success': True,
            'departments': [dept.to_dict() for dept in departments]
        })
    except Exception as e:
        print(f"Error getting departments: {str(e)}")  # Debug print
        return jsonify({'success': False, 'message': str(e)}), 500
    

#####################################################################################
# Everything about department route
#####################################################################################
@app.route('/dashboard/department')
@login_required
def department():
    faculties = Faculty.query.all()
    departments = Department.query.all()
    department_count = Department.query.count()
    total_students = Student.query.count()
    content = render_template('department.html', 
                            faculties=faculties,
                            departments=departments,
                            department_count=department_count,
                            total_students=total_students)
    
    return render_template('dashboard.html', content=content, active_page='department')

@app.route('/api/department/add', methods=['POST'])
@login_required
def add_department():
    try:
        data = request.form
        programs = ','.join(request.form.getlist('programs[]'))
        
        new_department = Department(
            department_name=data.get('department_name'),
            hod_name=data.get('hod_name'),
            hod_email=data.get('hod_email'),
            faculty_id=data.get('faculty_id'),
            programs=programs,
            description=data.get('description'),
            status=data.get('status', 'active')
        )
        
        db.session.add(new_department)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'department': new_department.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    

@app.route('/api/department/list', methods=['GET'])
@login_required
def get_department_list():
    try:
        # Query departments with student count
        departments = db.session.query(
            Department,
            db.func.count(Student.id).label('student_count')
        ).outerjoin(
            Student,
            Student.department_id == Department.id
        ).group_by(Department.id).all()

        # Prepare the response data
        department_data = []
        for dept, student_count in departments:
            dept_dict = dept.to_dict()
            dept_dict['total_students'] = student_count
            department_data.append(dept_dict)

        return jsonify({
            'success': True,
            'data': department_data,
            'total_departments': len(departments)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    


@app.route('/api/department/edit/<int:id>', methods=['GET'])
@login_required
def get_department(id):
    try:
        department = Department.query.get_or_404(id)
        return jsonify({
            'success': True,
            'department': department.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/department/update/<int:id>', methods=['POST'])
@login_required
def update_department(id):
    try:
        department = Department.query.get_or_404(id)
        data = request.form
        programs = ','.join(request.form.getlist('programs[]'))
        
        department.department_name = data.get('department_name')
        department.hod_name = data.get('hod_name')
        department.hod_email = data.get('hod_email')
        department.faculty_id = data.get('faculty_id')
        department.programs = programs
        department.description = data.get('description')
        department.status = data.get('status')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'department': department.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/department/delete/<int:id>', methods=['POST'])
@login_required
def delete_department(id):
    try:
        department = Department.query.get_or_404(id)
        db.session.delete(department)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Department deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

###################################### Department route end here ####################



######################################################################
#Everything about level route
###################################################################
@app.route('/dashboard/level')
@login_required
def level():
    # Count ND2 students
    nd2_count = Student.query.filter_by(level='ND2').count()
    
    # Count HND2 students
    hnd2_count = Student.query.filter_by(level='HND2').count()
    
    content = render_template('level.html', nd2_count=nd2_count, hnd2_count=hnd2_count)
    return render_template('dashboard.html', content=content, active_page='level')
################################################Level route ends here




@app.route('/dashboard/generate-result')
@login_required
def generate_result():
    content = render_template('generate_result.html')
    return render_template('dashboard.html', content=content, active_page='generate_result')


# Result Routes
@app.route('/api/result/add', methods=['POST'])
@login_required
def add_result():
    try:
        data = request.form
        
        # Check if result already exists for this student
        existing_result = Result.query.filter_by(matric_number=data.get('matric_number')).first()
        if existing_result:
            return jsonify({
                'success': False,
                'message': 'Result has already been generated for this student'
            }), 400
            
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_year = datetime.now().year
        
        # Generate result content
        content = f"""This is to certify that {data.get('student_name')} ({data.get('matric_number')}), 
        having completed an approved course of study and passed the prescribed examinations, has, 
        by the authority of the Academic Board, been awarded the {data.get('programme')} of the 
        Federal Polytechnic, Nasarawa in {data.get('department')} with a grade of {data.get('grade')}, 
        {data.get('cgpa')} CGPA in {current_year} Academic Session. The effective date of the award 
        is {current_date}. The certificate will be issued in due course."""

        new_result = Result(
            matric_number=data.get('matric_number'),
            student_name=data.get('student_name'),
            department=data.get('department'),
            programme=data.get('programme'),
            grade=data.get('grade'),
            cgpa=float(data.get('cgpa')),
            status='generated',
            content=content
        )
        db.session.add(new_result)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Result generated successfully',
            'result': new_result.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    


@app.route('/api/result/list', methods=['GET'])
@login_required
def get_result_list():
    try:
        results = Result.query.order_by(Result.created_at.desc()).all()
        return jsonify({
            'success': True,
            'data': [result.to_dict() for result in results]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    


@app.route('/api/result/<int:id>', methods=['GET'])
@login_required
def get_result(id):
    try:
        result = Result.query.get_or_404(id)
        return jsonify({
            'success': True,
            'result': result.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    


@app.route('/api/result/update-status', methods=['POST'])
@login_required
def update_result_status():
    try:
        data = request.json
        result = Result.query.filter_by(matric_number=data.get('matric_number')).first()
        
        if result:
            result.status = data.get('status')
            result.content = data.get('content')
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Result status updated successfully'
            })
            
        return jsonify({'success': False, 'message': 'Result not found'}), 404
        
    except Exception as e:
        db.session.rollback()
        print('Error:', str(e))
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/result/delete/<int:id>', methods=['POST'])
@login_required
def delete_result(id):
    try:
        result = Result.query.get_or_404(id)
        db.session.delete(result)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Result deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500



########################################################################
@app.route('/dashboard/result-analytics')
@login_required
def result_analytics():
    content = render_template('result_analytics.html')
    return render_template('dashboard.html', content=content, active_page='result_analytics')


#################################################################################
#Everything about verify result route and endpoints
#################################################################################
@app.route('/dashboard/verify-certificate')
@login_required
def verify_certificate():
    content = render_template('verify_certificate.html')
    return render_template('dashboard.html', content=content, active_page='verify_certificate')

@app.route('/api/verify/get-departments', methods=['GET'])
@login_required
def get_departments_for_verify():
    try:
        departments = Department.query.filter_by(status='active').all()
        return jsonify({
            'success': True,
            'departments': [dept.department_name for dept in departments]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/verify/get-matric-numbers/<department>', methods=['GET'])
@login_required
def get_matric_numbers(department):
    try:
        dept = Department.query.filter_by(department_name=department).first()
        if not dept:
            return jsonify({'success': False, 'message': 'Department not found'}), 404
            
        students = Student.query.filter_by(department_id=dept.id).all()
        return jsonify({
            'success': True,
            'matric_numbers': [student.matric_number for student in students]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
    

@app.route('/api/verify/save-verification', methods=['POST'])
@login_required
def save_verification():
    try:
        data = request.json
        
        # Get student details from Result model
        result = Result.query.filter_by(matric_number=data['matric_number']).first()
        if not result:
            return jsonify({'success': False, 'message': 'Result not found'}), 404
            
        # Create new verification record
        verification = VerifiedResult(
            matric_number=result.matric_number,
            student_name=result.student_name,
            department=result.department,
            grade=result.grade,
            cgpa=result.cgpa,
            status='verified'
        )
        
        db.session.add(verification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Verification saved successfully',
            'verification': verification.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/verify/list', methods=['GET'])
@login_required
def get_verifications():
    try:
        verifications = VerifiedResult.query.order_by(VerifiedResult.verification_date.desc()).all()
        return jsonify({
            'success': True,
            'data': [v.to_dict() for v in verifications]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/result/verify', methods=['POST'])
@login_required
def verify_result():
    try:
        data = request.json
        result = Result.query.filter_by(
            matric_number=data['matric_number'],
            student_name=data['student_name'],
            grade=data['grade'],
            cgpa=float(data['cgpa'])
        ).first()
        
        return jsonify({
            'success': bool(result),
            'message': 'Result verified successfully' if result else 'Result not found'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500




###############################################################################################
# Everything about System settings
###############################################################################################
@app.route('/dashboard/settings')
@login_required
def settings():
    content = render_template('settings.html')
    return render_template('dashboard.html', content=content, active_page='settings')



# logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# database initialization
with app.app_context():
    db.create_all()
if __name__ == '__main__':
    app.run(debug=True, port=55555)