from decimal import Decimal

from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from app.extensions import db
from app.models import Transaction
from app.services.monthly_summary import get_monthly_summary


main = Blueprint("main", __name__)


@main.route("/")
def home():
    if current_user.is_authenticated:
        summary = get_monthly_summary(current_user.id)
    else:
        summary = {
            "income": Decimal("0.00"),
            "expenses": Decimal("0.00"),
            "balance": Decimal("0.00"),
        }

    return render_template(
        "home.html",
        income=summary["income"],
        expenses=summary["expenses"],
        balance=summary["balance"],
    )


@main.route("/health")
def health():
    return {"status": "ok"}, 200


@main.route("/dashboard")
@login_required
def dashboard():
    summary = get_monthly_summary(current_user.id)

    month_start = summary["month_start"]
    next_month_start = summary["next_month_start"]

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
        income=summary["income"],
        expenses=summary["expenses"],
        balance=summary["balance"],
        monthly_transaction_count=monthly_transaction_count or 0,
        recent_transactions=recent_transactions,
        current_month=month_start.strftime("%B %Y"),
    )