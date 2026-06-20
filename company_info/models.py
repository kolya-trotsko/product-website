from django.db import models
from django.core.exceptions import ValidationError


class CompanyInfo(models.Model):
    address = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    instagram_link = models.URLField(blank=True, null=True)
    telegram_link = models.URLField(blank=True, null=True)
    viber_link = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if CompanyInfo.objects.exists() and not self.pk:
            raise ValidationError("Може існувати лише один запис CompanyInfo")
        super(CompanyInfo, self).save(*args, **kwargs)

    def __str__(self):
        return "Інформація про компанію"
