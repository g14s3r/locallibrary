from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre, Language
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
def index(request):
    """Функция отображения для домашней страницы сайта"""
    # Генерация "количеств" некоторых главных объектов
    num_books=Book.objects.all().count()
    #num_booksde=Book.objects.filter(title__icontains='de').count()
    num_instances=BookInstance.objects.all().count()
    # Доступные книги (статус = 'a')
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count() # Метод 'all()' применен по умолчанию
    num_genres=Genre.objects.all().count()
    num_languages=Language.objects.all().count()
    #num_genrenovel=Genre.objects.filter(name__icontains='novel').count()

    # Количество посещений этого представления, подсчитанное в переменной сеанса
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1

    # Отрисовка HTML-шаблона index.html с данными внутри переменной контекста context
    return render(
        request,
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances, 'num_instances_available': num_instances_available, 'num_authors': num_authors, 'num_genres': num_genres, 'num_languages': num_languages, 'num_visits': num_visits} #'num_genrenovel': num_genrenovel, 'num_booksde': num_booksde}
    )

class BookListView(generic.ListView):
    model = Book
    paginate_by = 5

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Общий вид на основе класса, в котором перечислены книги, переданные в аренду текущему пользователю."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
