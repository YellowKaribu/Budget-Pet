# Budget Pet

Budget Pet is a web-based personal finance tracker that uses a MySQL database for reliable data storage. Developed as part of my practical learning journey, this application provides an interactive interface to manage budgets, track income and expenses, and keep financial records organized.

> ⚠️ **Warning:** This is a learning project in a very early and experimental stage. It is not a production-ready application. Expect incomplete features, unstable behavior, and a lot of rough edges — I'm building this as I learn.


---

Current Features

    Web interface for tracking income, expenses, and budget management.

    Data stored reliably in a MySQL database.

    Interactive pages to view transaction logs and current balance.

    Support for multiple expense categories with user-friendly labels.

    Backend logic structured for scalability and maintainability.

Architecture

Budget Pet is implemented as a web-based monolithic application with:

    backend built in Python handling business logic,

    MySQL database for persistent storage of budget state and transactions,

    web server providing interactive frontend access,

    clear separation between core logic and infrastructure layers,

    designed for easy future expansion and feature additions.

Requirements

    Python 3.11+

    MySQL server

---

## Running the Database and Web API

Before using the app, ensure your MySQL database is running and properly configured.

To start the backend web API server, run:

```bash
python3 web_api.py
```

This will launch the web application locally. Open your browser and go to:

```bash http://127.0.0.1:5000 ```

(Adjust the port if your server uses a different one.)
