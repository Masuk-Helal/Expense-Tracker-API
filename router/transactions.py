from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session
from typing import Annotated, Optional, Literal
from datetime import date as date_type
from database import SessionLocal
from models import Transactions
from fastapi.responses import JSONResponse
from router.auth import get_current_user

router = APIRouter(prefix='/transactions', tags=['transactions'])


class Transaction(BaseModel):
    title: str
    amount: float = Field(gt=0)
    type: Literal['income', 'expense']
    category: str
    date: date_type


class TransactionUpdate(BaseModel):
    title: Optional[str] = Field(default=None)
    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[Literal['income', 'expense']] = Field(default=None)
    category: Optional[str] = Field(default=None)
    date: Optional[date_type] = Field(default=None)


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    amount: float
    type: str
    category: str
    date: date_type
    owner_id: int


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post('', response_model=TransactionOut, status_code=201)
def create_transaction(user: user_dependency, db: db_dependency, new_transaction: Transaction):

    transaction_model = Transactions(**new_transaction.model_dump(), owner_id=user.get('id'))
    db.add(transaction_model)
    db.commit()
    db.refresh(transaction_model)

    return transaction_model


@router.get('', response_model=list[TransactionOut])
def get_transactions(user: user_dependency, db: db_dependency):

    return db.query(Transactions).filter(Transactions.owner_id == user.get('id')).all()


@router.get('/filter', response_model=list[TransactionOut])
def filter_transactions(
    user: user_dependency,
    db: db_dependency,
    type: Optional[str] = None,
    category: Optional[str] = None,
    minimum_amount: Optional[float] = None,
    maximum_amount: Optional[float] = None,
):

    query = db.query(Transactions).filter(Transactions.owner_id == user.get('id'))

    if type is not None:
        query = query.filter(Transactions.type == type)
    if category is not None:
        query = query.filter(Transactions.category == category)
    if minimum_amount is not None:
        query = query.filter(Transactions.amount >= minimum_amount)
    if maximum_amount is not None:
        query = query.filter(Transactions.amount <= maximum_amount)

    return query.all()


@router.get('/{transaction_id}', response_model=TransactionOut)
def get_transaction(user: user_dependency, db: db_dependency, transaction_id: int):

    transaction = db.query(Transactions).filter(Transactions.owner_id == user.get('id')).filter(Transactions.id == transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail='Transaction not found')

    return transaction


@router.put('/{transaction_id}', response_model=TransactionOut)
def update_transaction(user: user_dependency, db: db_dependency, transaction_id: int, update_transaction: TransactionUpdate):

    transaction = db.query(Transactions).filter(Transactions.owner_id == user.get('id')).filter(Transactions.id == transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail='Transaction not found')

    update_data = update_transaction.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(transaction, key, value)

    db.commit()
    db.refresh(transaction)

    return transaction


@router.delete('/{transaction_id}')
def delete_transaction(user: user_dependency, db: db_dependency, transaction_id: int):

    transaction = db.query(Transactions).filter(Transactions.owner_id == user.get('id')).filter(Transactions.id == transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail='Transaction not found')

    db.query(Transactions).filter(Transactions.id == transaction_id).delete()
    db.commit()

    return JSONResponse(status_code=200, content={'message': 'Transaction deleted successfully'})
