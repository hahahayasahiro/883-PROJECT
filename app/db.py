"""Shared schema and synthetic demonstration fixtures. No real student data."""
import hashlib
import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def connect():
    path = Path(os.getenv('SMARTCAMPUS_DB', str(ROOT / 'data' / 'campus.sqlite')))
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    return db


def password_hash(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 120_000).hex()


COURSES = [
    ('CS101', 'Introduction to Programming', '', 'computing'),
    ('CS102', 'Data Structures', 'CS101', 'computing'),
    ('CS201', 'Database Systems', 'CS101', 'computing'),
    ('CS202', 'Artificial Intelligence', 'CS102', 'ai'),
    ('CS203', 'Web Development', 'CS101', 'computing'),
    ('MA101', 'Mathematics for Computing', '', 'mathematics'),
    ('ST201', 'Statistics', 'MA101', 'mathematics'),
    ('CS301', 'Machine Learning', 'CS202', 'ai'),
    ('PM101', 'Project Management', '', 'management'),
    ('IS201', 'Systems Analysis', 'CS101', 'management'),
]
KNOWLEDGE = [
    ('K01', 'CS102 prerequisites', 'CS102 Data Structures requires a pass in CS101 Introduction to Programming.'),
    ('K02', 'CS202 prerequisites', 'CS202 Artificial Intelligence requires a pass in CS102 Data Structures.'),
    ('K03', 'CS301 prerequisites', 'CS301 Machine Learning requires a pass in CS202 Artificial Intelligence.'),
    ('K04', 'Transcript application', 'A transcript application requires student ID, full name, university email and a purpose. Staff review applications before approval.'),
    ('K05', 'Certificate application', 'A certificate application requires student ID, full name, university email, purpose and certificate type.'),
    ('K06', 'Room booking rules', 'Rooms can be booked for up to two hours per booking. Overlapping active bookings are prohibited. Cancel a booking if you no longer need it.'),
    ('K07', 'Library opening hours', 'The demonstration library opens Monday to Friday from 08:00 to 22:00. Weekend opening is 10:00 to 18:00.'),
    ('K08', 'Attendance support', 'Attendance below 75 percent triggers a support reminder in this prototype. This is a synthetic demonstration rule, not a real university policy.'),
    ('K09', 'Academic support', 'Students with assessment marks below 50 should contact their course tutor and arrange an academic support appointment.'),
    ('K10', 'Facility fault reports', 'Report room equipment faults using a room name and description. The maintenance team tracks reports as open, in_progress and completed.'),
    ('K11', 'Application tracking', 'Applications move from draft to submitted and then approved or rejected. Only administrative staff can approve or reject submitted applications.'),
    ('K12', 'Energy demonstration', 'Energy charts use synthetic occupancy and electricity readings. The prototype does not control real equipment.'),
    ('K13', 'Database Systems', 'CS201 Database Systems requires CS101. It covers relational modelling, SQL and transactions.'),
    ('K14', 'Web Development', 'CS203 Web Development requires CS101. It introduces HTML, CSS, JavaScript and web services.'),
    ('K15', 'Privacy and AI', 'All prototype student profiles and campus rules are fictional. Campus questions, document text or fault descriptions are sent to DeepSeek only when the user requests the corresponding AI operation. Local file text extraction does not call AI.'),
]


def initialize(reset=False):
    with connect() as db:
        if reset:
            for table in ['notifications','application_events','application_versions','energy_readings','ticket_logs','learning_plans','learning_preferences','messages','conversations','schema_versions','sessions', 'reviews', 'applications', 'tickets', 'bookings', 'records', 'knowledge', 'courses', 'rooms', 'users']:
                db.execute(f'DROP TABLE IF EXISTS {table}')
        db.executescript('''
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, name TEXT, role TEXT, student_id TEXT, email TEXT, salt TEXT, password_hash TEXT);
        CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, user_id INTEGER REFERENCES users(id), expires REAL);
        CREATE TABLE IF NOT EXISTS courses(code TEXT PRIMARY KEY, name TEXT, prerequisite TEXT, area TEXT);
        CREATE TABLE IF NOT EXISTS records(user_id INTEGER REFERENCES users(id), course_code TEXT REFERENCES courses(code), grade REAL, attendance REAL, PRIMARY KEY(user_id,course_code));
        CREATE TABLE IF NOT EXISTS knowledge(id TEXT PRIMARY KEY, title TEXT, body TEXT);
        CREATE TABLE IF NOT EXISTS rooms(id INTEGER PRIMARY KEY, name TEXT, capacity INTEGER, kind TEXT);
        CREATE TABLE IF NOT EXISTS bookings(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id), room_id INTEGER REFERENCES rooms(id), start TEXT, end TEXT, status TEXT DEFAULT 'active');
        CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id), room_id INTEGER REFERENCES rooms(id), description TEXT, status TEXT DEFAULT 'open', cost REAL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS applications(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id), kind TEXT, fields TEXT, material TEXT, status TEXT DEFAULT 'draft', decision_note TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY, application_id INTEGER REFERENCES applications(id), result TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);
        ''')
        if db.execute('SELECT count(*) FROM users').fetchone()[0]:
            from .migrations import migrate
            migrate(db)
            return
        import secrets
        for uid, username, name, role, sid in [(1,'student','Alex Morgan','student','S1001'),(2,'student2','Jamie Chen','student','S1002'),(3,'admin','Taylor Reed','admin',''),(4,'maintenance','Sam Patel','maintenance','')]:
            salt = secrets.token_hex(16)
            db.execute('INSERT INTO users VALUES(?,?,?,?,?,?,?,?)', (uid,username,name,role,sid,f'{username}@gcu.example',salt,password_hash('Campus2026!',salt)))
        db.executemany('INSERT INTO courses VALUES(?,?,?,?)', COURSES)
        db.executemany('INSERT INTO knowledge VALUES(?,?,?)', KNOWLEDGE)
        db.executemany('INSERT INTO records VALUES(?,?,?,?)', [(1,'CS101',78,90),(1,'MA101',45,68),(1,'PM101',65,83),(2,'CS101',82,95)])
        db.executemany('INSERT INTO rooms VALUES(?,?,?,?)', [(i+1,n,c,k) for i,(n,c,k) in enumerate([('Library Study A',6,'Study room'),('Library Study B',8,'Study room'),('Computing Lab 1',30,'Laboratory'),('Computing Lab 2',24,'Laboratory'),('Seminar Room 1',20,'Classroom'),('Seminar Room 2',40,'Classroom'),('Meeting Room',10,'Meeting room'),('Sports Hall',60,'Sports')])])
        db.execute("INSERT INTO tickets(user_id,room_id,description) VALUES(1,3,'Projector does not turn on')")
        db.execute("INSERT INTO applications(user_id,kind,fields,material,status) VALUES(2,'transcript',?,?,'submitted')", ('{"student_id":"S1002","full_name":"Jamie Chen","email":"student2@gcu.example","purpose":"Internship"}', 'Please provide my transcript for an internship.'))
        db.commit()
        from .migrations import migrate
        migrate(db)


def rows(query, args=()):
    with connect() as db:
        return [dict(r) for r in db.execute(query, args).fetchall()]
