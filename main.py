
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from database import (
    init_db,
    find_all_accounts,
    find_account,
    update_balance,
    find_transactions
)

app = FastAPI()

# 서버 시작 시 데이터베이스 초기화
@app.on_event("startup")
def startup():
    init_db()


# 입출금 요청 데이터
class TransactionRequest(BaseModel):
    amount: int


# 전체 계좌 조회
@app.get("/accounts")
def get_accounts():
    return find_all_accounts()


# 특정 계좌 조회
@app.get("/accounts/{account_id}")
def get_account(account_id: int):
    account = find_account(account_id)

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="계좌가 없습니다."
        )

    return account


# 입금
@app.post("/accounts/{account_id}/deposit")
def deposit(account_id: int, request: TransactionRequest):

    balance, error = update_balance(
        account_id,
        request.amount,
        "deposit"
    )

    if error:
        raise HTTPException(status_code=400, detail=error)

    return {
        "message": "입금 완료",
        "balance": balance
    }


# 출금
@app.post("/accounts/{account_id}/withdraw")
def withdraw(account_id: int, request: TransactionRequest):

    balance, error = update_balance(
        account_id,
        request.amount,
        "withdraw"
    )

    if error:
        raise HTTPException(status_code=400, detail=error)

    return {
        "message": "출금 완료",
        "balance": balance
    }


# 거래 내역 조회
@app.get("/accounts/{account_id}/transactions")
def get_transactions(account_id: int):

    account = find_account(account_id)

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="계좌가 없습니다."
        )

    return find_transactions(account_id)
