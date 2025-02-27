from app import create_app
from app.models.models import reset_database_full, db

app = create_app()
reset_database_full(app)
print("Base de données réinitialisée avec succès !")
