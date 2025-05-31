from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

CHOICES = (
    ('accepted', 'Принята'),
    ('rejected', 'Отклонена'),
    ('pending', 'Ожидает')
)


class Category(models.Model):
    title = models.CharField(
        max_length=32)
    slug = models.SlugField(
        unique=True, blank=False)

    def ___str__(self):
        return self.title


class Condition(models.Model):
    title = models.CharField(
        max_length=32)
    slug = models.SlugField(
        unique=True, blank=False)

    def ___str__(self):
        return self.title


class Ad(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    title = models.CharField(
        max_length=64, blank=False)
    description = models.CharField(
        max_length=512, blank=False)
    image_url = models.ImageField(
        upload_to='ads/images/', null=True,
        blank=True)
    category = models.ManyToManyField(
        Category, through='AdCategory')
    condition = models.ForeignKey(
        Condition, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(
        auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title


class AdCategory(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class ExchangeProposal(models.Model):
    ad_sender = models.ForeignKey(
        Ad, on_delete=models.CASCADE, related_name='ad_sender')
    ad_receiver = models.ForeignKey(
        Ad, on_delete=models.CASCADE, related_name='ad_receiver')
    comment = models.CharField(
        max_length=512)
    status = models.CharField(
        max_length=32, choices=CHOICES, default='pending')
    created_at = models.DateTimeField(
        auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ad_sender', 'ad_receiver'],
                name='Exchange constraint')
        ]
