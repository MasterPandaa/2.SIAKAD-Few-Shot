from siakad_app.extensions import db, bcrypt


ROLES = {'ADMIN', 'TEACHER', 'STUDENT'}


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)

    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True)

    student = db.relationship('Student', backref=db.backref('user', uselist=False))
    teacher = db.relationship('Teacher', backref=db.backref('user', uselist=False))

    def __init__(self, username: str, role: str, student_id=None, teacher_id=None):
        self.username = username.strip()
        self.set_role(role)
        self.student_id = student_id
        self.teacher_id = teacher_id

    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def set_role(self, role: str):
        role = (role or '').upper()
        if role not in ROLES:
            raise ValueError('Role tidak valid. Gunakan ADMIN, TEACHER, atau STUDENT')
        self.role = role

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'student_id': self.student_id,
            'teacher_id': self.teacher_id,
        }
