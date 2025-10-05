# SIAKAD (Sistem Informasi Akademik) — Flask + MySQL

A production-ready academic information system (SIAKAD) built with Flask, SQLAlchemy, JWT, and MySQL. It implements role-based access for Admin, Teacher, and Student with robust validation, error handling, logging, and a minimal dashboard UI.

## Features
- **Manajemen Siswa**: CRUD siswa (NIS, nama, tgl lahir, alamat, gender, telp orang tua, kelas)
- **Manajemen Guru**: CRUD guru (NIP, nama, telp, alamat)
- **Manajemen Mata Pelajaran**: CRUD mapel (kode, nama, SKS, guru pengampu)
- **Manajemen Nilai**: Input/update nilai (tugas, UTS, UAS), hitung nilai akhir otomatis, transkrip siswa, laporan per kelas (JSON/HTML cetak)
- **Login & Roles (JWT)**: Admin, Teacher, Student
- **Dashboard**: Statistik (jumlah siswa, guru, mapel) dan grafik rata-rata nilai per mapel

## Tech Stack
- Python 3.10+
- Flask 3, SQLAlchemy, Flask-JWT-Extended, Flask-Bcrypt, Marshmallow
- MySQL (PyMySQL)
- Optional: Flask-Migrate (included), Chart.js (frontend)

## Project Structure
```
siakad/
├─ run.py
├─ manage.py
├─ config.py
├─ requirements.txt
├─ .env.example
└─ siakad_app/
   ├─ __init__.py
   ├─ extensions.py
   ├─ models/
   │  ├─ __init__.py
   │  ├─ student.py
   │  ├─ teacher.py
   │  ├─ subject.py
   │  ├─ grade.py
   │  └─ user.py
   ├─ schemas/
   │  ├─ __init__.py
   │  ├─ student.py
   │  ├─ teacher.py
   │  ├─ subject.py
   │  ├─ grade.py
   │  └─ user.py
   ├─ routes/
   │  ├─ __init__.py
   │  ├─ auth_routes.py
   │  ├─ student_routes.py
   │  ├─ teacher_routes.py
   │  ├─ subject_routes.py
   │  ├─ grade_routes.py
   │  └─ dashboard_routes.py
   ├─ utils/
   │  ├─ decorators.py
   │  └─ errors.py
   ├─ templates/
   │  ├─ index.html
   │  └─ reports/
   │     └─ class_report.html
   └─ static/
      ├─ css/styles.css
      └─ js/main.js
```

## Setup
1. Create and activate a virtual environment (recommended)
   - Windows PowerShell:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy environment file and configure:
   ```bash
   copy .env.example .env   # Windows (PowerShell/CMD)
   ```
   Edit `.env`:
   - `SECRET_KEY`, `JWT_SECRET_KEY`
   - `DATABASE_URL` e.g.:
     - Laragon default (no password): `mysql+pymysql://root:@localhost:3306/siakad_db`
     - XAMPP or MySQL with password: `mysql+pymysql://root:yourpass@localhost:3306/siakad_db`
   - Set `AUTO_CREATE_DB=true` to auto create database on first run

4. Run the app:
   ```bash
   python run.py
   ```
   Open http://localhost:5000 to view the dashboard login page.

## First-time Admin User
Create an initial admin user via Flask CLI:
```bash
flask --app manage.py create-admin --username admin --password admin123
```
(Optional) Seed sample data (teachers, subjects, students):
```bash
flask --app manage.py seed-sample
```

## API Quick Start
- **Login** `POST /auth/login`
  ```json
  { "username": "admin", "password": "admin123" }
  ```
  Response contains `access_token`. Use it in header: `Authorization: Bearer <token>`

- **Register User (Admin only)** `POST /auth/register`
  - Admin: `{ username, password, role: "ADMIN" }`
  - Teacher user: `{ username, password, role: "TEACHER", teacher_id }`
  - Student user: `{ username, password, role: "STUDENT", student_id }`

### Students
- List: `GET /students/?q=&class_name=&page=&per_page=` (Admin/Teacher)
- Create: `POST /students/` (Admin)
- Detail: `GET /students/{id}` (Admin/Teacher; Student only for self)
- Update: `PUT/PATCH /students/{id}` (Admin)
- Delete: `DELETE /students/{id}` (Admin)
- My profile: `GET /students/me` (Student)

### Teachers
- List: `GET /teachers/?q=&page=&per_page=` (Admin)
- Create: `POST /teachers/` (Admin)
- Detail: `GET /teachers/{id}` (Admin; Teacher only for self)
- Update: `PUT/PATCH /teachers/{id}` (Admin)
- Delete: `DELETE /teachers/{id}` (Admin)
- My profile: `GET /teachers/me` (Teacher)

### Subjects
- List: `GET /subjects/?q=&page=&per_page=` (Admin/Teacher)
- Create: `POST /subjects/` (Admin)
- Detail: `GET /subjects/{id}` (Admin/Teacher)
- Update: `PUT/PATCH /subjects/{id}` (Admin)
- Delete: `DELETE /subjects/{id}` (Admin)

### Grades
- Upsert: `POST /grades/` (Admin/Teacher)
  - Body: `{ student_id, subject_id, tugas, uts, uas }`
  - Teacher can only input grades for subjects they teach
- Update: `PUT/PATCH /grades/{grade_id}` (Admin/Teacher)
- Transcript: `GET /grades/transcript/{student_id}` (Admin/Teacher; Student only for self)
- Grades by subject: `GET /grades/subject/{subject_id}` (Admin/Teacher)
- My grades: `GET /grades/me` (Student)
- Class report: `GET /grades/class-report?class_name=7A`
  - JSON by default
  - Printable HTML when `Accept: text/html` or open in browser

### Dashboard
- Stats: `GET /dashboard/stats` (Admin/Teacher)
- Average by subject: `GET /dashboard/avg-by-subject` (Admin/Teacher)

## Security & Best Practices
- Config via `.env` environment variables (`config.py`)
- Input validation with Marshmallow (`siakad_app/schemas/`)
- Parameterized queries via SQLAlchemy ORM (prevents SQL injection)
- Centralized error handling and proper HTTP codes (`siakad_app/utils/errors.py`)
- Logging configured via `Config.LOG_LEVEL`

## Notes
- Tables are ensured on app start (`db.create_all()`). For production, use Flask-Migrate.
- Ensure MySQL user has permission to create database if `AUTO_CREATE_DB=true`.
- Default UI is minimal; extend templates for richer admin pages as needed.
