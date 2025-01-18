from flask_migrate import Migrate

from inatorAPI import create_app
from inatorAPI import db

app = create_app()
migrate = Migrate(app, db)


if __name__ == '__main__':
    app.run()
