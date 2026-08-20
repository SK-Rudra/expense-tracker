from app.extensions import db
from app.models import Category, User


DEFAULT_CATEGORIES = {
    "income": (
        "Salary",
        "Freelance",
        "Investments",
        "Other Income",
    ),
    "expense": (
        "Food",
        "Transport",
        "Housing",
        "Utilities",
        "Entertainment",
        "Health",
        "Shopping",
        "Education",
        "Other Expense",
    ),
}


def ensure_default_categories(user: User) -> int:
    existing_categories = {
        (category.name.casefold(), category.kind)
        for category in user.categories
    }

    added_count = 0

    for kind, category_names in DEFAULT_CATEGORIES.items():
        for name in category_names:
            category_key = (name.casefold(), kind)

            if category_key in existing_categories:
                continue

            category = Category(
                name=name,
                kind=kind,
                user=user,
            )

            db.session.add(category)
            existing_categories.add(category_key)
            added_count += 1

    return added_count