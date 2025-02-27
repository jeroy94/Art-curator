from app import create_app
from app.models.models import db
from flask_migrate import Migrate, upgrade

def run_migration():
    app = create_app()
    with app.app_context():
        migrate = Migrate(app, db)
        upgrade()

if __name__ == '__main__':
    run_migration()
