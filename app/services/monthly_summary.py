from datetime import date
from decimal import Decimal

from sqlalchemy import func

from app.extensions import db
from app.models import Category, Transaction


def get_monthly_summary(user_id, reference_date=None):
    current_date = reference_date or date.today()
    month_start = current_date.replace(day=1)

    if current_date.month == 12:
        next_month_start = date(current_date.year + 1, 1, 1)
    else:
        next_month_start = date(
            current_date.year,
            current_date.month + 1,
            1,
        )

    monthly_totals = db.session.execute(
        db.select(
            Category.kind,
            func.sum(Transaction.amount),
        )
        .join(
            Transaction,
            Transaction.category_id == Category.id,
        )
        .where(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= month_start,
            Transaction.transaction_date < next_month_start,
        )
        .group_by(Category.kind)
    ).all()

    totals = {
        kind: total
        for kind, total in monthly_totals
    }

    income = totals.get("income", Decimal("0.00"))
    expenses = totals.get("expense", Decimal("0.00"))

    return {
        "income": income,
        "expenses": expenses,
        "balance": income - expenses,
        "month_start": month_start,
        "next_month_start": next_month_start,
    }