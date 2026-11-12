
import sqlite3

DB_NAME = "bank.db"


# 데이터베이스 연결
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# 테이블 생성 및 초기 데이터 저장
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            balance INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO accounts
        (account_id, name, balance)
        VALUES (1001, '홍길동', 500000)
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO accounts
        (account_id, name, balance)
        VALUES (1002, '김철수', 1000000)
    """)

    conn.commit()
    conn.close()


# 계좌 전체 조회
def find_all_accounts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM accounts")
    result = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return result


# 특정 계좌 조회
def find_account(account_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM accounts WHERE account_id = ?",
        (account_id,)
    )

    result = cursor.fetchone()
    conn.close()

    return dict(result) if result else None


# 입출금 처리
def update_balance(account_id, amount, transaction_type):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute(
            "SELECT balance FROM accounts WHERE account_id = ?",
            (account_id,)
        )

        account = cursor.fetchone()

        if account is None:
            conn.rollback()
            return None, "계좌가 없습니다."

        balance = account["balance"]

        if amount <= 0:
            conn.rollback()
            return None, "금액은 0보다 커야 합니다."

        if transaction_type == "withdraw" and balance < amount:
            conn.rollback()
            return None, "잔액이 부족합니다."

        if transaction_type == "deposit":
            new_balance = balance + amount
        else:
            new_balance = balance - amount

        cursor.execute(
            "UPDATE accounts SET balance = ? WHERE account_id = ?",
            (new_balance, account_id)
        )

        cursor.execute("""
            INSERT INTO transactions
            (account_id, type, amount)
            VALUES (?, ?, ?)
        """, (account_id, transaction_type, amount))

        conn.commit()
        return new_balance, None

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# 거래 내역 조회
def find_transactions(account_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM transactions
        WHERE account_id = ?
        ORDER BY id DESC
    """, (account_id,))

    result = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return result
