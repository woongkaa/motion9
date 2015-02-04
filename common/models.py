import datetime
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


# prefix 'N' in class name means renewal version model(2015/01/07)
@python_2_unicode_compatible
class NCategory(models.Model):
    name = models.CharField(max_length=20, unique=True)
    kor_name = models.CharField(max_length=20, default='')

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class NProduct(models.Model):
    name = models.CharField(max_length=20, null=False)
    brand = models.CharField(max_length=20, null=False, blank=True)
    category = models.ForeignKey(NCategory)
    price = models.IntegerField(null=False, default=0)
    capacity = models.IntegerField(null=False, default=0)
    capacity_unit = models.CharField(max_length=10, null=False, default='ml')

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class ProductDetail(models.Model):
    product = models.ForeignKey(NProduct, related_name='details')
    function = models.TextField(null=False, blank=True)
    estimation_period = models.SmallIntegerField(null=False, default=0)

    def __str__(self):
        return self.product.name

@python_2_unicode_compatible
class ProductAnalysis(models.Model):
    product = models.ForeignKey(NProduct,unique=True, related_name='analysis')
    total_count = models.IntegerField(null=False, default=0)
    skin_type = models.CharField(max_length=4, null=False, blank=True) # one start character of ('dry', 'oily', 'neutral', 'complex')
    feature = models.CharField(max_length=2, null=False, default='no') # two start character of ('whitening', 'wrinkle', 'trouble', 'nothing')
    general_review = models.TextField(null=False, blank=True)

    def __str__(self):
        return self.product

@python_2_unicode_compatible
class ProductAnalysisDetail(models.Model):
    product_analysis = models.ForeignKey(ProductAnalysis, related_name='details')
    content = models.TextField(null=False, blank=True)
    count = models.IntegerField(null=False, default=0)
    type = models.CharField(max_length=20, null=False)

    def __str__(self):
        return self.product_analysis

    class Meta:
        unique_together = (("product_analysis", "content"),)
        ordering = ['-count']