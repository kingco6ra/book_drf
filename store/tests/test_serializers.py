from django.contrib.auth.models import User
from django.test import TestCase

from store.models import Book
from store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def test_serializer_data(self):
        book_1 = Book.objects.create(title='Test_1', author='Author 1', price='199.99')
        book_2 = Book.objects.create(title='Test_2', author='Author 2', price='99.99')
        user = User.objects.create(username='test_user')

        data = BookSerializer([book_1, book_2], many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'title': 'Test_1',
                'author': 'Author 1',
                'price': '199.99',
            },
            {
                'id': book_2.id,
                'title': 'Test_2',
                'author': 'Author 2',
                'price': '99.99',
            }
        ]

        print(*data)
        print('----------')
        print(*expected_data)
        self.assertEqual(data, expected_data)

    def test_serializer_str(self):
        title = 'Test Book'
        price = '299.99'
        book = Book.objects.create(title=title, price=price)

        self.assertEqual(book.__str__(), f'{title} - {price}')
