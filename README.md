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

### 1. Install the driver

```bash
pip install mysql-connector-python
```

Tkinter ships with Python on Windows and macOS. On Linux: `sudo apt install python3-tk`.

### 2. Create the database and user

Run once in MySQL as root:

```sql
CREATE DATABASE library;

CREATE USER 'libraryuser'@'localhost' IDENTIFIED BY 'library123';
GRANT ALL PRIVILEGES ON library.* TO 'libraryuser'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Run

```bash
python library_management_mysql.py   # console version
python library_gui.py                # GUI version
```

The `books` table is created automatically on startup.

## Database

### Table definition

```sql
CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    author VARCHAR(100) NOT NULL,
    isbn VARCHAR(20) NOT NULL UNIQUE,
    category VARCHAR(50),
    total_copies INT NOT NULL DEFAULT 1,
    available_copies INT NOT NULL DEFAULT 1
);
```

```sql
DESCRIBE books;
```

```
+------------------+--------------+------+-----+---------+----------------+
| Field            | Type         | Null | Key | Default | Extra          |
+------------------+--------------+------+-----+---------+----------------+
| id               | int          | NO   | PRI | NULL    | auto_increment |
| title            | varchar(150) | NO   |     | NULL    |                |
| author           | varchar(100) | NO   |     | NULL    |                |
| isbn             | varchar(20)  | NO   | UNI | NULL    |                |
| category         | varchar(50)  | YES  |     | NULL    |                |
| total_copies     | int          | NO   |     | 1       |                |
| available_copies | int          | NO   |     | 1       |                |
+------------------+--------------+------+-----+---------+----------------+
```

**Add books (INSERT)**

```sql
INSERT INTO books (title, author, isbn, category, total_copies, available_copies) VALUES
 ('Wings of Fire', 'A.P.J. Abdul Kalam', '9788173711466', 'Autobiography', 3, 3),
 ('The Alchemist', 'Paulo Coelho', '9780061122415', 'Fiction', 2, 2),
 ('Malgudi Days', 'R.K. Narayan', '9780143039655', 'Fiction', 1, 1);
```

**View all books (SELECT)**

```sql
SELECT * FROM books;
```

```
+----+---------------+--------------------+---------------+---------------+--------------+------------------+
| id | title         | author             | isbn          | category      | total_copies | available_copies |
+----+---------------+--------------------+---------------+---------------+--------------+------------------+
|  1 | Wings of Fire | A.P.J. Abdul Kalam | 9788173711466 | Autobiography |            3 |                3 |
|  2 | The Alchemist | Paulo Coelho       | 9780061122415 | Fiction       |            2 |                2 |
|  3 | Malgudi Days  | R.K. Narayan       | 9780143039655 | Fiction       |            1 |                1 |
+----+---------------+--------------------+---------------+---------------+--------------+------------------+
```

**Search by ISBN**

```sql
SELECT * FROM books WHERE isbn = '9788173711466';
```

```
+----+---------------+--------------------+---------------+---------------+--------------+------------------+
| id | title         | author             | isbn          | category      | total_copies | available_copies |
+----+---------------+--------------------+---------------+---------------+--------------+------------------+
|  1 | Wings of Fire | A.P.J. Abdul Kalam | 9788173711466 | Autobiography |            3 |                3 |
+----+---------------+--------------------+---------------+---------------+--------------+------------------+
```

**Search by keyword**

```sql
SELECT id, title, author, isbn, category, total_copies, available_copies
FROM books
WHERE title LIKE '%fiction%' OR author LIKE '%fiction%'
   OR isbn LIKE '%fiction%' OR category LIKE '%fiction%'
