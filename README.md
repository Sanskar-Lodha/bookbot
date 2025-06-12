# 📚 BookBot 

**BookBot** is a Flask-based web application that allows users to register, log in, and interact with a chatbot to search and explore a catalog of books. The chatbot uses natural language processing (via OpenAI API) to understand user queries and help them find books by title, author, price range, or availability.

---

## 🚀 Features

- 🔐 User Authentication (Register, Login, Logout)
- 💬 Chat Interface for Book Search
- 🔍 Search Books by:
  - Title
  - Author
  - Price Range
- 🧠 Remembers Search Context (Pagination)
- 📦 Book Inventory Management (Stock, Price)
- 🌐 RESTful API Endpoints

---

## 📁 Project Structure

<pre lang="plaintext"> BookBot/ 
  │ ├── data/ 
  │   └── books.json # Initial book dataset 
  │ ├── Project/ 
  │   ├── __init__.py 
      ├── models.py # SQLAlchemy models  
      ├── forms.py # Flask-WTF forms 
  ├── static/ # Static assets (CSS/JS/images)   
  ├── templates/ 
      ├── base.html   
      ├── home.html  
      ├── login.html  
      ├── register.html 
      └── chatbot.html    
├── requirements.txt   
├── app.py # Main app entry point 
└── README.md </pre>
---

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite (SQLAlchemy)
- **Auth:** Flask-Login
- **Forms:** Flask-WTF
- **NLP:** OpenAI API (GPT)
- **Search:** RapidFuzz (fuzzy matching)
- **Templating:** Jinja2

---

## 1. Clone the repository
- git clone https://github.com/your-username/bookbot.git
- cd bookbot

  ---
## 2. Create a virtual environment
- python -m venv venv
- source venv/bin/activate

## 3. Install dependencies
- pip install -r requirements.txt

 ---
 ## 4. Set environment variables
 - SECRET_KEY=your_secret_key
 - OPENAI_API_KEY=your_openai_api_key

   ---
## 5. Initialize the database
- flask db init
- flask db migrate
- flask db upgrade
---
## 6. Run the app
- python app.py
- Visit http://127.0.0.1:5000 in your browser.

  ---
## 🧪 Example Chat Prompts
- J.K rowling
- Harry Potter
- recommend books
- recommend me a fiction story for 8 year old

---
## ✅ To-Do / Future Improvements
- Add book reviews/ratings
- Add admin panel for book management
- Improve error handling & bot responses
- Switch to production database (e.g., PostgreSQL)
- Deploy the website









  











