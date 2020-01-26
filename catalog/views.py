from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre, Language
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from .forms import RenewBookForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

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
    """Общий вид на основе класса для списка книг"""
    model = Book
    paginate_by = 5

class BookDetailView(generic.DetailView):
    """Общий подробный вид на основе класса для книги"""
    model = Book

class AuthorListView(generic.ListView):
    """Общий вид списка на основе классов для списка авторов"""
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    """Общий детальный вид на основе классов для автора"""
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Общий вид на основе класса, в котором перечислены книги, переданные в аренду текущему пользователю."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Общий вид на основе класса со списком всех книг, взятых в долг. Видно только пользователям с разрешением 'can_mark_returned'"""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """Функция просмотра для обновления определенного BookInstance от библиотекаря"""
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # Если это POST-запрос, обработайте данные формы
    if request.method == 'POST':

        # Создайте экземпляр формы и заполните его данными из запроса (привязка)
        form = RenewBookForm(request.POST)

        # Проверьте правильность формы
        if form.is_valid():
            # обрабатывать данные в form.cleaned_data по мере необходимости (здесь мы просто записываем их в поле "due_back")
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # перенаправить на новый URL
            return HttpResponseRedirect(reverse('all-borrowed') )

    # Если это GET-запрос (или любой другой метод), создайте форму по умолчанию
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death': '12/10/2016',}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(CreateView):
    model = Book
    fields = '__all__'

class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
