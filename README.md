# Budget Pet

**This is a personal pet project (financial tracker) built for educational purposes.**

This project was developed to meet some custom personal requirements for a financial tracker — for example, the ability to split the budget into specific categories tailored to my needs, and to specify a tax amount when adding income, which is then automatically allocated to the Taxes category of the budget.

I developed it while learning the technologies involved — including Flask, Pydantic, and relational databases.  
The goal was not to create a production-ready or user-friendly application, but rather to explore architecture, state persistence, and backend logic.

---

## 🚀 Features

- Add, edit, and delete financial transactions  
- Transaction history overview  
- Budget management with four custom categories: reserve, available funds, rent, and taxes — tailored for personal needs with manual adjustment capability  
- Statistics with filters by date range, transaction type (expense, income), and categories  
- Web interface consisting of 5 pages  
- Data persisted in a MySQL database  

---

## 🛠️ Tech Stack

- Python 3.10  
- Flask  
- MySQL  
- PyMySQL  
- Pydantic  
- Jinja2 (HTML templating)  
- JavaScript (client-side scripting)  

---

## 🧱 Architecture Overview

The project is organized into several logical layers for clarity and maintainability:

- **Application** — business logic and services  
- **Domain** — core models and interfaces  
- **Infrastructure** — database access and logging  
- **Interface** — web API and routing  

The web frontend assets (CSS, JS, templates) are located under the `web/` folder.  
`main.py` serves as the application entry point.

---

## ⚙️ Setup

The project is designed to run locally with Python and a configured MySQL database.  
Database schema is assumed to be pre-created.  
Environment variables are used for configuration (e.g., database credentials).

---

## 🔒 Notes

- No migration system is used; table definitions are static.  
- The app uses a `.env` configuration file (not included in the repo).  
