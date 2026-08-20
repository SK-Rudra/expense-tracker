from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from flask_login import current_user
from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import (
    DateField,
    DecimalField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Length,
    NumberRange,
    ValidationError,
)

from app.extensions import db
from app.models import Category


class CategoryForm(FlaskForm):
    name = StringField(
        "Category name",
        validators=[
            DataRequired(),
            Length(min=2, max=80),
        ],
    )
    kind = SelectField(
        "Category type",
        choices=[
            ("expense", "Expense"),
            ("income", "Income"),
        ],
        validators=[InputRequired()],
    )
    submit = SubmitField("Save category")

    def __init__(
        self,
        *args,
        category: Category | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.category = category

    def validate_name(self, name) -> None:
        name.data = name.data.strip()

        existing_category = db.session.scalar(
            db.select(Category).where(
                Category.user_id == current_user.id,
                func.lower(Category.name) == name.data.lower(),
                Category.kind == self.kind.data,
            )
        )

        if (
            existing_category is not None
            and (
                self.category is None
                or existing_category.id != self.category.id
            )
        ):
            raise ValidationError(
                "You already have a category with this name and type."
            )


class TransactionForm(FlaskForm):
    kind = SelectField(
        "Transaction type",
        choices=[
            ("expense", "Expense"),
            ("income", "Income"),
        ],
        validators=[InputRequired()],
    )
    category_id = SelectField(
        "Category",
        coerce=int,
        validators=[InputRequired()],
    )
    amount = DecimalField(
        "Amount",
        places=2,
        rounding=ROUND_HALF_UP,
        validators=[
            InputRequired(),
            NumberRange(
                min=Decimal("0.01"),
                max=Decimal("9999999999.99"),
            ),
        ],
    )
    description = StringField(
        "Description",
        validators=[
            DataRequired(),
            Length(min=2, max=255),
        ],
    )
    transaction_date = DateField(
        "Date",
        default=date.today,
        validators=[InputRequired()],
    )
    submit = SubmitField("Save transaction")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if current_user.is_authenticated:
            categories = db.session.scalars(
                db.select(Category)
                .where(Category.user_id == current_user.id)
                .order_by(Category.kind, Category.name)
            ).all()

            self.category_id.choices = [
                (
                    category.id,
                    f"{category.kind.title()} — {category.name}",
                )
                for category in categories
            ]
        else:
            self.category_id.choices = []

    def validate_category_id(self, category_id) -> None:
        category = db.session.scalar(
            db.select(Category).where(
                Category.id == category_id.data,
                Category.user_id == current_user.id,
            )
        )

        if category is None:
            raise ValidationError("Please select a valid category.")

        if category.kind != self.kind.data:
            raise ValidationError(
                "The selected category does not match the transaction type."
            )