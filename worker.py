import asyncio
import requests
import config
import random
import os

from aiohttp.client_exceptions import ContentTypeError
from sqlalchemy.orm import Session

from database.connection import SessionLocal, get_db
from database.models import Account
from utils.cruds.account_crud import accounts_get_by_last_game
from utils.logger import logger
from utils.vertus import Vertus
from dotenv import load_dotenv

load_dotenv()


async def start(thread: int, session_name: str, session_string: str, proxy: [str, None], db: Session):
    vertus = Vertus(session_name=session_name,
                    session_string=session_string, thread=thread, proxy=proxy)
    account = session_name + '.session'
    db_acc = db.query(Account).filter(Account.id == session_name).first()

    if await vertus.login():
        logger.success(f"Thread {thread} | {account} | Login")

        db.query(Account).filter(Account.id ==
                                 session_name).update({"work_now": True})
        db.commit()

        try:
            data = await vertus.get_data()

            if not await vertus.is_activated(data):
                wallet = await vertus.create_wallet()
                logger.success(f"Thread {thread} | {
                               account} | Create wallet: {wallet}")

            if await vertus.can_collect_first(data):
                amount = await vertus.first_collect()
                logger.success(f"Thread {thread} | {
                               account} | First collect {amount} VERT")

            if vertus.can_claim_daily_reward(data):
                status, claim_count = await vertus.claim_daily_reward()
                if status == 201:
                    logger.success(f"Thread {thread} | {
                                   account} | Claim daily reward: {claim_count} VERT!")
                else:
                    logger.error(f"Thread {thread} | {
                                 account} | Can't claim daily reward! Response {status}")

            storage = vertus.get_storage(data)

            if storage >= 0.003:
                status, balance = await vertus.collect()
                if status == 201:
                    logger.success(f"Thread {thread} | {
                                   account} | Collect VERT! New balance: {balance}")
                else:
                    logger.error(f"Thread {thread} | {
                                 account} | Can't collect VERT! Response {status}")
                    return

            balance = vertus.get_balance(data)
            farm, population = vertus.get_upgrades(data)

            if farm is None or farm > 10:
                farm = 9999
            if population is None or population > 10:
                population = 9999

            if farm < population and balance >= farm:
                upgrade = "farm"
            elif farm > population and balance >= population:
                upgrade = "population"
            elif farm == population and balance >= population:
                upgrade = "farm"
            else:
                upgrade = ""

            if upgrade and config.BUY_UPGRADE:
                status, balance = await vertus.upgrade(upgrade)
                if status == 201:
                    logger.success(f"Thread {thread} | {account} | Upgrade {
                                   upgrade}! New balance: {balance}")
                else:
                    logger.error(f"Thread {thread} | {account} | Can't upgrade {
                                 upgrade}! Response {status}")

            cards = None
            while config.BUY_CARD:
                await asyncio.sleep(random.uniform(*config.DELAYS['BUY_CARD']))
                card = await vertus.get_profitable_upgrade_card(balance, cards)
                if not card:
                    break

                status, balance, cards = await vertus.buy_upgrade_card(card['id'])
                if status == 201:
                    logger.success(
                        f"Thread {thread} | {account} | Buy card «{card['title']}» in «{
                            card['category']}»! New balance: {balance}"
                    )
                else:
                    logger.error(
                        f"Thread {thread} | {account} | Can't buy card «{card['title']}» in «{
                            card['category']}»! Response {status}: {balance}"
                    )

            data = await vertus.get_data()
            balance = vertus.get_balance(data)

            if db_acc.balance != balance:
                db.query(Account).filter(Account.id == session_name).update(
                    {"balance": balance, "last_game": vertus.current_datetime()}
                )
                db.commit()
                print(f"Thread {thread} | {
                      account} | Update balance: {balance}")

            # await asyncio.sleep(random.uniform(*config.DELAYS['REPEAT']))
        except ContentTypeError as e:
            logger.error(f"Thread {thread} | {account} | Error: {e}")
            await asyncio.sleep(15)

        except Exception as e:
            logger.error(f"Thread {thread} | {account} | Error: {e}")
            await asyncio.sleep(10)

        await vertus.logout()

        db.query(Account).filter(Account.id ==
                                 session_name).update({"work_now": False})
        db.commit()
    else:
        await vertus.logout()


async def main():
    db: Session = SessionLocal()
    backend_url = os.getenv("BACKEND_URL")
    get_accounts_url = f"{backend_url}/v1/internal/accounts/list"

    _accounts = await accounts_get_by_last_game(db, minutes=30, limit=10)

    response_accounts = requests.post(get_accounts_url, headers={
        "Content-Type": "application/json", 
        "access-token": os.getenv("ACCESS_TOKEN")
    }, json={
        "accounts_ids": [account.id for account in _accounts]
    })

    if response_accounts.status_code != 200:
        logger.error(f"Error: {response_accounts.json()}")
        return

    accounts_db = response_accounts.json().get("accounts", [])

    accounts = []
    for account in _accounts:
        acc_db = next(
            (acc for acc in accounts_db if acc["id"] == account.id), None)
        if acc_db:
            accounts.append(
                {
                    "account_id": acc_db["id"],
                    "session_string": acc_db["session"],
                    "proxy": acc_db["proxy"],
                }
            )

    if not accounts:
        logger.info("No accounts found!")
        return

    tasks = []
    for thread, account in enumerate(accounts):
        account_id, session_string, proxy = account.values()
        tasks.append(
            asyncio.create_task(
                start(session_name=account_id, session_string=session_string,
                      thread=thread, proxy=proxy, db=db)
            )
        )

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
