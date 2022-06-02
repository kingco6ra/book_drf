from django.contrib.auth.models import User
from rest_framework import serializers

from store.models import Book, UserBookRelation


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(read_only=True, format='%H:%M:%S %Y-%m-%d')
    user_owner = serializers.HyperlinkedRelatedField(many=True, view_name='book-detail', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'date_joined', 'user_owner')


class BookSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'title', 'price', 'author', 'likes', 'rating')

    def get_likes(self, instance):
        return UserBookRelation.objects.filter(book=instance, like=True).count()


class UserBookRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ('book', 'like', 'in_bookmarks', 'rating')
