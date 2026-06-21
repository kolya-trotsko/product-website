from django.db import migrations


ACCESSORY_MODELS = (
    "AM-MHI-01",
    "WI-FI USB IDEA_SARDIUS MT7682 (TR)",
    "WI-FI SMART KIT MIDEA EU-SK105",
)


def cleanup_accessory_catalog_visibility(apps, schema_editor):
    CatalogProduct = apps.get_model("catalog", "CatalogProduct")

    CatalogProduct.objects.filter(product_type="accessory").update(
        category="accessories",
        is_indexable=False,
    )

    CatalogProduct.objects.filter(model__in=ACCESSORY_MODELS).update(
        product_type="accessory",
        category="accessories",
        subcategory="",
        series="",
        is_indexable=False,
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0007_alter_conditionerorder_conditioner_and_more"),
    ]

    operations = [
        migrations.RunPython(cleanup_accessory_catalog_visibility, noop_reverse),
    ]
