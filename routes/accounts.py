from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from schemas.models import Account
from utils.cruds.account_crud import (
    account_create,
    account_delete,
    account_get_one,
    account_update,
    accounts_get_all,
)

router = APIRouter(tags=["accounts"])


@router.post("/", response_model=Account, status_code=status.HTTP_201_CREATED)
async def create_account(
    request: Account,
    db: Session = Depends(get_db),
):
    account = Account(
        id=request.id,
        balance=request.balance,
        status=request.status,
        state=request.state,
        created_at=request.created_at,
        updated_at=request.updated_at,
    )
    return await account_create(db, account)


@router.get("/", response_model=List[Account])
async def read_accounts(db: Session = Depends(get_db)):
    return await accounts_get_all(db)


@router.get("/{account_id}", response_model=Account)
async def read_account(account_id: int, db: Session = Depends(get_db)):
    account = await account_get_one(db, account_id)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return account


@router.put("/{account_id}", response_model=Account)
async def update_account(account_id: int, account: Account, db: Session = Depends(get_db)):
    account = await account_update(db, account_id, account)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return account


@router.delete("/{account_id}", response_model=Account)
async def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = await account_delete(db, account_id)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return account
