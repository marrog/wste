# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import re
import datetime

DOC_UPLOAD_TO = getattr(settings, 'DOCUMENTS_UPLOAD_TO', 'documents/')
# zeby byly polskie znaki wyswietlane na stronach do bazy danych nalezy przekazac nazwe u'nazwa' (tak jak w choice'ach ponizej)

SEMESTER_CHOICES = (
    (u'I', 'I'),
    (u'II', 'II'),
    (u'III', 'III'),
    (u'IV', 'IV'),
    (u'V', 'V'),
    (u'VI', 'VI'),
    (u'VII', 'VII'),
    (u'absolwent', 'absolwent'),
)

STUDY_CHOICES = (
    (u'INF', 'informatyka'),
    (u'SM', 'stosunki międzynarodowe'),
)

SPECIALIZATION_CHOICES = (
    (u'INFBIA', 'informatyka w biznesie i administracji'),
    (u'INFT', 'informatyka w telekomunikacji'),
    (u'INFU', 'informatyka w ubezpieczeniach'),
    (u'INFOS', 'informatyka w ochronie środowiska'),
    (u'INFT', 'informatyka w transporcie'),
    (u'ADME', 'administracja europejska'),
    (u'HZ', 'handel zagraniczny'),
)

CATEGORY_CHOICES = (
    (u'praca dyplomowa', 'praca dyplomowa'),
    (u'referat', 'referat'),
    (u'plan zajęć', 'plan zajęć'),
    (u'wniosek', 'wniosek'),
    (u'inny dokument', 'inny dokument'),
)

TYPE_CHOICES = (
    (u'dokument tekstowy', 'dokument tekstowy'),
    (u'dokument PDF', 'dokument PDF'),
    (u'dokument graficzny', 'dokument graficzny'),
    (u'inny dokument', 'inny dokument'),
)

PUBLIC_CHOICES = (
    (u'wszystkich', 'wszystkich'),
    (u'studentów', 'studentów'),
    (u'dziekanatu', 'dziekanatu'),
    (u'instruktorów', 'instruktorów'),
)
class Studentgroup(models.Model):
    """model opisujacy grupe studenta"""
    name = models.CharField(max_length=100, unique=True, verbose_name="nazwa grupy")
    slug = models.SlugField(unique=True, verbose_name="nazwa w adresie (bez spacji i polskich znaków!)")
    notes = models.TextField(max_length=300, blank=True, verbose_name="informacje o grupie")
    pub_date = models.DateTimeField(default=datetime.datetime.now, verbose_name="założona")
    class Meta:
        ordering=['name']
        verbose_name="grupa studencka"
        verbose_name_plural="grupy studenckie"
    def __unicode__(self):
        return self.name

class Semester(models.Model):
    number = models.CharField(max_length=30, choices=SEMESTER_CHOICES, unique=True, verbose_name="semestr")
    slug = models.SlugField(max_length=30, unique=True, verbose_name="nazwa w adresie (bez spacji i polskich znaków!)")
    subjects = models.ManyToManyField("Subject", null=True, blank=True, verbose_name="przedmioty w semestrze")
    class Meta:
        #managed=False # komendy syncdb i reset na bazie nie powoduja zmian w tym modelu
        verbose_name="semestr"
        verbose_name_plural="semestry"
    def __unicode__(self):
        return self.number

class Subject(models.Model):
    title = models.CharField(max_length=100, verbose_name="nazwa przedmiotu")
    #instructors = models.ManyToManyField(Instructor, null=True, blank=True, verbose_name="instruktorzy")
    class Meta:
        #managed=False # komendy syncdb i reset na bazie nie powoduja zmian w tym modelu
        ordering=['title']
        verbose_name="przedmiot"
        verbose_name_plural="przedmioty"
    def __unicode__(self):
        return self.title
class Dean(models.Model):
    user = models.OneToOneField(User)
    class Meta:
        verbose_name="pracownik dziekanatu"
        verbose_name_plural="pracownicy dziekanatu"
    def __unicode__(self):
        return self.user.username

