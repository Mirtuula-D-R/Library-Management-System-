# Library Management System

A library management application built with **Python** and **MySQL**, integrated with **GUI version**



## Features

- Add, view, search, update and delete books
- Issue a book (reduces available copies) and return a book (increases available copies)
- Duplicate ISBN protection
- Input validation (empty fields, invalid copy counts)
- Parameterized queries to prevent SQL injection
- GUI: live search by title, author, ISBN or category, plus red highlighting for out-of-stock books

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language  | Python 3 |
| Database  | MySQL 8.0 |
| Driver    | mysql-connector-python |
| GUI       | Tkinter |


## Setup

### Install the driver

```bash
pip install mysql-connector-python
```

## Database

**Create the database and user** (run once in MySQL as root):

   ```sql
   CREATE DATABASE IF NOT EXISTS library;
   CREATE USER IF NOT EXISTS 'libraryuser'@'localhost' IDENTIFIED BY 'library123';
   GRANT ALL PRIVILEGES ON library.* TO 'libraryuser'@'localhost';
   FLUSH PRIVILEGES;
   ```

**Run:**

   ```bash
   python Project.py
   ```

## Database Table

```sql
CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    author VARCHAR(100) NOT NULL,
    isbn VARCHAR(20) NOT NULL UNIQUE,
    category VARCHAR(50),
    total_copies INT NOT NULL DEFAULT 1,
    available_copies INT NOT NULL DEFAULT 1
);
```

## Usage

- **Add:** fill in the form and click **Add**.
- **Update / Delete:** click a book in the table, then use **Update** or **Delete**.
- **Issue / Return:** select a book and click **Issue** or **Return**.
- **Search:** type in the search box and press Enter.

## Future Improvements

- Members table to track who borrowed which book
- Due dates and fine calculation
- Login for librarian and student roles
- Flask web version
- Read database credentials from environment variables
