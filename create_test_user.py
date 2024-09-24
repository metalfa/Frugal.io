from __init__ import create_app, db, bcrypt
from models import User

app = create_app()

def create_test_user():
    with app.app_context():
        # Check if the test user already exists
        test_user = User.query.filter_by(email='test@example.com').first()
        if test_user is None:
            # Create a new test user
            hashed_password = bcrypt.generate_password_hash('testpassword').decode('utf-8')
            new_user = User(username='testuser', email='test@example.com', password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            print("Test user created successfully.")
        else:
            print("Test user already exists.")

if __name__ == '__main__':
    create_test_user()
