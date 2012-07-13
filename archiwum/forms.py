# -*- coding: utf-8 -*-
from django.forms import ModelForm
from archiwum.models import *
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.localflavor.pl.forms import PLPostalCodeField

class SubjectForm(ModelForm):
    title = forms.CharField(label = 'Nazwa przedmiotu', error_messages={'required': 'Proszę wpisać nazwę przedmiotu!'})
    class Meta:
        model = Subject
    def save(self, commit=True):
        subject=ModelForm.save(self,commit=False)
        if commit:
            subject.save()
        return subject

class DocumentForm(ModelForm):
    #dok = forms.FileField(label = 'Plik dokumentu', widget=forms.FileInput, error_messages={'required' : 'Nie podałeś pliku!'})
    #title = forms.CharField(label = 'Tytuł', widget = forms.TextInput(attrs={'size': 80,}), error_messages={'required': 'Proszę wpisać tytuł!'})
    #description = forms.CharField(label = 'Opis dokumentu', widget = forms.Textarea(attrs={'rows': 10, 'cols': 80,}), error_messages={'required': 'Proszę opisać dokument!'})
    class Meta:
        model = Document
        exclude = ('author', 'issued_on',)
    def save(self,author, commit=True):
        document=ModelForm.save(self,commit=False)
        document.author = author
        if commit:
            document.save()
        return document

class NewsForm(ModelForm):
    title = forms.CharField(label = 'Tytuł wiadomości:', widget = forms.TextInput(attrs={'size': 93,}), error_messages={'required': 'Proszę wpisać tytuł wiadomości!'})
    text = forms.CharField(label='Treść:', widget=forms.Textarea(attrs={'rows': 10, 'cols': 120,}), error_messages={'required': 'Proszę wpisać treść!'})
    class Meta:
        model = News
        exclude = ('pub_date','author',)
    def save(self,author, commit=True):
        news=ModelForm.save(self,commit=False)
        news.author = author
        if commit:
            news.save()
        return news

class UserRegistrationForm(UserCreationForm):
    """group_choices = (
    (u'Student', 'Student'),
    (u'Instruktor', 'Instruktor'),
    (u'Pracownik dziekanatu', 'Pracownik dziekanatu'),
)"""
    username = forms.CharField(label="Nazwa użytkownika", error_messages={'required': 'Proszę wpisać nazwę użytkownika!'})
    first_name = forms.CharField(label="Imię", error_messages={'required': 'Proszę wpisać imię!'})
    last_name = forms.CharField(label="Nazwisko", error_messages={'required': 'Proszę wpisać nazwisko!'})
    username = forms.RegexField(label=_("Nazwa użytkownika"), max_length=30, regex=r'^[\w.@+-]+$',
            help_text = _("Długość do 30 znaków. Tylko litery, liczby oraz @/./+/-/_."),
            error_messages = {'Błąd': _("To pole może zawierać tylko litery, liczby oraz @/./+/-/_.")})
    password1 = forms.CharField(label=_("Hasło"), widget=forms.PasswordInput, error_messages={'required': 'Proszę wpisać hasło!'})
    password2 = forms.CharField(label=_("Potwierdź hasło"), widget=forms.PasswordInput, error_messages={'required': 'Wpisz ponownie hasło!'})
    #groups = forms.ChoiceField(group_choices, label="grupa")
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name",) #"groups",
        
        
class SearchDocumentForm(forms.Form):
    search_text = forms.CharField(max_length=500, label="Szukaj wg słów kluczowych, np. fragmentu tytułu, opisu",  required = False)
    
    
    def __init__(self, categories, types, publics, *args, **kwargs):
        super(SearchDocumentForm, self).__init__(*args, **kwargs)
        # build a choice tuple (list in this case)
        types_choices = []
        for t in types:
            x = (t.slug, t.name)
            types_choices.append(x)
        self.fields['types'] = forms.ChoiceField(types_choices, label='Typ', required=False, widget=forms.Select)
        
        categories_choices = []
        for c in categories:
            x = (c.slug, c.name)
            categories_choices.append(x)
        # create a field with all categories
        self.fields['categories'] = forms.ChoiceField(categories_choices, label='Kategorie',required=False, widget=forms.Select)

class SendmailForm(forms.Form):
    subject = forms.CharField(max_length=255, label='Temat', widget = forms.TextInput(attrs={'size': 93,}), error_messages={'required': 'Proszę wpisać tytuł!'})
    message = forms.CharField(max_length=1000, label='Treść', widget=forms.Textarea(attrs={'rows': 10, 'cols': 120,}), error_messages={'required': 'Proszę wpisać treść!'})





