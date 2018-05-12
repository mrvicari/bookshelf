from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usernameDB = db.Column(db.String(10), unique=True)
    passwordDB = db.Column(db.Unicode(20))
    authenticated = db.Column(db.Boolean, default=False)
    lists = db.relationship('List', backref='user', lazy='dynamic')

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

ListBook = db.Table('ListBook', db.Model.metadata,
    db.Column('listID', db.Integer, db.ForeignKey('list.id')),
    db.Column('bookID', db.Integer, db.ForeignKey('book.id'))
)

class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listTitle = db.Column(db.String(20))
    listDescription = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    books = db.relationship('Book', secondary=ListBook)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bookTitle = db.Column(db.String(20))
    bookRating = db.Column(db.Integer())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    lists = db.relationship('List', secondary=ListBook)
