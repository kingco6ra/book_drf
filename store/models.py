from django.contrib.auth.models import User
from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='user_owner')
    evaluations = models.ManyToManyField(User, through='UserBookRelation', related_name='evaluations')

    def __str__(self):
        return f'{self.id}. {self.author} / {self.title} - ${self.price}'


class UserBookRelation(models.Model):
    RATE_CHOICES = (
        (1, 'Very bad'),
        (2, 'Bad'),
        (3, 'Not bad'),
        (4, 'Good'),
        (5, 'Very good'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rating = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)

    def __str__(self):
        return f'{self.user}: {self.book.title}, LIKE: {self.like}, RATE: {self.rating}'
