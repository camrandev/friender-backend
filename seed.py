"""Seed database with sample data from CSV Files."""

from csv import DictReader
from app import db
from models import User

db.drop_all()
db.create_all()


with open("generator/users.csv") as users:
    db.session.bulk_insert_mappings(User, DictReader(users))

    users = User.query.all()
    for user in users:
        user.set_location()

    for user in users[0:5]:
        for u in users:
            if u != user:
                u.likes.append(user)

db.session.commit()
