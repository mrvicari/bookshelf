from flask import render_template, request, url_for, flash, redirect
from app import app, models, db, login_manager
from .forms import LogInForm, RegisterForm, ChangePassForm, AddListForm, AddBookForm, EditListForm
import bcrypt, logging
from flask_login import login_user, login_required, current_user, logout_user

log = logging.getLogger('views')
handler = logging.FileHandler('BookRecord.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.DEBUG)

@app.route('/')
def index():
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(id):
    return models.User.query.get(int(id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    log.debug("GET register page")
    form = RegisterForm()
    if form.validate_on_submit():
        log.debug("Register form submitted")
        user = models.User.query.filter_by(usernameDB=form.username.data).first()
        if user is None:
            if form.password.data == form.repeatPassword.data:
                password_hash = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
                newUser = models.User(usernameDB=form.username.data, passwordDB=password_hash)
                db.session.add(newUser)
                db.session.commit()
                log.info("Successfully registered user '%s'", form.username.data)
                return redirect(url_for('login'))
            else:
                log.error("Cannot register: Passwords do not match")
                flash("Passwords do not match!")
        else:
            log.error("Cannot register: Username already exists")
            flash("Username already exists!")
            form.username.data=""
    return render_template('Register.html', title = 'Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    log.debug("GET login page")
    form = LogInForm()
    if form.validate_on_submit():
        log.debug("Login form submitted")
        user = models.User.query.filter_by(usernameDB=form.username.data).first()
        if user:
            if bcrypt.checkpw(form.password.data.encode('utf-8'), user.passwordDB):
                user.authenticated=True
                db.session.commit()
                login_user(user)
                log.info("Successfully logged in user '%s'", current_user.usernameDB)
                return redirect(url_for('lists'))
            else:
                log.error("Cannot login: Wrong password")
                flash("Wrong Password!")
        else:
            log.error("Cannot login: Wrong username")
            flash("Wrong Username!")
            form.username.data=""
    return render_template('LogIn.html', title = 'Log In', form=form)

@app.route('/logout')
@login_required
def logout():
    current_user.authenticated=False
    log.info("Successfully logged out user '%s'", current_user.usernameDB)
    logout_user();
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    log.debug("GET profile page")
    form = ChangePassForm()
    if form.validate_on_submit():
        log.debug("Change password submitted")
        chUser = models.User.query.filter_by(usernameDB=current_user.usernameDB).first()
        if bcrypt.checkpw(form.oldPassword.data.encode('utf-8'), chUser.passwordDB):
            if form.newPassword.data == form.repeatNewPassword.data:
                chUser.passwordDB = bcrypt.hashpw(form.newPassword.data.encode('utf-8'), bcrypt.gensalt())
                db.session.commit()
                log.info("Password for user '%s' successfully changed", current_user.usernameDB)
                flash("Password Changed!")
            else:
                log.error("Cannot change password: Passwords do not match")
                flash("Passwords do not match!")
        else:
            log.error("Cannot change password: wrong current password")
            flash("Wrong Password!")
    return render_template('ChangePassword.html', title = 'Change Password', form=form)

@app.route('/lists')
@login_required
def lists():
    # log.debug("GET lists page")
    user = models.User.query.filter_by(usernameDB=current_user.usernameDB).first()
    return render_template('Lists.html', title = 'Book Lists', Lists = models.List.query.filter_by(user_id=user.id))

@app.route('/addList', methods=['POST', 'GET'])
@login_required
def addList():
    log.debug("GET add list page")
    form = AddListForm()
    if form.validate_on_submit():
        log.debug("Add list form submitted")
        user = models.User.query.filter_by(usernameDB=current_user.usernameDB).first()
        newList = models.List(listTitle=form.listTitle.data, listDescription=form.listDescription.data, user_id=user.id)
        checkList = models.List.query.filter_by(listTitle=form.listTitle.data).filter_by(user_id=current_user.id).first()
        if checkList is None:
            db.session.add(newList)
            db.session.commit()
            log.info("Successfully added list '%s'", newList.listTitle)
        else:
            log.error("Cannot add list: List already exists")
            flash("List already exists!")

        form.listTitle.data=""
        form.listDescription.data=""
        flash("List added!")
    return render_template('AddList.html', title = 'Add List', form=form)

@app.route('/editList/<listID>', methods=['POST', 'GET'])
@login_required
def editList(listID):
    log.debug("GET edit list page")
    form = EditListForm()

    editList = models.List.query.filter_by(id=listID).first()
    form = EditListForm(obj=editList)

    getList = models.List.query.filter_by(id=listID).first()
    BooksToRemove = [(book.id, book.bookTitle) for book in getList.books]
    form.booksToRemove.choices = BooksToRemove

    if form.validate_on_submit():
        log.debug("Edit list form submitted")
        editList.listTitle = form.listTitle.data
        editList.listDescription = form.listDescription.data
        for bookID in form.booksToRemove.data:
            removeFromList = models.Book.query.get(bookID)
            editList.books.remove(removeFromList)
        db.session.commit()
        log.info("Successfully edit list '%s'", form.listTitle.data)
        return redirect(url_for('lists'))

    return render_template('EditList.html', title = 'Edit List', form=form, Books = models.Book.query.filter_by(user_id=current_user.id))

@app.route('/removeList/<listID>')
@login_required
def removeList(listID):
    rmList = models.List.query.get(listID)
    db.session.delete(rmList)
    db.session.commit()
    log.info("Successfully removed list '%s'", rmList.listTitle)
    return redirect(url_for('lists'))

@app.route('/books')
@login_required
def books():
    log.debug("GET books page")
    user = models.User.query.filter_by(usernameDB=current_user.usernameDB).first()
    return render_template('Books.html', title = 'Books', Books = models.Book.query.filter_by(user_id=user.id))

@app.route('/addBook', methods=['POST', 'GET'])
@login_required
def addBook():
    log.debug("GET add book page")
    form = AddBookForm()
    user = models.User.query.filter_by(usernameDB=current_user.usernameDB).first()
    ListsToPick = [(list.id, list.listTitle) for list in models.List.query.filter_by(user_id=user.id)]
    form.addBookToList.choices = ListsToPick
    if form.validate_on_submit():
        log.debug("Add book form submitted")
        newBook = models.Book(bookTitle=form.bookTitle.data, bookRating=form.bookRating.data, user_id=user.id)
        checkBook = models.Book.query.filter_by(user_id=current_user.id).filter_by(bookTitle=form.bookTitle.data).first()
        if checkBook is None:
            for listID in form.addBookToList.data:
                addToList = models.List.query.get(listID)
                newBook.lists.append(addToList)
            db.session.add(newBook)
            db.session.commit()
            log.info("Successfully added book '%s'", newBook.bookTitle)
        else:
            log.error("Cannot add book: Book already exists")
            flash("Book alreay exists!")

        form.bookTitle.data=""
        form.bookRating.data=""
        flash("Book added!")
    return render_template('AddBook.html', title = 'Add Book', form=form, Lists = models.List.query.filter_by(user_id=user.id))

@app.route('/editBook/<bookID>', methods=['POST', 'GET'])
def editBook(bookID):
    log.debug("GET edit book page")
    form = AddBookForm()

    editedBook = models.Book.query.filter_by(id=bookID).first()
    form = AddBookForm(obj=editedBook)

    user = models.User.query.filter_by(usernameDB=current_user.usernameDB).first()
    ListsToPick = [(list.id, list.listTitle) for list in models.List.query.filter_by(user_id=user.id)]
    form.addBookToList.choices = ListsToPick

    if form.validate_on_submit():
        log.debug("Edit book form submitted")
        editedBook.bookTitle = form.bookTitle.data
        editedBook.bookRating = form.bookRating.data

        for listID in form.addBookToList.data:
            addToList = models.List.query.get(listID)
            editedBook.lists.append(addToList)
        db.session.commit()
        log.info("Successfully edited book '%s'", form.bookTitle.data)
        return redirect(url_for('books'))
    return render_template('AddBook.html', title = 'Edit Book', form=form, Lists = models.List.query.filter_by(user_id=user.id))

@app.route('/removeBook/<bookID>')
@login_required
def removeBook(bookID):
    book = models.Book.query.get(bookID)
    db.session.delete(book)
    db.session.commit()
    log.info("Successfully removed book '%s'", book.bookTitle)
    return redirect(url_for('books'))

@app.route('/<listID>')
@login_required
def getList(listID):
    if models.List.query.filter_by(id=listID).first():
        getList = models.List.query.filter_by(id=listID).first()
        log.debug("GET list '%s' page", getList.listTitle)
        user = models.User.query.filter_by(usernameDB=current_user.usernameDB).first()
        return render_template('ListOfBooks.html', title = 'Book Lists', Books = getList.books, listTitle = getList.listTitle, listID=listID)
    else:
        return redirect(url_for('lists'))

@app.route('/removeUser/<userID>')
@login_required
def removeUser(userID):
    rmUser = models.User.query.get(userID)
    db.session.delete(rmUser)
    db.session.commit()
    log.info("Successfully removed user '%s'", current_user.usernameDB)
    logout_user()
    return redirect(url_for('login'))

@app.route('/help')
@login_required
def help():
    return render_template('Help.html', title = 'Help')

@app.route('/clear')
def clearList():
    Tasks = models.List.query.all()
    for task in Tasks:
        db.session.delete(task)
        db.session.commit()
    return("DB Cleared")
