import re

from django.db import migrations


PUBLIC_TYPES = {
    "air_conditioner",
    "air_conditioner_set",
    "multi_split",
    "semi_industrial",
    "heat_pump",
}

OUTDOOR_PREFIXES = ("MUZ", "MUY", "MXZ", "SUZ")

BTU_CLASS_TO_AREA = {
    7: 20,
    9: 25,
    12: 35,
    18: 50,
    24: 70,
    30: 80,
    36: 100,
    48: 140,
    60: 160,
}

KW_CLASS_TO_AREA = {
    15: 15,
    18: 20,
    20: 20,
    22: 22,
    25: 25,
    35: 35,
    42: 42,
    50: 50,
    60: 60,
    71: 70,
    80: 80,
    100: 100,
    125: 125,
    140: 140,
    160: 160,
}


def first_model_token(model):
    return re.split(r"[\s+/]", (model or "").strip().upper(), maxsplit=1)[0]


def first_number(value):
    text = str(value or "").replace("\xa0", " ").replace(",", ".")
    match = re.search(r"\d+(?:\.\d+)?", text)
    return float(match.group(0)) if match else None


def round_area(value):
    if value <= 0:
        return 0
    return int(round(value / 5) * 5) or 5


def area_from_capacity(product):
    specs = product.specs or {}
    kw = first_number(specs.get("capacity_cooling"))
    if kw is None:
        return None
    if 1 <= kw <= 20:
        return round_area(kw * 10)
    if 1000 <= kw <= 60000:
        return BTU_CLASS_TO_AREA.get(round(kw / 1000))
    return None


def area_from_model(product):
    model = first_model_token(product.model)
    for class_value, area in sorted(BTU_CLASS_TO_AREA.items(), key=lambda item: -item[0]):
        if re.search(rf"(?<!\d)0?{class_value}(?!\d)", model):
            return area
    for class_value, area in sorted(KW_CLASS_TO_AREA.items(), key=lambda item: -item[0]):
        if re.search(rf"(?<!\d){class_value}(?!\d)", model):
            return area
    return None


def infer_area_and_hide_standalone_outdoor_units(apps, schema_editor):
    CatalogProduct = apps.get_model("catalog", "CatalogProduct")

    for product in CatalogProduct.objects.all().iterator():
        update_fields = []
        token = first_model_token(product.model)

        if token.startswith(OUTDOOR_PREFIXES):
            if product.product_type != "outdoor_unit":
                product.product_type = "outdoor_unit"
                update_fields.append("product_type")
            if product.is_indexable:
                product.is_indexable = False
                update_fields.append("is_indexable")

        if product.recommended_area_m2 is None and product.product_type in PUBLIC_TYPES:
            area = area_from_capacity(product) or area_from_model(product)
            if area:
                product.recommended_area_m2 = area
                update_fields.append("recommended_area_m2")

        if update_fields:
            product.save(update_fields=sorted(set(update_fields)))


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0008_cleanup_accessory_catalog_visibility"),
    ]

    operations = [
        migrations.RunPython(infer_area_and_hide_standalone_outdoor_units, noop_reverse),
    ]
