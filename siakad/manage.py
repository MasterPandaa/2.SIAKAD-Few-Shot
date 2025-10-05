import click
from siakad_app import create_app
from siakad_app.extensions import db
from siakad_app.models import User, Student, Teacher, Subject

app = create_app()


@app.cli.command('create-admin')
@click.option('--username', default='admin', show_default=True)
@click.option('--password', default='admin123', show_default=True)
def create_admin(username, password):
    """Create an initial ADMIN user."""
    with app.app_context():
        if User.query.filter_by(username=username).first():
            click.echo(f"User '{username}' already exists")
            return
        user = User(username=username, role='ADMIN')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Admin user created: {username}")


@app.cli.command('seed-sample')
def seed_sample():
    """Seed sample teachers, subjects, and students."""
    with app.app_context():
        # Teachers
        t1 = Teacher(nip='12345678', name='Budi', phone='0812345678')
        t2 = Teacher(nip='87654321', name='Sari', phone='0812345679')
        db.session.add_all([t1, t2])
        db.session.flush()

        # Subjects
        s1 = Subject(code='MAT101', name='Matematika', sks=3, teacher_id=t1.id)
        s2 = Subject(code='BIO101', name='Biologi', sks=2, teacher_id=t2.id)
        db.session.add_all([s1, s2])

        # Students
        from datetime import date
        st1 = Student(nis='2023000001', name='Andi', birth_date=date(2010,1,1), gender='L', class_name='7A', address='Jl. Mawar', parent_phone='0811111111')
        st2 = Student(nis='2023000002', name='Rina', birth_date=date(2010,2,2), gender='P', class_name='7A', address='Jl. Melati', parent_phone='0812222222')
        db.session.add_all([st1, st2])

        db.session.commit()
        click.echo('Sample data seeded')


if __name__ == '__main__':
    app.run(debug=True)
