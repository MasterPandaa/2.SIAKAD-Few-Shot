import re
from siakad_app.extensions import db


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    sks = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True)

    grades = db.relationship('Grade', backref='subject', lazy=True, cascade='all, delete-orphan')

    def __init__(self, code: str, name: str, sks: int, teacher_id: int = None):
        self.code = self._validate_code(code)
        self.name = self._validate_name(name)
        self.sks = self._validate_sks(sks)
        self.teacher_id = teacher_id

    @staticmethod
    def _validate_code(code: str) -> str:
        code = (code or '').strip().upper()
        if not re.fullmatch(r'[A-Z0-9_\-]{2,12}', code):
            raise ValueError('Kode mata pelajaran harus 2-12 karakter (A-Z, 0-9, _ atau -)')
        return code

    @staticmethod
    def _validate_name(name: str) -> str:
        name = (name or '').strip()
        if len(name) < 2:
            raise ValueError('Nama mata pelajaran minimal 2 karakter')
        return name

    @staticmethod
    def _validate_sks(sks: int) -> int:
        try:
            sks = int(sks)
        except Exception:
            raise ValueError('SKS harus berupa angka')
        if sks < 1 or sks > 6:
            raise ValueError('SKS harus antara 1 sampai 6')
        return sks

    def to_dict(self, include_teacher: bool = True):
        data = {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'sks': self.sks,
            'teacher_id': self.teacher_id,
        }
        if include_teacher and self.teacher:
            data['teacher'] = {'id': self.teacher.id, 'name': self.teacher.name, 'nip': self.teacher.nip}
        return data
