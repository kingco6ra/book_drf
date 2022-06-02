import json

from django.contrib.auth.models import User
from django.db.models import Avg
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BooksAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username2')
        self.user_admin = User.objects.create(username='admin', is_staff=True)

        self.book_1 = Book.objects.create(title='Test Book 1', author='Author 1', price=299, owner=self.user)
        self.book_2 = Book.objects.create(title='Test Book 2', author='Author 2', price='199.99', owner=self.user)
        self.book_3 = Book.objects.create(title='Test Book 3, Author', author='Author 3', price='100.00',
                                          owner=self.user)
        self.book_list = Book.objects.all().annotate(
            rating=Avg('userbookrelation__rating')
        ).order_by('id')

        self.url_detail = reverse('book-detail', args=(self.book_1.pk,))
        self.url_list = reverse('book-list')

        self.json_data = json.dumps({
            'title': self.book_1.title,
            'author': self.book_1.author,
            'price': 500
        })

    def test_get(self):
        response = self.client.get(self.url_list)
        serializer_data = BookSerializer(self.book_list, many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_detail(self):
        response = self.client.get(self.url_detail)
        expected_data = {
            'id': self.book_1.id,
            'title': 'Test Book 1',
            'price': '299.00',
            'author': 'Author 1',
            'likes': 0,
            'rating': None
        }

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_data, response.data)

    def test_get_filter(self):
        book = Book.objects.filter(price=100).annotate(
            rating=Avg('userbookrelation__rating')
        )
        response = self.client.get(self.url_list, data={'price': 100})
        serializer_data = BookSerializer(book, many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        book = Book.objects.filter(title='Test Book 1').annotate(
            rating=Avg('userbookrelation__rating')
        )
        response = self.client.get(self.url_list, data={'search': 'Test Book 1'})
        serializer_data = BookSerializer(book, many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        response = self.client.get(self.url_list, data={'ordering': '-author'})
        serializer_data = BookSerializer(Book.objects.all().annotate(
            rating=Avg('userbookrelation__rating')
        ).order_by('-author'), many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_post(self):
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'price': '199.99'
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(self.url_list, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.all().last().owner)

    def test_put(self):
        self.client.force_login(self.user)
        response = self.client.put(self.url_detail, data=self.json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(500, self.book_1.price)

    def test_put_not_owner(self):
        self.client.force_login(self.user2)
        response = self.client.put(self.url_detail, data=self.json_data, content_type='application/json')

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail(
            string='You do not have permission to perform this action.',
            code='permission_denied')}, response.data
        )
        self.book_1.refresh_from_db()
        self.assertEqual(299, self.book_1.price)

    def test_put_not_owner_but_staff(self):
        self.client.force_login(self.user_admin)
        response = self.client.put(self.url_detail, data=self.json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(500, self.book_1.price)

    def test_delete(self):
        self.client.force_login(self.user)
        response = self.client.delete(self.url_detail)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        response = self.client.get(self.url_detail)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_not_owner(self):
        self.client.force_login(self.user2)
        response = self.client.delete(self.url_detail)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

        response = self.client.get(self.url_detail)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_delete_not_owner_but_staff(self):
        self.client.force_login(self.user_admin)
        response = self.client.delete(self.url_detail)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        response = self.client.get(self.url_detail)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)


class BooksRelationAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username2')
        self.user_admin = User.objects.create(username='admin', is_staff=True)

        self.book_1 = Book.objects.create(title='Test Book 1', author='Author 1', price=299, owner=self.user)

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'like': True,
         }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.like)

    def test_bookmarks(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'in_bookmarks': True,
         }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.in_bookmarks)

    def test_rating(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'rating': 5,
         }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertEqual(5, relation.rating)

    def test_rating_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'rating': 777,
         }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
