import re

from django.db import migrations


PUBLIC_TYPES = {
    "air_conditioner",
    "air_conditioner_set",
    "multi_split",
    "semi_industrial",
    "heat_pump",
}

COLOR_DEFINITIONS = {
    "white": ("Білий", "#ffffff"),
    "black": ("Чорний", "#111111"),
    "silver": ("Сріблястий", "#c0c0c0"),
    "gray": ("Сірий", "#808080"),
    "gold": ("Золотий", "#d4af37"),
}

COLOR_ALIASES = {
    "WHITE": "white",
    "W": "white",
    "WP": "white",
    "NG": "white",
    "БІЛИЙ": "white",
    "БІЛОГО": "white",
    "BLACK": "black",
    "FULL BLACK": "black",
    "CARBON BLACK": "black",
    "B": "black",
    "FB": "black",
    "BL": "black",
    "BDK": "black",
    "ЧОРНИЙ": "black",
    "SILVER": "silver",
    "SC": "silver",
    "СРІБЛЯСТИЙ": "silver",
    "СРІБЛЯСТОГО": "silver",
    "GRAY": "gray",
    "GREY": "gray",
    "GRAPHITE": "gray",
    "СІРИЙ": "gray",
    "GOLD": "gold",
    "GD": "gold",
    "ЗОЛОТИЙ": "gold",
}

MODEL_SUFFIX_COLORS = {
    "-FB": "black",
    "-BL": "black",
    "-BDK": "black",
    "BDK": "black",
    "-B": "black",
    "-SC": "silver",
    "-GD": "gold",
    "-WP": "white",
    "-NG": "white",
    "-W": "white",
}


def first_model_token(model):
    return re.split(r"[\s+/]", (model or "").strip().upper(), maxsplit=1)[0]


def color_key_for(product):
    specs = product.specs or {}
    raw_color = str(specs.get("color") or "").strip().upper()
    if raw_color in COLOR_ALIASES:
        return COLOR_ALIASES[raw_color]

    text = " ".join(
        str(value or "").upper()
        for value in (
            specs.get("color"),
            product.series,
            product.description,
            product.model,
            product.main_image,
        )
    )
    for marker in sorted(COLOR_ALIASES, key=len, reverse=True):
        if len(marker) < 2:
            continue
        if re.search(rf"(?<![A-ZА-ЯІЇЄҐ0-9]){re.escape(marker)}(?![A-ZА-ЯІЇЄҐ0-9])", text):
            return COLOR_ALIASES[marker]

    model = first_model_token(product.model)
    for suffix, color_key in MODEL_SUFFIX_COLORS.items():
        if model.endswith(suffix):
            return color_key
    return "white"


def fill_catalog_product_colors(apps, schema_editor):
    CatalogProduct = apps.get_model("catalog", "CatalogProduct")
    Color = apps.get_model("catalog", "Color")

    colors = {}
    for color_key, (name, color_hash) in COLOR_DEFINITIONS.items():
        color, _ = Color.objects.get_or_create(hash=color_hash, defaults={"name": name})
        if color.name != name:
            color.name = name
            color.save(update_fields=["name"])
        colors[color_key] = color

    products = CatalogProduct.objects.filter(
        is_active=True,
        is_indexable=True,
        product_type__in=PUBLIC_TYPES,
    ).iterator()
    for product in products:
        if product.colors.exists():
            continue
        product.colors.add(colors[color_key_for(product)])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0009_infer_area_and_hide_standalone_outdoor_units"),
    ]

    operations = [
        migrations.RunPython(fill_catalog_product_colors, noop_reverse),
    ]
