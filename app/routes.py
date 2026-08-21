from datetime import date
from decimal import Decimal

from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from app.extensions import db
from app.models import Category, Transaction


main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("home.html")

@main.route("/health")
def health():
    return {"status": "ok"}, 200

@main.route("/dashboard")
@login_required
def dashboard():
    today = date.today()
    month_start = today.replace(day=1)

    if today.month == 12:
        next_month_start = date(today.year + 1, 1, 1)
    else:
        next_month_start = date(
            today.year,
            today.month + 1,
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
            Transaction.user_id == current_user.id,
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
    balance = income - expenses

    monthly_transaction_count = db.session.scalar(
        db.select(func.count(Transaction.id)).where(
            Transaction.user_id == current_user.id,
            Transaction.transaction_date >= month_start,
            Transaction.transaction_date < next_month_start,
        )
    )

    recent_transactions = db.session.scalars(
        db.select(Transaction)
        .options(selectinload(Transaction.category))
        .where(Transaction.user_id == current_user.id)
        .order_by(
            Transaction.transaction_date.desc(),
            Transaction.id.desc(),
        )
        .limit(5)
    ).all()

    return render_template(
        "dashboard.html",
        income=income,
        expenses=expenses,
        balance=balance,
        monthly_transaction_count=monthly_transaction_count or 0,
        recent_transactions=recent_transactions,
        current_month=month_start.strftime("%B %Y"),
    )