ORDER BY id;
```

```
+----+---------------+--------------+---------------+----------+--------------+------------------+
| id | title         | author       | isbn          | category | total_copies | available_copies |
+----+---------------+--------------+---------------+----------+--------------+------------------+
|  2 | The Alchemist | Paulo Coelho | 9780061122415 | Fiction  |            2 |                2 |
|  3 | Malgudi Days  | R.K. Narayan | 9780143039655 | Fiction  |            1 |                1 |
+----+---------------+--------------+---------------+----------+--------------+------------------+
```

**Issue a book (UPDATE)**

```sql
UPDATE books SET available_copies = available_copies - 1
WHERE isbn = '9788173711466' AND available_copies > 0;
```

```
+----+---------------+--------------+------------------+
| id | title         | total_copies | available_copies |
+----+---------------+--------------+------------------+
|  1 | Wings of Fire |            3 |                2 |
+----+---------------+--------------+------------------+
```

**Return a book (UPDATE)**

```sql
UPDATE books SET available_copies = available_copies + 1
WHERE isbn = '9788173711466' AND available_copies < total_copies;
```

```
+----+---------------+--------------+------------------+
| id | title         | total_copies | available_copies |
+----+---------------+--------------+------------------+
|  1 | Wings of Fire |            3 |                3 |
+----+---------------+--------------+------------------+
```

**Update book details (UPDATE)**

```sql
UPDATE books SET title = 'Wings of Fire (Updated)', category = 'Biography'
WHERE isbn = '9788173711466';
```

```
+----+-------------------------+--------------------+---------------+-----------+--------------+------------------+
| id | title                   | author             | isbn          | category  | total_copies | available_copies |
+----+-------------------------+--------------------+---------------+-----------+--------------+------------------+
|  1 | Wings of Fire (Updated) | A.P.J. Abdul Kalam | 9788173711466 | Biography |            3 |                3 |
+----+-------------------------+--------------------+---------------+-----------+--------------+------------------+
```

**Delete a book (DELETE)**

```sql
DELETE FROM books WHERE isbn = '9780061122415';
SELECT * FROM books;
```

```
+----+-------------------------+--------------------+---------------+-----------+--------------+------------------+
| id | title                   | author             | isbn          | category  | total_copies | available_copies |
+----+-------------------------+--------------------+---------------+-----------+--------------+------------------+
|  1 | Wings of Fire (Updated) | A.P.J. Abdul Kalam | 9788173711466 | Biography |            3 |                3 |
|  3 | Malgudi Days            | R.K. Narayan       | 9780143039655 | Fiction   |            1 |                1 |
+----+-------------------------+--------------------+---------------+-----------+--------------+------------------+
```

**Duplicate ISBN (error case)**

The `UNIQUE` constraint on `isbn` rejects a second book with the same ISBN. Both apps catch this and show a friendly message.

```sql
INSERT INTO books (title, author, isbn, category) VALUES ('Dup', 'X', '9788173711466', 'Fiction');
```

```
ERROR 1062 (23000): Duplicate entry '9788173711466' for key 'books.isbn'
```

## Sample Run

```
Database Connected Successfully!

===== LIBRARY MANAGEMENT SYSTEM =====
1. Add Book
2. View Books
3. Search Book
4. Update Book
5. Delete Book
6. Issue Book
7. Return Book
8. Exit
Enter your choice: 1
Enter book title: Wings of Fire
Enter author name: A.P.J. Abdul Kalam
Enter ISBN: 9788173711466
Enter category: Autobiography
Enter number of copies: 3
Book added successfully!

...
Enter your choice: 2

========== BOOK DETAILS ==========
ID               : 1
Title            : Wings of Fire
Author           : A.P.J. Abdul Kalam
ISBN             : 9788173711466
Category         : Autobiography
Total Copies     : 3
Available Copies : 3
-------------------------------------

...
Enter your choice: 6
Enter ISBN of the book to issue: 9788173711466
Book issued successfully!

...
Enter your choice: 3
Enter ISBN to search: 9788173711466

Book Found!
ID               : 1
Title            : Wings of Fire
Author           : A.P.J. Abdul Kalam
ISBN             : 9788173711466
Category         : Autobiography
Total Copies     : 3
Available Copies : 2
-------------------------------------

...
Enter your choice: 1
Enter book title: Wrong Duplicate
Enter author name: X
Enter ISBN: 9788173711466
Enter category: Fiction
Enter number of copies: 1
A book with this ISBN already exists!

...
Enter your choice: 8
Thank you!
Program exited.
```

## Future Improvements

- Members table to track who borrowed which book
- Due dates and fine calculation
- Login for librarian and student roles
- Flask web version
- Read database credentials from environment variables
