from django.db import models
from django.urls import reverse #Используется для создания URL-адресов путем изменения шаблонов URL
import uuid #Требуется для уникальных экземпляров книги
from django.contrib.auth.models import User
from datetime import date

# Create your models here.
class Genre(models.Model):
    """ Модель, представляющая жанр книги (например науч. фантастика, документалистика)"""

    name = models.CharField(max_length=200, help_text="Введите жанр книги (например науч. фантастика, документалистика)")

    def __str__(self):
        """ Строка для представления объекта модели"""
        return self.name


class Language(models.Model):
    """Модель, представляющая язык (например, английский, французский, японский и т. Д.)"""

    name = models.CharField(max_length=100, help_text="Введите язык книги (например, английский, французский, японский и т.д.)")

    def __str__(self):
        return self.name


class Book(models.Model):
    """ Модель, представляющая книгу (но не конкретную копию книги)"""

    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
        #ForeignKey используется потому, что книга может иметь только одного автора, но авторы могут иметь несколько книг
        #Author в виде строки, а не класса, поскольку он еще не была объявлена в файле
    summary = models.TextField(max_length=1000, help_text="Введите краткое описание книги")
    isbn = models.CharField('ISBN', max_length=13, help_text='13 символов <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text="Выберите жанр для этой книги")
        #ManyToManyField используется потому, что жанр может содержать много книг. Книги могут охватывать многие жанры
        #Класс Genre уже определен, поэтому мы можем указать объект выше
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Возвращает URL для доступа к конкретному экземпляру книги"""
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        """Создает строку для жанра. Это необходимо для отображения жанра в Admin"""
        return ', '.join([ genre.name for genre in self.genre.all()[:3] ])
    display_genre.short_description = 'Genre'

    class Meta:
        ordering = ['title']

class BookInstance(models.Model):
    """Модель, представляющая конкретную копию книги (то есть, которая может быть заимствована из библиотеки)"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Уникальный ID для конкретной книги во всей библиотеке")
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m', help_text='Доступность книги')
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["due_back"]
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        return '{0} ({1})'.format(self.id, self.book.title)

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

class Author(models.Model):
    """Модель, представляющая автора"""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    def get_absolute_url(self):
        """Возвращает URL для доступа к конкретному экземпляру автора"""

        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return '{0} {1}'.format(self.last_name, self.first_name)

    class Meta:
        ordering = ['last_name']
