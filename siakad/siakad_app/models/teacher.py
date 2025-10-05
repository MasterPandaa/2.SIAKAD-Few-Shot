import re

from siakad_app.extensions import db


class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)
    nip = db.Column(db.String(30), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)

    subjects = db.relationship("Subject", backref="teacher", lazy=True)

    def __init__(self, nip: str, name: str, phone: str = None, address: str = None):
        self.nip = self._validate_nip(nip)
        self.name = self._validate_name(name)
        self.phone = self._validate_phone(phone)
        self.address = (address or "").strip()

    @staticmethod
    def _validate_nip(nip: str) -> str:
        nip = str(nip).strip()
        # typical NIP length; flexible 8-18
        if not re.fullmatch(r"\d{8,18}", nip):
            raise ValueError("NIP harus 8-18 digit angka")
        return nip

    @staticmethod
    def _validate_name(name: str) -> str:
        name = (name or "").strip()
        if len(name) < 3:
            raise ValueError("Nama minimal 3 karakter")
        return name

    @staticmethod
    def _validate_phone(phone: str) -> str:
        if not phone:
            return ""
        phone = re.sub(r"\s+", "", str(phone))
        if not re.fullmatch(r"\d{8,15}", phone):
            raise ValueError("Nomor telepon harus 8-15 digit")
        return phone

    def to_dict(self, include_subjects: bool = True):
        data = {
            "id": self.id,
            "nip": self.nip,
            "name": self.name,
            "phone": self.phone,
            "address": self.address,
        }
        if include_subjects:
            data["subjects"] = [s.to_dict(include_teacher=False)
                                for s in self.subjects]
        return data
