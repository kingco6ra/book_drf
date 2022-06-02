from django.contrib.auth.models import User
from django.test import TestCase

from store.models import Book
from store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def test_serializer_data(self):
        user = User.objects.create(username='test_user')

        book_1 = Book.objects.create(title='Test_1', author='Author 1', price=15)
        book_2 = Book.objects.create(title='Test_2', author='Author 2', price=25)

        data = BookSerializer([book_1, book_2], many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'title': 'Test_1',
                'price': '15.00',
                'author': 'Author 1',
                'likes': 0,
            },
            {
                'id': book_2.id,
                'title': 'Test_2',
                'price': '25.00',
                'author': 'Author 2',
                'likes': 0,
            }
        ]

        self.assertEqual(expected_data, data)

    def test_serializer_str(self):
        title = 'Test Book'
        price = '299.99'
        book = Book.objects.create(title=title, price=price)

        self.assertEqual(book.__str__(), f'{title} - {price}')
