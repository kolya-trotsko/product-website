from django.conf import settings
from django.db import models

from ks_klimat_kh.order_status import (
    ORDER_STATUS_CANCELLED,
    ORDER_STATUS_CHOICES,
    ORDER_STATUS_DONE,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_NEW,
)


class Company(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="logos/", default=None, null=True, blank=True)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=100)
    hash = models.CharField(max_length=100, null=True, default=None)

    def __str__(self):
        return self.name


class CatalogProduct(models.Model):
    TYPE_AIR_CONDITIONER = "air_conditioner"
    TYPE_AIR_CONDITIONER_SET = "air_conditioner_set"
    TYPE_INDOOR_UNIT = "indoor_unit"
    TYPE_OUTDOOR_UNIT = "outdoor_unit"
    TYPE_PANEL = "panel"
    TYPE_ACCESSORY = "accessory"
    TYPE_VENTILATION = "ventilation"
    TYPE_HEAT_PUMP = "heat_pump"
    TYPE_MULTI_SPLIT = "multi_split"
    TYPE_SEMI_INDUSTRIAL = "semi_industrial"
    TYPE_OTHER = "other"
    TYPE_CHOICES = [
        (TYPE_AIR_CONDITIONER, "Кондиціонер"),
        (TYPE_AIR_CONDITIONER_SET, "Комплект кондиціонера"),
        (TYPE_INDOOR_UNIT, "Внутрішній блок"),
        (TYPE_OUTDOOR_UNIT, "Зовнішній блок"),
        (TYPE_PANEL, "Панель"),
        (TYPE_ACCESSORY, "Аксесуар"),
        (TYPE_VENTILATION, "Вентиляція"),
        (TYPE_HEAT_PUMP, "Тепловий насос"),
        (TYPE_MULTI_SPLIT, "Мульти-спліт"),
        (TYPE_SEMI_INDUSTRIAL, "Напівпромисловий"),
        (TYPE_OTHER, "Інше"),
    ]

    brand = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="catalog_products")
    name = models.CharField(max_length=255)
    model = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    source_key = models.CharField(max_length=255, unique=True, db_index=True)
    category = models.CharField(max_length=120, default="catalog", db_index=True)
    subcategory = models.CharField(max_length=120, blank=True, default="", db_index=True)
    series = models.CharField(max_length=180, blank=True, default="", db_index=True)
    product_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default=TYPE_AIR_CONDITIONER, db_index=True)
    short_description = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    specs = models.JSONField(default=dict, blank=True)
    main_image = models.ImageField(upload_to="catalog/products/", blank=True, null=True)
    recommended_area_m2 = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    power_btu = models.PositiveIntegerField(null=True, blank=True)
    energy_class = models.CharField(max_length=20, blank=True, default="")
    country = models.CharField(max_length=100, blank=True, default="")
    is_in_stock = models.BooleanField(default=True, db_index=True)
    warranty_months = models.PositiveSmallIntegerField(default=24, db_index=True)
    colors = models.ManyToManyField(Color, blank=True, related_name="catalog_products")
    is_active = models.BooleanField(default=True, db_index=True)
    is_indexable = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("brand__name", "model")
        indexes = [
            models.Index(fields=("brand", "model")),
            models.Index(fields=("category", "series")),
        ]

    def __str__(self):
        return self.name

    @property
    def company(self):
        return self.brand

    @property
    def photo(self):
        if self.main_image:
            return self.main_image
        images = list(self.images.all()[:1])
        if images and images[0].image:
            return images[0].image
        return None

    @property
    def primary_price(self):
        prices = list(self.prices.all())
        current_prices = [price for price in prices if price.is_current]
        if not current_prices:
            current_prices = prices

        priority = {
            (CatalogProductPrice.TYPE_RETAIL, CatalogProductPrice.CURRENCY_UAH): 0,
            (CatalogProductPrice.TYPE_SET, CatalogProductPrice.CURRENCY_UAH): 1,
            (CatalogProductPrice.TYPE_BLOCK, CatalogProductPrice.CURRENCY_UAH): 2,
            (CatalogProductPrice.TYPE_RETAIL, CatalogProductPrice.CURRENCY_USD): 3,
            (CatalogProductPrice.TYPE_SET, CatalogProductPrice.CURRENCY_USD): 4,
            (CatalogProductPrice.TYPE_BLOCK, CatalogProductPrice.CURRENCY_USD): 5,
        }
        current_prices.sort(key=lambda price: priority.get((price.price_type, price.currency), 100))
        return current_prices[0].amount if current_prices else None

    @property
    def primary_currency(self):
        prices = list(self.prices.all())
        current_prices = [price for price in prices if price.is_current]
        if not current_prices:
            current_prices = prices
        priority = {
            (CatalogProductPrice.TYPE_RETAIL, CatalogProductPrice.CURRENCY_UAH): 0,
            (CatalogProductPrice.TYPE_SET, CatalogProductPrice.CURRENCY_UAH): 1,
            (CatalogProductPrice.TYPE_BLOCK, CatalogProductPrice.CURRENCY_UAH): 2,
            (CatalogProductPrice.TYPE_RETAIL, CatalogProductPrice.CURRENCY_USD): 3,
            (CatalogProductPrice.TYPE_SET, CatalogProductPrice.CURRENCY_USD): 4,
            (CatalogProductPrice.TYPE_BLOCK, CatalogProductPrice.CURRENCY_USD): 5,
        }
        current_prices.sort(key=lambda price: priority.get((price.price_type, price.currency), 100))
        return current_prices[0].currency if current_prices else ""

    @property
    def price(self):
        return self.primary_price

    def get_conditioner_type_display(self):
        return self.specs.get("legacy_conditioner_type") or self.specs.get("source_product_type") or self.get_product_type_display()


