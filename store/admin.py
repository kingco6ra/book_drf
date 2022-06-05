from django.contrib import admin

from store.models import Book, UserBookRelation


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'title', 'price')
    list_display_links = ('id', 'author', 'title', 'price')
    list_filter = ('author',)
    search_fields = ('author', 'title')


@admin.register(UserBookRelation)
class UserBookRelationAdmin(admin.ModelAdmin):
    pass
