from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    # avoid recursive serialization of related recipes when returning user JSON
    serialize_rules = ('-recipes',)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.LargeBinary)
    image_url = db.Column(db.String)
    bio = db.Column(db.Text)

    # relationship to recipes
    recipes = db.relationship('Recipe', backref='user')

    # hide password hash from being accessed
    @property
    def password_hash(self):
        raise AttributeError("password_hash is not a readable attribute")

    @password_hash.setter
    def password_hash(self, password):
        # store hashed bytes
        self._password_hash = bcrypt.generate_password_hash(password)

    def authenticate(self, password):
        if not self._password_hash:
            return False
        return bcrypt.check_password_hash(self._password_hash, password)


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    # avoid recursive serialization of the related user
    serialize_rules = ('-user',)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @validates('instructions')
    def validate_instructions(self, key, value):
        if not value or len(value) < 50:
            raise ValueError('Instructions must be at least 50 characters long')
        return value
