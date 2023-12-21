# forms.py
from django import forms
from .models import Author, Book, Publisher

class BookForm(forms.Form):
    title = forms.CharField(max_length=100)
    authors = forms.ModelMultipleChoiceField(queryset=Author.objects.all(), required=False)
    publisher = forms.ModelChoiceField(queryset=Publisher.objects.all(), required=False)
    book_instance = None  # Placeholder for the Book instance to update

    def __init__(self, *args, **kwargs):
        self.book_instance = kwargs.pop('instance', None)
        super(BookForm, self).__init__(*args, **kwargs)
        if self.book_instance:
            self.fields['title'].initial = self.book_instance.title
            self.fields['authors'].initial = self.book_instance.authors.all()
            self.fields['publisher'].initial = self.book_instance.publisher

    def save(self):
        title = self.cleaned_data['title']
        authors = self.cleaned_data['authors']
        publisher = self.cleaned_data['publisher']

        if self.book_instance:
            # Update existing Book instance
            self.book_instance.title = title
            self.book_instance.publisher = publisher
            self.book_instance.save()
            self.book_instance.authors.set(authors)
            return self.book_instance
        else:
            # Create new Book instance
            book = Book.objects.create(title=title, publisher=publisher)
            if authors:
                book.authors.add(*authors)
            return book
