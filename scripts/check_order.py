"""
This script checks that the categories in the README.md file are sorted.

License: MIT License (see scripts/LICENSE).
"""

from pathlib import Path
import locale
import re
import sys

TITLE_REGEX = re.compile(r"^(#+) (.+)$")


class InvalidCategoryError(Exception):
    pass


class CategoryNotFoundError(Exception):
    pass


class SubCategoriesNotFoundError(Exception):
    pass


class IncorrectLastSubcategoryError(Exception):
    pass


class IncorrectSubcategoriesOrderError(Exception):
    pass


def extract_subcategories(content: str, main_category: str):
    match = TITLE_REGEX.match(main_category)
    if not match:
        raise InvalidCategoryError

    lines = content.splitlines()
    main_category_level = len(match.group(1))
    try:
        main_category_start = lines.index(main_category)
    except ValueError:
        raise CategoryNotFoundError

    sub_categories = []
    for i in range(main_category_start + 1, len(lines)):
        line = lines[i]
        match = TITLE_REGEX.match(line)
        if not match:
            continue

        header_level = len(match.group(1))
        title = match.group(2)

        if header_level > main_category_level + 1:
            # It's a sub-sub-category, skip it.
            continue

        if header_level <= main_category_level:
            # It's a new category, stop.
            break

        sub_categories.append(title)

    return sub_categories


def check_subcategories_order(
    content: str, main_category: str, last_subcategory: str | None = None
):
    sub_categories = extract_subcategories(content, main_category)
    if not sub_categories:
        raise SubCategoriesNotFoundError

    if last_subcategory:
        index_last_subcategory = None
        try:
            index_last_subcategory = sub_categories.index(last_subcategory)
        except ValueError:
            # TODO: should this be an error?
            print(
                f'Categoría "{main_category}" no tiene la sub-categoría "{last_subcategory}".'
            )

        if index_last_subcategory:
            if index_last_subcategory != len(sub_categories) - 1:
                raise IncorrectLastSubcategoryError
            sub_categories.pop()

    # Sort categories using spanish locale.
    locale.setlocale(locale.LC_ALL, "es_ES")
    sorted_categories = sorted(sub_categories, key=locale.strxfrm)
    # Reset locale.
    locale.setlocale(locale.LC_ALL, "")

    if sorted_categories == sub_categories:
        return

    # TODO: Move these messages to the caller.
    print(f'Las sub-categorías de "{main_category}" no están ordenadas.')

    for i in range(len(sub_categories)):
        if sub_categories[i] != sorted_categories[i]:
            print(f"Primera categoría desordenada: {sub_categories[i]}")
            print(f"En su lugar debería estar: {sorted_categories[i]}")
            break

    print("Orden correcto:")
    for category in sorted_categories:
        print(f"- {category}")

    raise IncorrectSubcategoriesOrderError


def main():
    file = Path("README.md")
    content = file.read_text()
    category = "## Software"
    last_subcategory = "Otros"
    try:
        check_subcategories_order(content, category, last_subcategory)
        print("Sub-categorías están ordenadas correctamente.")
    except InvalidCategoryError:
        print(f'Categoría "{category}" no es un título válido (## Título).')
        sys.exit(1)
    except CategoryNotFoundError:
        print(f'Categoría "{category}" no encontrada.')
        sys.exit(1)
    except SubCategoriesNotFoundError:
        print(f'Categoría "{category}" no tiene sub-categorías.')
        sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
