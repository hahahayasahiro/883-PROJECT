"""Additive, transactional and repeatable upgrade of the original prototype."""
import json
from datetime import date, timedelta


def migrate(db):
    db.execute('CREATE TABLE IF NOT EXISTS schema_versions(version INTEGER PRIMARY KEY, applied TEXT DEFAULT CURRENT_TIMESTAMP)')
    db.execute('BEGIN IMMEDIATE')
    # Refresh only the obsolete seed wording; preserve locally customised policies.
    db.execute('UPDATE knowledge SET body=? WHERE id=? AND body=?', (
        'All prototype student profiles and campus rules are fictional. Campus questions, document text or fault descriptions are sent to DeepSeek only when the user requests the corresponding AI operation. Local file text extraction does not call AI.',
        'K15',
        'All prototype student profiles and campus rules are fictional. Application text is sent to DeepSeek only when the user requests an AI pre-review.',
    ))
    if db.execute('SELECT 1 FROM schema_versions WHERE version=2').fetchone():
        return
    additions={
        'courses':{'credits':'INTEGER NOT NULL DEFAULT 3'},
        'rooms':{'equipment':"TEXT NOT NULL DEFAULT '[]'"},
        'bookings':{'cancel_reason':"TEXT DEFAULT ''",'created':"TEXT DEFAULT ''"},
        'tickets':{'category':"TEXT DEFAULT 'other'",'priority':"TEXT DEFAULT 'normal'",'eta':"TEXT DEFAULT ''"},
        'applications':{'version':'INTEGER NOT NULL DEFAULT 1','created':"TEXT DEFAULT ''",'submitted_at':"TEXT DEFAULT ''",'decided_at':"TEXT DEFAULT ''",'was_returned':'INTEGER DEFAULT 0','file_name':"TEXT DEFAULT ''"},
        'reviews':{'version':'INTEGER NOT NULL DEFAULT 1'},
    }
    for table,columns in additions.items():
        present={r[1] for r in db.execute(f'PRAGMA table_info({table})')}
        for name,kind in columns.items():
            if name not in present:db.execute(f'ALTER TABLE {table} ADD COLUMN {name} {kind}')
    statements=[
      'CREATE TABLE IF NOT EXISTS conversations(id INTEGER PRIMARY KEY,user_id INTEGER REFERENCES users(id),title TEXT,created TEXT DEFAULT CURRENT_TIMESTAMP)',
      'CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY,conversation_id INTEGER REFERENCES conversations(id),question TEXT,result TEXT,created TEXT DEFAULT CURRENT_TIMESTAMP)',
      "CREATE TABLE IF NOT EXISTS learning_preferences(user_id INTEGER PRIMARY KEY REFERENCES users(id),interest TEXT DEFAULT 'computing',goal TEXT DEFAULT '')",
      'CREATE TABLE IF NOT EXISTS learning_plans(user_id INTEGER REFERENCES users(id),term TEXT,course_code TEXT REFERENCES courses(code),PRIMARY KEY(user_id,term,course_code))',
      'CREATE TABLE IF NOT EXISTS ticket_logs(id INTEGER PRIMARY KEY,ticket_id INTEGER REFERENCES tickets(id),actor_id INTEGER REFERENCES users(id),note TEXT,status TEXT,cost REAL DEFAULT 0,created TEXT DEFAULT CURRENT_TIMESTAMP)',
      'CREATE TABLE IF NOT EXISTS energy_readings(room_id INTEGER REFERENCES rooms(id),day TEXT,hour INTEGER,kwh REAL,occupancy INTEGER,PRIMARY KEY(room_id,day,hour))',
      "CREATE TABLE IF NOT EXISTS application_versions(application_id INTEGER REFERENCES applications(id),version INTEGER,kind TEXT,fields TEXT,material TEXT,file_name TEXT DEFAULT '',created TEXT DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY(application_id,version))",
      'CREATE TABLE IF NOT EXISTS application_events(id INTEGER PRIMARY KEY,application_id INTEGER REFERENCES applications(id),actor_id INTEGER REFERENCES users(id),action TEXT,note TEXT,version INTEGER,created TEXT DEFAULT CURRENT_TIMESTAMP)',
      'CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY,user_id INTEGER REFERENCES users(id),application_id INTEGER REFERENCES applications(id),message TEXT,is_read INTEGER DEFAULT 0,created TEXT DEFAULT CURRENT_TIMESTAMP)',
    ]
    for statement in statements:db.execute(statement)
    for room in db.execute('SELECT id,kind FROM rooms').fetchall():
        equipment=['whiteboard','wifi']+(['projector'] if room['kind'] in ['Laboratory','Classroom','Meeting room'] else [])+(['computers'] if room['kind']=='Laboratory' else [])
        db.execute('UPDATE rooms SET equipment=? WHERE id=?',(json.dumps(equipment),room['id']))
        for offset in range(7):
            day=(date.today()-timedelta(days=offset)).isoformat()
            for hour in [8,10,12,14,16,18]:
                occupancy=(room['id']*13+hour*7+offset*11)%95
                kwh=round(3+occupancy*.22+room['id']*.7,2)
                db.execute('INSERT OR IGNORE INTO energy_readings VALUES(?,?,?,?,?)',(room['id'],day,hour,kwh,occupancy))
    for item in db.execute('SELECT * FROM applications').fetchall():
        db.execute('INSERT OR IGNORE INTO application_versions(application_id,version,kind,fields,material,file_name) VALUES(?,?,?,?,?,?)',(item['id'],1,item['kind'],item['fields'],item['material'],item['file_name']))
        db.execute('INSERT INTO application_events(application_id,actor_id,action,note,version) VALUES(?,?,?,?,?)',(item['id'],item['user_id'],'imported','Existing record preserved; original timestamps unavailable.',1))
    db.execute("UPDATE knowledge SET body='Applications move from draft to submitted. Staff may return them for corrections, approve or reject. Students revise returned drafts and resubmit. Only administrative staff decide submitted applications.' WHERE id='K11'")
    db.execute('CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id,id)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id,is_read)')
    db.execute('INSERT INTO schema_versions(version) VALUES(2)')
