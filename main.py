
from fastapi import FastAPI, HTTPException
from psycopg.rows import dict_row

from database import get_connection
from models import BookCreate

app = FastAPI(title="Digital Library API")


@app.post("/books", status_code=201)
def create_book(book: BookCreate):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO books (title, author, price, is_available)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (
                    book.title,
                    book.author,
                    book.price,
                    book.is_available,
                ),
            )
            new_book = cur.fetchone()

    return {
        "message": "Book added",
        "id": new_book["id"],
    }


@app.get("/books")
def get_books():
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM books ORDER BY id")
            books = cur.fetchall()

    return books


@app.get("/books/{book_id}")
def get_book(book_id: int):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT * FROM books WHERE id = %s",
                (book_id,),
            )
            book = cur.fetchone()

    if book is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    return book
