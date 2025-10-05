from siakad_app.extensions import db
from sqlalchemy import UniqueConstraint


class Grade(db.Model):
    __tablename__ = "grades"
    __table_args__ = (
        UniqueConstraint("student_id", "subject_id",
                         name="uq_student_subject"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.Integer, db.ForeignKey("students.id"), nullable=False, index=True
    )
    subject_id = db.Column(
        db.Integer, db.ForeignKey("subjects.id"), nullable=False, index=True
    )

    tugas = db.Column(db.Float, nullable=False, default=0.0)
    uts = db.Column(db.Float, nullable=False, default=0.0)
    uas = db.Column(db.Float, nullable=False, default=0.0)

    def __init__(
        self,
        student_id: int,
        subject_id: int,
        tugas: float = 0.0,
        uts: float = 0.0,
        uas: float = 0.0,
    ):
        self.student_id = student_id
        self.subject_id = subject_id
        self.tugas = self._score(tugas)
        self.uts = self._score(uts)
        self.uas = self._score(uas)

    @staticmethod
    def _score(val: float) -> float:
        try:
            v = float(val)
        except Exception:
            raise ValueError("Nilai harus berupa angka")
        if v < 0 or v > 100:
            raise ValueError("Nilai harus di antara 0 dan 100")
        return round(v, 2)

    @property
    def final_score(self) -> float:
        return round((float(self.tugas) + float(self.uts) + float(self.uas)) / 3.0, 2)

    def to_dict(self, include_student=False, include_subject=False):
        data = {
            "id": self.id,
            "student_id": self.student_id,
            "subject_id": self.subject_id,
            "tugas": self.tugas,
            "uts": self.uts,
            "uas": self.uas,
            "final": self.final_score,
        }
        if include_student and self.student:
            data["student"] = {
                "id": self.student.id,
                "name": self.student.name,
                "nis": self.student.nis,
                "class_name": self.student.class_name,
            }
        if include_subject and self.subject:
            data["subject"] = {
                "id": self.subject.id,
                "code": self.subject.code,
                "name": self.subject.name,
            }
        return data
