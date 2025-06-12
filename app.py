from Project import app, db
from flask import Flask, render_template, redirect, request, url_for, flash, abort, session
from flask_login import login_user, logout_user, login_required, current_user
from Project.models import User, ChatMessage, Book
from Project.forms import LoginForm, RegistrationForm
from datetime import datetime
import json
from rapidfuzz import process, fuzz
import os
import re
import openai
from Project.models import UserMemory


# Setup OpenAI key from environment
openai.api_key = os.getenv("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")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/Welcome')
@login_required
def welcome_user():
    return render_template('welcome.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged Out")
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in Successfully!')
            next_page = request.args.get('next')
            if not next_page:
                next_page = url_for('welcome_user')
            return redirect(next_page)
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/populate_books')
def populate_books():
    with open('Project/data/books.json', 'r', encoding='utf-8') as f:
        books_data = json.load(f)
    if Book.query.count() == 0:
        books = []
        for item in books_data:
            book = Book(
                title=item['title'],
                author=item['author'],
                description=item.get('description', ''),
                price=item['price'],
                stock=item['stock']
            )
            books.append(book)
        db.session.add_all(books)
        db.session.commit()
        return f"{len(books)} books added to the database!"
    else:
        return "Books already exist in the database."

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    session.permanent = True
    if request.method == 'POST':
        user_message = request.form.get('message')
        if user_message:
            user_msg = ChatMessage(user_id=current_user.id, message=user_message, is_user=True)
            db.session.add(user_msg)
            bot_text = handle_bot_logic(user_message)
            bot_msg = ChatMessage(user_id=current_user.id, message=bot_text, is_user=False)
            db.session.add(bot_msg)
            db.session.commit()
    messages = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp).all()
    return render_template('chatbot.html', messages=messages)



def handle_bot_logic(user_input):
    inp = user_input.strip().lower()
    greetings = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]
    best_greet = process.extractOne(inp, greetings, scorer=fuzz.partial_ratio)
    if best_greet and best_greet[1] > 80:
        return f"{best_greet[0].title()}! How can I help you find a book today?"
    
    if "recommend" in inp:
        books = Book.query.order_by(Book.price.desc()).limit(5).all()
        save_user_memory(current_user.id, [b.id for b in books], 0)
        return format_books_details(books)


    # NEXT or MORE (pagination)
    if any(word in inp for word in ["next", "more"]):
        mem = get_user_memory(current_user.id)
        if not mem.get("books"):
            return "Nothing more to show. Ask me for books first!"
        return get_paginated_books_response(mem)

    # PRICE RANGE
    match = re.search(r'(\d+)\s*(?:to|-|and)?\s*(\d+)', inp)

    if match:
        low, high = map(int, match.groups())
        books = Book.query.filter(Book.price.between(low, high)).all()
        save_user_memory(current_user.id, [b.id for b in books], 0)
        return get_paginated_books_response(get_user_memory(current_user.id))

    # TITLE MATCH (using working version)
    titles = {b.title: b.id for b in Book.query.all()}
    match = process.extractOne(user_input, titles.keys(), scorer=fuzz.partial_ratio)
    if match and match[1] > 40:
        book = Book.query.get(titles[match[0]])
        return format_books_details([book])

    # AUTHOR MATCH (using working version)
    authors = {b.author: b.id for b in Book.query.all()}
    match = process.extractOne(user_input, authors.keys(), scorer=fuzz.partial_ratio)
    if match and match[1] > 70:
        books = Book.query.filter(Book.author.ilike(f"%{match[0]}%")).all()
        save_user_memory(current_user.id, [b.id for b in books], 0)
        return format_books_details(books)

    return "Sorry, I couldn't understand that. Try asking for a book title, author, price range, or say 'recommend me books'."


def format_books_details(books):
    parts = []
    for b in books:
        parts.append(
            f"• Title: {b.title}\n  Author: {b.author}\n  Price: ₹{int(b.price)}\n  Stock: {'In stock' if b.is_available() else 'Out of stock'}\n  Description: {b.description}"
        )
    return "\n\n".join(parts)

def get_paginated_books_response(mem):
    ids = mem["books"]
    offset = mem["offset"]
    subset = ids[offset:offset+5]
    books = Book.query.filter(Book.id.in_(subset)).all()

    # Save new offset
    save_user_memory(current_user.id, ids, offset + len(subset))

    response = format_books_details(books)
    if offset + len(subset) < len(ids):
        response += "\n\nType 'next' or 'more' to see more."
    return response

@app.route('/api/books', methods=['GET'])
def api_get_books():
    books = Book.query.all()
    return {"books": [b.to_dict() for b in books]}

@app.route('/api/book/<int:book_id>', methods=['GET'])
def api_get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return book.to_dict()

@app.route('/api/search', methods=['GET'])
def api_search():
    query = request.args.get('q', '')
    books = Book.query.filter(Book.title.ilike(f'%{query}%') | Book.author.ilike(f'%{query}%')).all()
    return {"results": [b.to_dict() for b in books]}





def get_user_memory(user_id):
    memory = UserMemory.query.filter_by(user_id=user_id).first()
    if memory:
        ids = list(map(int, memory.book_ids.split(","))) if memory.book_ids else []
        return {"books": ids, "offset": memory.offset}
    return {"books": [], "offset": 0}

def save_user_memory(user_id, book_ids, offset=0):
    memory = UserMemory.query.filter_by(user_id=user_id).first()
    if not memory:
        memory = UserMemory(user_id=user_id)
        db.session.add(memory)
    memory.book_ids = ",".join(map(str, book_ids))
    memory.offset = offset
    db.session.commit()







if __name__ == '__main__':
    app.run(debug=True)