class Instructor(models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=30, verbose_name="imię instruktora")
    second_name = models.CharField(max_length=30, null=True, blank=True, verbose_name="opcjonalne drugie imię")
    surname = models.CharField(max_length=30, verbose_name="nazwisko instruktora")
    prefix = models.CharField(max_length=30, null=True, blank=True)
    subjects = models.ManyToManyField(Subject, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, verbose_name="adres e-mail")
    phone = models.IntegerField(null=True, blank=True, verbose_name="numer telefonu")
    pesel = models.IntegerField(null=True, blank=True, verbose_name="numer PESEL")
    account = models.IntegerField(null=True, blank=True, verbose_name="numer konta bankowego")
    birth_date = models.DateTimeField(null=True, blank=True, verbose_name="data urodzenia")
    adress = models.CharField(max_length=100, null=True, blank=True, verbose_name="adres")
    issued_on = models.DateTimeField(auto_now_add=True, verbose_name="data dodania")
    photo =  models.ImageField(upload_to="photo/instructors/", verbose_name="fotografia instruktora", null=True, blank=True)
    remove_the_photo = models.BooleanField(verbose_name="usuń fotografię")
    description = models.TextField(null=True, blank=True, verbose_name="uwagi")
    curriculum_vitae = models.FileField(upload_to="documents/instructors/cv", null=True, blank=True, verbose_name="życiorys")
    remove_the_cv = models.BooleanField(verbose_name="usuń życiorys")
    publication1 = models.FileField(upload_to="documents/instructors/publications", null=True, blank=True, verbose_name="publikacja nr 1")
    remove_pub1 = models.BooleanField(verbose_name="usuń publikację nr 1")
    publication2 = models.FileField(upload_to="documents/instructors/publications", null=True, blank=True, verbose_name="publikacja nr 2")
    remove_pub2 = models.BooleanField(verbose_name="usuń publikację nr 2")
    publication3 = models.FileField(upload_to="documents/instructors/publications", null=True, blank=True, verbose_name="publikacja nr 3")
    remove_pub3 = models.BooleanField(verbose_name="usuń publikację nr 3")
    class Meta:
        verbose_name="instruktor"
        verbose_name_plural="instruktorzy"
    def __unicode__(self):
        return self.prefix + ' ' + self.first_name + ' ' + self.second_name + ' ' + self.surname
    def save(self, *args, **kwargs):
        if self.remove_the_photo:
            self.photo = ""
            self.remove_the_photo = False
        try:
            this = Instructor.objects.get(id=self.id)
            if this.photo != self.photo:
                this.photo.delete()
        except: pass
        if self.remove_the_cv:
            self.curriculum_vitae = ""
            self.remove_the_cv = False
        try:
            this = Instructor.objects.get(id=self.id)
            if this.curriculum_vitae != self.curriculum_vitae:
                this.curriculum_vitae.delete()
        except: pass
        if self.remove_pub1:
            self.publication1 = ""
            self.remove_pub1 = False
        try:
            this = Instructor.objects.get(id=self.id)
            if this.publication1 != self.publication1:
                this.publication1.delete()
        except: pass
        if self.remove_pub2:
            self.publication2 = ""
            self.remove_pub2 = False
        try:
            this = Instructor.objects.get(id=self.id)
            if this.publication2 != self.publication2:
                this.publication2.delete()
        except: pass
        if self.remove_pub3:
            self.publication3 = ""
            self.remove_pub3 = False
        try:
            this = Instructor.objects.get(id=self.id)
            if this.publication3 != self.publication3:
                this.publication3.delete()
        except: pass
        super(Instructor, self).save(*args, **kwargs)

class Student(models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=30, verbose_name="imię studenta")
    second_name = models.CharField(max_length=30, null=True, blank=True, verbose_name="opcjonalne drugie imię")
    surname = models.CharField(max_length=30, verbose_name="nazwisko studenta")
    indeks = models.IntegerField(unique=True, verbose_name="numer indeksu")
    study = models.CharField(max_length=30, choices=STUDY_CHOICES, verbose_name="kierunek studiów")
    specialization = models.CharField(max_length=30, null=True, blank=True, choices=SPECIALIZATION_CHOICES, verbose_name="wybrana specjalizacja")
    semestr = models.ForeignKey(Semester, null=True, blank=True, verbose_name="semestr studiów")
    group = models.ManyToManyField(Studentgroup, null=True, blank=True, verbose_name="grupa studencka")
    birth_date = models.DateTimeField(null=True, blank=True, verbose_name="data urodzenia")
    adress = models.CharField(max_length=100, null=True, blank=True, verbose_name="adres zamieszkania")
    phone = models.IntegerField(null=True, blank=True, verbose_name="telefon kontaktowy")
    email = models.EmailField(null=True, blank=True, verbose_name="adres e-mail")
    pesel = models.IntegerField(null=True, blank=True, verbose_name="numer PESEL")
    account = models.IntegerField(null=True, blank=True, verbose_name="numer konta bankowego")
    issued_on = models.DateTimeField(auto_now_add=True, verbose_name="data dodania")
    photo =  models.ImageField(upload_to="photo/students/", verbose_name="fotografia studenta", null=True, blank=True)
    remove_the_photo = models.BooleanField(verbose_name="usuń fotografię")
    description = models.TextField(null=True, blank=True, verbose_name="uwagi")
    #subjects = models.ForeignKey(Subject, blank=True)
    class Meta:
        verbose_name="student"
        verbose_name_plural="studenci"
    def __unicode__(self):
        return str(self.indeks) + ' ' + self.first_name + ' ' + self.second_name + ' ' + self.surname
    def save(self, *args, **kwargs):
        if self.remove_the_photo:
            self.photo = ""
            self.remove_the_photo = False
        try:
            this = Student.objects.get(id=self.id)
            if this.photo != self.photo:
                this.photo.delete()
        except: pass
        super(Student, self).save(*args, **kwargs)


