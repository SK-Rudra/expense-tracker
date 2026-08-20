from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Category, Transaction
from app.transactions import transactions
from app.transactions.forms import CategoryForm, TransactionForm


def get_owned_transaction_or_404(transaction_id: int) -> Transaction:
    return db.one_or_404(
        db.select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
        )
    )


def get_owned_category_or_404(category_id: int) -> Category:
    return db.one_or_404(
        db.select(Category).where(
            Category.id == category_id,
            Category.user_id == current_user.id,
        )
    )


@transactions.route("/")
@login_required
def index():
    user_transactions = db.session.scalars(
        db.select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(
            Transaction.transaction_date.desc(),
            Transaction.id.desc(),
        )
    ).all()

    return render_template(
        "transactions/index.html",
        transactions=user_transactions,
    )


@transactions.route("/add", methods=["GET", "POST"])
@login_required
def create():
    form = TransactionForm()

    if form.validate_on_submit():
        category = get_owned_category_or_404(form.category_id.data)

        transaction = Transaction(
            amount=form.amount.data,
            description=form.description.data.strip(),
            transaction_date=form.transaction_date.data,
            user=current_user,
            category=category,
        )

        db.session.add(transaction)
        db.session.commit()

        flash("Transaction added successfully.", "success")
        return redirect(url_for("transactions.index"))

    return render_template(
        "transactions/form.html",
        form=form,
        title="Add transaction",
    )


@transactions.route("/<int:transaction_id>/edit", methods=["GET", "POST"])
@login_required
def edit(transaction_id: int):
    transaction = get_owned_transaction_or_404(transaction_id)
    form = TransactionForm()

    if form.validate_on_submit():
        category = get_owned_category_or_404(form.category_id.data)

        transaction.amount = form.amount.data
        transaction.description = form.description.data.strip()
        transaction.transaction_date = form.transaction_date.data
        transaction.category = category

        db.session.commit()

        flash("Transaction updated successfully.", "success")
        return redirect(url_for("transactions.index"))

    if request.method == "GET":
        form.kind.data = transaction.category.kind
        form.category_id.data = transaction.category_id
        form.amount.data = transaction.amount
        form.description.data = transaction.description
        form.transaction_date.data = transaction.transaction_date

    return render_template(
        "transactions/form.html",
        form=form,
        title="Edit transaction",
        transaction=transaction,
    )


@transactions.route("/<int:transaction_id>/delete", methods=["POST"])
@login_required
def delete(transaction_id: int):
    transaction = get_owned_transaction_or_404(transaction_id)

    db.session.delete(transaction)
    db.session.commit()

    flash("Transaction deleted successfully.", "success")
    return redirect(url_for("transactions.index"))


@transactions.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    form = CategoryForm()

    if form.validate_on_submit():
        category = Category(
            name=form.name.data.strip(),
            kind=form.kind.data,
            user=current_user,
        )

        db.session.add(category)
        db.session.commit()

        flash("Category added successfully.", "success")
        return redirect(url_for("transactions.categories"))

    user_categories = db.session.scalars(
        db.select(Category)
        .where(Category.user_id == current_user.id)
        .order_by(Category.kind, Category.name)
    ).all()

    return render_template(
        "transactions/categories.html",
        form=form,
        categories=user_categories,
    )


@transactions.route(
    "/categories/<int:category_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit_category(category_id: int):
    category = get_owned_category_or_404(category_id)
    form = CategoryForm(category=category, obj=category)

    if form.validate_on_submit():
        has_transactions = db.session.scalar(
            db.select(Transaction.id)
            .where(Transaction.category_id == category.id)
            .limit(1)
        )

        if has_transactions is not None and form.kind.data != category.kind:
            flash(
                "You cannot change the type of a category that has transactions.",
                "danger",
            )
        else:
            category.name = form.name.data.strip()
            category.kind = form.kind.data
            db.session.commit()

            flash("Category updated successfully.", "success")
            return redirect(url_for("transactions.categories"))

    return render_template(
        "transactions/category_form.html",
        form=form,
        category=category,
        title="Edit category",
    )


@transactions.route(
    "/categories/<int:category_id>/delete",
    methods=["POST"],
)
@login_required
def delete_category(category_id: int):
    category = get_owned_category_or_404(category_id)

    has_transactions = db.session.scalar(
        db.select(Transaction.id)
        .where(Transaction.category_id == category.id)
        .limit(1)
    )

    if has_transactions is not None:
        flash(
            "This category cannot be deleted because it has transactions.",
            "danger",
        )
    else:
        db.session.delete(category)
        db.session.commit()
        flash("Category deleted successfully.", "success")

    return redirect(url_for("transactions.categories"))