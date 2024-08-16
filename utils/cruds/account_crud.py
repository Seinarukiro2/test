from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from database.models import Account


async def account_create(db: Session, account: Account):
    db_account = Account(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


async def account_delete(db: Session, account_id: int):
    account = db.query(Account).filter(Account.id == account_id).first()
    db.delete(account)
    db.commit()
    return account


async def account_get_one(db: Session, account_id: int):
    return db.query(Account).filter(Account.id == account_id).first()


async def account_update(db: Session, account_id: int, account: Account):
    db.query(Account).filter(Account.id == account_id).update(account.dict())
    db.commit()
    return db.query(Account).filter(Account.id == account_id).first()


async def accounts_get_all(db: Session):
    return db.query(Account).all()


async def account_get_by_status(db: Session, status: str):
    return db.query(Account).filter(Account.status == status).all()


async def accounts_get_by_last_game(db: Session, minutes: int, limit: [int, None]):
    time = datetime.now() - timedelta(minutes=minutes)

    if limit is None:
        return (
            db.query(Account)
            .filter(
                (Account.last_game <= time) | (Account.last_game == None),
                Account.status == "active",
                Account.work_now == False,
            )
            .all()
        )

    return (
        db.query(Account)
        .filter(
            (Account.last_game <= time) | (Account.last_game == None),
            Account.status == "active",
            Account.work_now == False,
        )
        .limit(limit)
        .all()
    )
