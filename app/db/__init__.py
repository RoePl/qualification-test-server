from app.db.build.entities import FileStorage, Table, connect_tables
from app.db.models import User, Administrator

users = Table(User)
admins = Table(Administrator)
images = FileStorage("./bucket/images")

connect_tables("./bucket/tables")
