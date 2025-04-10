from django.db import models

# Create your models here.

class Page1(models.Model):
    full_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    date = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Page 1 Data"
        verbose_name_plural = "Page 1 Data"

    def __str__(self):
        return f"Page 1 - {self.full_name or 'No Name'}"

class Page2(models.Model):
    full_name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    occupation = models.CharField(max_length=255, blank=True, null=True)
    citizenship_number = models.CharField(max_length=255, blank=True, null=True)
    district = models.CharField(max_length=255, blank=True, null=True)
    municipality_or_vdc = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.CharField(max_length=255, blank=True, null=True)
    fathers_name = models.CharField(max_length=255, blank=True, null=True)
    training_place = models.CharField(max_length=255, blank=True, null=True)
    training_date = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Page 2 Data"
        verbose_name_plural = "Page 2 Data"

    def __str__(self):
        return f"Page 2 - {self.full_name or 'No Name'}"

class Page3(models.Model):
    full_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Page 3 Data"
        verbose_name_plural = "Page 3 Data"

    def __str__(self):
        return f"Page 3 - {self.full_name or 'No Name'}"

class Page4(models.Model):
    full_name = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    fathers_name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    occupation = models.CharField(max_length=255, blank=True, null=True)
    mobile_number = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    pan_number = models.CharField(max_length=255, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    bank_account_number = models.CharField(max_length=255, blank=True, null=True)
    signed_date = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Page 4 Data"
        verbose_name_plural = "Page 4 Data"

    def __str__(self):
        return f"Page 4 - {self.full_name or 'No Name'}"
