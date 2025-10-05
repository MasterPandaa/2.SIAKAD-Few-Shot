import re
from datetime import date

from siakad_app.extensions import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    nis = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.String(1), nullable=False)  # 'L' or 'P'
    parent_phone = db.Column(db.String(20), nullable=True)
    class_name = db.Column(db.String(20), nullable=False)

    grades = db.relationship(
        "Grade", backref="student", lazy=True, cascade="all, delete-orphan"
    )

    def __init__(
        self,
        nis: str,
        name: str,
        birth_date: date,
        address: str,
        gender: str,
        parent_phone: str,
        class_name: str,
    ):
        self.nis = self._validate_nis(nis)
        self.name = self._validate_name(name)
        self.birth_date = birth_date
        self.address = (address or "").strip()
        self.gender = self._validate_gender(gender)
        self.parent_phone = self._validate_phone(parent_phone)
        self.class_name = self._validate_class_name(class_name)

    @staticmethod
    def _validate_nis(nis: str) -> str:
        if not re.fullmatch(r"\d{10}", str(nis).strip()):
            raise ValueError("NIS harus 10 digit angka")
        return str(nis).strip()

    @staticmethod
    def _validate_name(name: str) -> str:
        name = (name or "").strip()
        if len(name) < 3:
            raise ValueError("Nama minimal 3 karakter")
        return name

    @staticmethod
    def _validate_gender(gender: str) -> str:
        gender = (gender or "").strip().upper()
        if gender not in {"L", "P"}:
            raise ValueError(
                "Gender harus 'L' (Laki-laki) atau 'P' (Perempuan)")
        return gender

    @staticmethod
    def _validate_phone(phone: str) -> str:
        if phone is None:
            return ""
        phone = re.sub(r"\s+", "", str(phone))
        if not re.fullmatch(r"\d{8,15}", phone):
            raise ValueError("Nomor telepon orang tua harus 8-15 digit")
        return phone

    @staticmethod
    def _validate_class_name(cname: str) -> str:
        cname = (cname or "").strip()
        if not cname:
            raise ValueError("Kelas harus diisi")
        if len(cname) > 20:
            raise ValueError("Nama kelas maksimal 20 karakter")
        return cname

    def to_dict(self):
        return {
            "id": self.id,
            "nis": self.nis,
            "name": self.name,
            "birth_date": self.birth_date.isoformat(),
            "address": self.address,
            "gender": self.gender,
            "parent_phone": self.parent_phone,
            "class_name": self.class_name,
        }
