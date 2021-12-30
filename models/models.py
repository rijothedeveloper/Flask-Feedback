from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

def connect_db(app):
    """ connect to a database """
    db.app = app
    db.init_app(app)
    bcrypt = Bcrypt()
    
    class User(db.Model):
        """ user """
        
        __tablename__ = "user"
        
        id = db.Column(db.Integer,
                       primary_key=True,
                       autoincrement=True)
        
        username = db.Column(db.Text,
                             nullable=False,
                             unique=True)
        
        password = db.Column(db.Text,
                             nullable=False)
        
        email = db.Column(db.Text,
                             nullable=False,
                             unique=True)
        
        first_name = db.Column(db.Text,
                             nullable=False)
        
        last_name = db.Column(db.Text,
                             nullable=False)
        
        @classmethod
        def register(cls, username, pwd, email, first_name, last_name):
            hashed_pwd = bcrypt.generate_password_hash(pwd)
            # turn bytestring into normal (unicode utf8) string
            hashed_pwd_utf8 = hashed_pwd.decode("utf8")
            
            return cls(username=username, password=hashed_pwd_utf8, email=email, first_name=first_name, last_name=last_name)
            
        @classmethod
        def authenticate(cls, username, pwd):
            """Validate that user exists & password is correct.

            Return user if valid; else return False.
            """

            u = User.query.filter_by(username=username).first()

            if u and bcrypt.check_password_hash(u.password, pwd):
                # return user instance
                return u
            else:
                return False