class CatalogProductPrice(models.Model):
    TYPE_BLOCK = "block"
    TYPE_SET = "set"
    TYPE_WHOLESALE = "wholesale"
    TYPE_RETAIL = "retail"
    TYPE_DEALER = "dealer"
    TYPE_GROSS = "gross"
    TYPE_CHOICES = [
        (TYPE_BLOCK, "Block"),
        (TYPE_SET, "Set"),
        (TYPE_WHOLESALE, "Wholesale"),
        (TYPE_RETAIL, "Retail"),
        (TYPE_DEALER, "Dealer"),
        (TYPE_GROSS, "Gross"),
    ]

    CURRENCY_UAH = "UAH"
    CURRENCY_USD = "USD"
    CURRENCY_EUR = "EUR"
    CURRENCY_CHOICES = [
        (CURRENCY_UAH, "UAH"),
        (CURRENCY_USD, "USD"),
        (CURRENCY_EUR, "EUR"),
    ]

    product = models.ForeignKey(CatalogProduct, on_delete=models.CASCADE, related_name="prices")
    price_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    source_sheet = models.CharField(max_length=100, blank=True, default="")
    source_row = models.PositiveIntegerField(null=True, blank=True)
    is_current = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("product", "price_type", "currency")
        constraints = [
            models.UniqueConstraint(
                fields=("product", "price_type", "currency", "source_sheet", "source_row"),
                name="uniq_catalog_product_price_source",
            )
        ]
        indexes = [
            models.Index(fields=("price_type", "currency")),
        ]

    def __str__(self):
        return f"{self.product} {self.price_type} {self.amount} {self.currency}"


class CatalogProductComponent(models.Model):
    ROLE_INDOOR = "indoor"
    ROLE_OUTDOOR = "outdoor"
    ROLE_PANEL = "panel"
    ROLE_REMOTE = "remote"
    ROLE_OPTION = "option"
    ROLE_CHOICES = [
        (ROLE_INDOOR, "Indoor"),
        (ROLE_OUTDOOR, "Outdoor"),
        (ROLE_PANEL, "Panel"),
        (ROLE_REMOTE, "Remote"),
        (ROLE_OPTION, "Option"),
    ]

    parent_product = models.ForeignKey(CatalogProduct, on_delete=models.CASCADE, related_name="components")
    component_product = models.ForeignKey(CatalogProduct, on_delete=models.CASCADE, related_name="used_in_sets")
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    quantity = models.PositiveSmallIntegerField(default=1)
    notes = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("parent_product", "component_product", "role"),
                name="uniq_catalog_product_component_role",
            )
        ]

    def __str__(self):
        return f"{self.parent_product} -> {self.component_product} ({self.role})"


class CatalogProductImage(models.Model):
    product = models.ForeignKey(CatalogProduct, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="catalog/products/", blank=True, null=True)
    source_sheet = models.CharField(max_length=100, blank=True, default="")
    anchor_row = models.PositiveIntegerField(null=True, blank=True)
    anchor_col = models.PositiveIntegerField(null=True, blank=True)
    is_primary = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("product", "source_sheet", "anchor_row", "anchor_col"),
                name="uniq_catalog_product_image_anchor",
            )
        ]

    def __str__(self):
        return f"{self.product} image"


class CatalogProductImportSource(models.Model):
    product = models.ForeignKey(CatalogProduct, on_delete=models.CASCADE, related_name="import_sources")
    source_file = models.CharField(max_length=255)
    source_sheet = models.CharField(max_length=100)
    source_row = models.PositiveIntegerField()
    source_hash = models.CharField(max_length=64, db_index=True)
    raw_row_json = models.JSONField(default=dict, blank=True)
    imported_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("source_file", "source_sheet", "source_row"),
                name="uniq_catalog_product_import_source",
            )
        ]
        indexes = [
            models.Index(fields=("source_sheet", "source_row")),
        ]

    def __str__(self):
        return f"{self.source_sheet}:{self.source_row}"


class Review(models.Model):
    conditioner = models.ForeignKey(CatalogProduct, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField(null=True)

    def __str__(self):
        return f"Review: {self.user.get_username()} ({self.conditioner})"


class ConditionerOrder(models.Model):
    name = models.CharField(max_length=100, verbose_name="Ім'я")
    phone = models.CharField(max_length=100, verbose_name="Телефон")
    address = models.CharField(max_length=100, verbose_name="Адреса")
    conditioner = models.ForeignKey(CatalogProduct, on_delete=models.PROTECT)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=ORDER_STATUS_NEW, db_index=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conditioner_orders",
    )
    admin_comment = models.TextField(blank=True, default="")
    source_page = models.CharField(max_length=100, blank=True, default="", db_index=True)
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    unaccepted_reminded_at = models.DateTimeField(null=True, blank=True)
    service_reminder_6m_sent_at = models.DateTimeField(null=True, blank=True)
    service_reminder_12m_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name