class News(models.Model):
    public = models.CharField(max_length=50, choices=PUBLIC_CHOICES)
    title = models.CharField(max_length=250)
    text = models.TextField()
    pub_date = models.DateTimeField(default=datetime.datetime.now)
    author = models.ForeignKey(User, null=True, blank=True)
    class Meta:
        verbose_name="wiadomość"
        verbose_name_plural="wiadomości"
    def __unicode__(self):
        return self.title

class Grade(models.Model):
    # How good is the grade
    rating = models.IntegerField()
    # title is: "For what i got that grade?"
    title = models.CharField(max_length=250)
    # additional comment from Instructor (dodatkowy komentarz od wykladowcy"
    text = models.TextField()
    pub_date = models.DateTimeField(default=datetime.datetime.now)
    subject = models.ForeignKey(Subject)
    # From who?
    instructor = models.ForeignKey(Instructor)
    # Whose grade is that?
    student = models.ForeignKey(Student)
    class Meta:
        verbose_name="ocena"
        verbose_name_plural="oceny"
    def __unicode__(self):
        return self.student.__unicode__() + ': ' + self.subject.title + ' ' + str(self.rating)

class Lesson(models.Model):
    # Subject of the lesson (tematy wykladu)
    name = models.CharField(max_length=250)
    subject = models.ForeignKey(Subject)
    # This specific user have to be from Instructors group!
    instructor = models.ForeignKey(Instructor)
    # Better text for that one?
    date = models.DateTimeField('data ')
    students = models.ManyToManyField(Student,  blank=True)
    grades = models.ManyToManyField(Grade,  blank=True)
    class Meta:
        verbose_name="wykład"
        verbose_name_plural="wykłady"
    def __unicode__(self):
        return self.name
    
class DocumentCategory(models.Model):
    name = models.CharField(max_length=30, choices=CATEGORY_CHOICES, verbose_name='kategoria')
    slug = models.SlugField(max_length=30, unique=True, verbose_name='nazwa w adresie (bez spacji i polskich znaków!)')
    class Meta:
        #managed=False # komendy syncdb i reset na bazie nie powoduja zmian w tym modelu
        verbose_name="kategoria dokumentu"
        verbose_name_plural="kategorie dokumentu"
    class Admin:
        list_display=(u'name')
    def __unicode__(self):
        return self.name
    
class DocumentType(models.Model):
    name = models.CharField(max_length=30, choices=TYPE_CHOICES, verbose_name='Typ dokumentu')
    slug = models.SlugField(max_length=30, unique=True, verbose_name='nazwa w adresie (bez spacji i polskich znaków!)')
    class Meta:
        #managed=False # komendy syncdb i reset na bazie nie powoduja zmian w tym modelu
        verbose_name='typ dokumentu'
        verbose_name_plural='typy dokumentu'
    class Admin:
        list_display=('name')
    def __unicode__(self):
        return self.name

class DocumentPublic(models.Model):
    name = models.CharField(max_length=50, choices=PUBLIC_CHOICES)
    class Meta:
        #managed=False # komendy syncdb i reset na bazie nie powoduja zmian w tym modelu
        verbose_name="publikacja dokumentu dla..."
        verbose_name_plural="publikacje dokumentu dla..."
    def __unicode__(self):
        return self.name    
    
class Document(models.Model):
    dok = models.FileField(upload_to="documents/", verbose_name="Plik dokumentu")
    public = models.ForeignKey(DocumentPublic, verbose_name="publikuj dla...")
    category = models.ForeignKey(DocumentCategory, verbose_name="kategoria")
    typ = models.ForeignKey(DocumentType, verbose_name="typ dokumentu")
    title = models.CharField(max_length=255, unique=True, verbose_name="tytuł")
    author = models.ForeignKey(User)
    issued_on = models.DateTimeField(default=datetime.datetime.now)
    description = models.TextField()
    class Meta:
        verbose_name="dokument"
        verbose_name_plural="dokumenty"
    def __unicode__(self):
        return self.title


