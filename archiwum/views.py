from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from archiwum.models import *
from archiwum.forms import NewsForm, DocumentForm, SearchDocumentForm, UserRegistrationForm, SubjectForm, SendmailForm
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.models import *
from django.conf import settings
from django.db.models import Q
import re
from django.core.mail import mail_admins, BadHeaderError


# Helper functions
def check_user_group_policy(request):
    group = check_user_group(request)
    if group =="instruktor":
        return u'instruktorów'
    elif group == "pracownik dziekanatu":
        return u'dziekanatu'
    elif group == "student":
        return u'studentów'
    else:
        return "Administrator"

def check_user_group(request):
    if request.user.is_authenticated():
        if Instructor.objects.filter(user=request.user):
            return "instruktor"
        elif Student.objects.filter(user=request.user):
            return "student"
        elif Dean.objects.filter(user=request.user):
            return "pracownik dziekanatu"
        else:
            return "Administrator"
    else:
        return "Gosc"

# functions to search queries                
def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

#returns paginated object
def set_pages(model_object, pages, request):
    paginator = Paginator(model_object,pages)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page =1
    try:
        paginated= paginator.page(page)
    except (EmptyPage, InvalidPage):
        paginated= paginator.page(1)
    return paginated

# End of Helper Functions                

# Actually views
@login_required
def main_index(request):
    user_group = check_user_group(request)
    documents = Document.objects.all().order_by('-issued_on')[:5]
    news = News.objects.all().order_by('-pub_date')[:5]
    return render_to_response('archiwum/main_index.html',  {
        'user_group': user_group, 'documents': documents,
        'news': news,
        }, context_instance=RequestContext(request))

def log_in(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password = password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # returning back
                # return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
        #changing because of other main index site
                return HttpResponseRedirect('/')
            else:
                pass
                # Return a page about disabled account
        else:
            return render_to_response('archiwum/log_in.html', {'form': form, 'do_not_show_nav': 1}, context_instance = RequestContext(request))
    # endif request method = POST
    else:
        form = AuthenticationForm(request)
        return render_to_response('archiwum/log_in.html',{'form': form,
                'do_not_show_nav': 1}, 
                    context_instance = RequestContext(request))


def log_out(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/users/login')
    else:
        logout(request)
        return HttpResponseRedirect('/')

def register_user(request):
    # Dodac first_name i last_name w formularzu...
    user_group = check_user_group(request)
    if request.user.is_authenticated() and user_group in ('pracownik dziekanatu',):
        if request.method == "POST":
            form = UserRegistrationForm(data=request.POST)
            if form.is_valid():
                form.save()
                # By default, new user is a Student, group and class
                u = User.objects.get(username=request.POST.get('username'))
                gid = Group.objects.get(name='Student')
                u.groups.add(gid.id)
                s = Student(user = u)
                s.save()
                # end of 'magic', dirty but works pretty well
                return HttpResponseRedirect('/')
            else:
                return render_to_response('archiwum/register.html', {'form': form}, context_instance = RequestContext(request))
        else:	
            form = UserRegistrationForm()
            return render_to_response('archiwum/register.html', {'form': form,
                    'do_not_show_nav': 0,}, context_instance = RequestContext(request))
    else:
        warning = "Nie masz uprawnień do dodawania studentów!"
        return render_to_response('archiwum/message.html', {'warning' : warning}, context_instance = RequestContext(request))

def add_subject(request):
    user_group = check_user_group(request)
    subjects = Subject.objects.all().order_by('title')
    warning = "Nie masz uprawnień do dodawania przedmiotów!"
    if not request.user.is_authenticated() or user_group not in ('pracownik dziekanatu',):
        return render_to_response('archiwum/message.html', {'warning' : warning}, context_instance = RequestContext(request))
    if request.method == "POST":
        form = SubjectForm(data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/archiwum/subjects/add')
    else:
        form = SubjectForm()
    return render_to_response('archiwum/add_subject.html', {'form' : form, 'user_group' : user_group, 'subjects' : subjects,}, context_instance = RequestContext(request))

@login_required
def add_document(request):
    user_group = check_user_group(request)
    warning = "Nie masz uprawnień do dodawania dokumentów!"
    if not request.user.is_authenticated() or user_group not in ('instruktor', 'pracownik dziekanatu',):
        return render_to_response('archiwum/message.html', {'warning' : warning, 'user_group' : user_group,}, context_instance = RequestContext(request))
    if request.FILES: #method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            #handle_uploaded_file(request.FILES['dok'])
            form.save(author=request.user)
            return HttpResponseRedirect('/') #render_to_response('archiwum/message.html', {'user_group' : user_group, 'warning' : warning, }, context_instance=RequestContext(request))
        else:
            render_to_response('archiwum/add_document.html', {'user_group' : user_group, 'form' : form, }, context_instance=RequestContext(request))
    else:
        form = DocumentForm()
    return render_to_response('archiwum/add_document.html', {'user_group' : user_group, 'form' : form, }, context_instance=RequestContext(request))
	
@login_required
def add_news(request):
    user_group = check_user_group(request)
    warning = "Nie masz uprawnień do dodawania wiadomości"
    if not request.user.is_authenticated() or user_group not in ('instruktor', 'pracownik dziekanatu',):
        return render_to_response('archiwum/message.html', {'warning' : warning, 'user_group' : user_group,}, context_instance = RequestContext(request))
    if request.method == "POST":
        form = NewsForm(data=request.POST)
        if form.is_valid():
            form.save(author=request.user)
            return HttpResponseRedirect('/')
    else:
        form = NewsForm()
    return render_to_response('archiwum/add_news.html', {'form': form, 'user_group': user_group,}, context_instance = RequestContext(request))


def edit_news(request, news_id):
    user_group = check_user_group(request)
    form = NewsForm(instance=News.objects.get(id=news_id))
    if request.method == "POST":
        form = NewsForm(request.POST, instance=News.objects.get(id=news_id))
        if form.is_valid():
            if request.POST.get('cancel'):
               return HttpResponseRedirect('/')
            elif request.POST.get('delete'):
                news = News.objects.get(id=news_id)
                news.delete()
                return HttpResponseRedirect('/')
            else:
                form.save(author=request.user)
            return HttpResponseRedirect('/')
        else:
            return render_to_response('archiwum/edit_news.html', {'form':form, 'user_group':user_group,}, context_instance = RequestContext(request))
    else:
        form = NewsForm(instance=News.objects.get(id=news_id))
        return render_to_response('archiwum/edit_news.html', {'form':form, 'user_group':user_group,}, context_instance = RequestContext(request))

def my_newses(request):
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        news_query = get_query(query_string,  ['title',  'text', ])
        found_entries = News.objects.filter(author=request.user).filter(news_query).order_by('-pub_date')
    else:
        found_entries = News.objects.filter(author=request.user).order_by('-pub_date')
    user_group = check_user_group(request)
        # paginate that crap
    newses_ = set_pages(found_entries,  10,  request)
    return render_to_response('archiwum/my_newses.html', {'user_group':user_group, 'newses': newses_,}, context_instance=RequestContext(request))

@login_required
def news_show(request, news_id):
    user_group = check_user_group(request)
    try:
        news = News.objects.get(pk=news_id)
    except News.DoesNotExist:
        raise Http404
    return render_to_response('archiwum/news_show.html', {'news' : news,  'user_group' : user_group, },  context_instance = RequestContext(request))

def newses(request):
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        news_query = get_query(query_string,  ['title',  'text', ])
        found_entries = News.objects.filter(news_query).order_by('-pub_date')
    else:
        found_entries = News.objects.all().order_by('-pub_date')
    user_group = check_user_group(request)
        # paginate that crap
    newses_ = set_pages(found_entries,  10,  request)
    return render_to_response('archiwum/newses.html', {'user_group':user_group, 'newses': newses_,}, context_instance=RequestContext(request))


def documents(request):
    documents = Document.objects.all()
    document_types = DocumentType.objects.all()
    document_publics = DocumentPublic.objects.all()
    document_categories = DocumentCategory.objects.all()
    documents_ = set_pages(documents, 5, request)
    user_group = check_user_group(request)
    return render_to_response('archiwum/documents.html', {'user_group' : user_group, 'documents' : documents_, 'document_categories' : document_categories,}, context_instance=RequestContext(request))

def graphs(request):
    try:
        documents = Document.objects.filter(category__name__startswith='plan zajęć')
    except Document.DoesNotExist:
        raise Http404
    documents_ = set_pages(documents, 5, request)
    user_group = check_user_group(request)
    return render_to_response('archiwum/graphs.html', {'user_group' : user_group, 'documents' : documents_,}, context_instance=RequestContext(request))

def info(request):
    user_group = check_user_group(request)
    mailadmin = settings.ADMINS
    return render_to_response('archiwum/info.html', {'user_group' : user_group, 'mailadmin' : mailadmin,}, context_instance=RequestContext(request))

def search_documents(request):
    document_categories = DocumentCategory.objects.all()
    document_types = DocumentType.objects.all()
    document_publics = DocumentPublic.objects.all()
    query_string = ''
    found_entries = None
    user_group = check_user_group(request)
    policy_group = check_user_group_policy(request)
    if not request.GET.items() or (request.GET['search_text'] == '' and 'types' not in request.GET and 'categories' not in request.GET and 'publics' not in request.GET):
        found_entries = Document.objects.all()
        form = SearchDocumentForm(document_categories, document_types, document_publics)
        print "Nic w requescie"
    
    #if not request.GET.items() or (request.GET['search_text'] == '' and 'choices' not in request.GET):
        ##documents = Document.objects.all()
        #found_entries = Document.objects.all()
        #form = SearchDocumentForm(document_categories)
        ##documents_ = set_pages(documents, 10,  request)
        ##return render_to_response('docu/documents.html',  {'documents':  documents_,'user_group': user_group,  'form': form, },  context_instance=RequestContext(request))

    else:
        if  request.GET['search_text'] !='':
            query_string = request.GET['search_text']
            q = get_query(query_string,  ['title',  'description', ])
        else:
            q = Q()
        #if 'types' in request.GET:
            #types = request.GET.getlist('types')
            #if len(types) > 0:
                #q.add(Q(type=types),    'AND')
        
        found_entries = Document.objects.filter(q)
    #pir - publics in request
    pir = request.GET.getlist('publics')
    if pir:
        found_entries = found_entries.filter(public__name__in=pir)
    #cir = categories_in_request
    cir = request.GET.getlist('categories')
    if cir:
        found_entries = found_entries.filter(category__slug__in=cir)
    #tir = type in request
    tir = request.GET.getlist('types')
    if tir:
        found_entries = found_entries.filter(type__slug__in=tir)
    #pagination
    documents_ = set_pages(found_entries, 5,  request) 
    # have a updated form
    form = SearchDocumentForm(document_categories, document_types, document_publics, data=request.GET)
    return render_to_response('archiwum/search_documents.html',  
                {'user_group': user_group,  'form': form, 
                 'documents' : documents_, 'document_categories': document_categories,
                 'policy_group': policy_group,},  
                context_instance=RequestContext(request))

def documents_by_category(request, slug):
    document_categories = DocumentCategory.objects.all()
    user_group = check_user_group(request)
    try:
        cat = DocumentCategory.objects.get(slug=slug)
    except DocumentCategory.DoesNotExist:
        raise Http404    
    documents_ = cat.document_set.all().order_by('-id')
    documents = set_pages(documents_, 5,  request) 
    return render_to_response('archiwum/documents_by_category.html',
                              {'documents':documents, 'user_group':user_group,
                               'cat':cat,'document_categories':document_categories,},
                              context_instance=RequestContext(request))

@login_required							  
def document_show(request, document_id):
    user_group = check_user_group(request)
    policy_group = check_user_group_policy(request)
    try:

        document = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        raise Http404
    except DocumentVersion.DoesNotExist:
        document_version = False
    restricted_access = 0
    if user_group == "Administrator":
        restricted_access = 1
    print policy_group
    return render_to_response('archiwum/document_show.html', {'document' : document,  'user_group' : user_group, 'restricted_access': restricted_access, 
                              'policy_group': policy_group,}, context_instance = RequestContext(request))

def lesson_show(request, lesson_id):
    user_group = check_user_group(request)
    try:
        lesson = Lesson.objects.get(pk=lesson_id)
    except Lesson.DoesNotExist:
        raise Http404
    return render_to_response('archiwum/lesson_show.html',  {'user_group': user_group,  'lesson': lesson, }, context_instance=RequestContext(request))

def lessons(request):
    #use the sorting app
    search_text = request.GET.get('search_text')
    sort_by = request.get('sort_by')
    lessons = Lesson.objects.all()

def list_users(request):
    user_group = check_user_group(request)
    semestr = Semester.objects.all().order_by('number')
    grupa = Studentgroup.objects.all().order_by('name')
    students = Student.objects.all().order_by('indeks')
    students_ = set_pages(students,  20,  request)
    return render_to_response('archiwum/list_students.html', {'user_group': user_group, 'semestr': semestr, 'grupa': grupa, 'students': students_,}, context_instance =RequestContext(request))

def list_instructors(request):
    user_group = check_user_group(request)
    instructors = Instructor.objects.all().order_by('surname')
    return render_to_response('archiwum/list_instructors.html', {'user_group':user_group, 'instructors': instructors,}, context_instance =RequestContext(request))

def list_groups(request):
    user_group = check_user_group(request)
    groups = Studentgroup.objects.all().order_by('name')
    return render_to_response('archiwum/list_groups.html', {'user_group' : user_group, 'groups' : groups, }, context_instance = RequestContext(request))

def instructor_show(request, instructor_id):
    user_group = check_user_group(request)
    try:
        instructor = Instructor.objects.get(pk=instructor_id)
    except Lesson.DoesNotExist:
        raise Http404
    return render_to_response('archiwum/instructor_show.html', {'user_group' : user_group, 'instructor' : instructor, }, context_instance=RequestContext(request))

def send_email(request):
    user_group = check_user_group(request)
    subject = request.POST.get('subject', '')
    message = request.POST.get('message', '')
    if request.method == "POST":
        form = SendmailForm(request.POST)
        if request.POST.get('cancel'):
            return HttpResponseRedirect('/info')
        elif request.POST.get('send'):
            if form.is_valid(): #if subject and message and from_email:
                warning = 'Dziękuję. Wiadomość została wysłana do administratora!'
                try:
                    mail_admins(subject, message, fail_silently=False, connection=None)
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
                return render_to_response('archiwum/message.html', {'user_group' : user_group, 'warning' : warning, }, context_instance=RequestContext(request))
            else:
                return render_to_response('archiwum/send_mail.html', {'user_group' : user_group, 'form' : form}, context_instance=RequestContext(request))
    else:
        form = SendmailForm()
        return render_to_response('archiwum/send_mail.html', {'user_group' : user_group, 'form' : form}, context_instance=RequestContext(request))


def students_by_semester(request, slug):
    user_group = check_user_group(request)
    try:
        semestr = Semester.objects.get(slug=slug)
    except DocumentCategory.DoesNotExist:
        raise Http404 
    students = Student.objects.filter(semestr=semestr).order_by('indeks')
    students_ = set_pages(students, 20, request)
    return render_to_response('archiwum/students_by_semester.html', {'user_group' : user_group, 'students' : students_, 'semestr' : semestr,}, context_instance=RequestContext(request))

def students_by_group(request, slug):
    user_group = check_user_group(request)
    try:
        grupa = Studentgroup.objects.get(slug=slug)
    except Studentgroup.DoesNotExist:
        raise Http404 
    students = Student.objects.filter(group=grupa).order_by('indeks')
    counter = Student.objects.filter(group=grupa).count()
    students_ = set_pages(students, 20, request)
    return render_to_response('archiwum/students_by_group.html', {'user_group' : user_group, 'students' : students_, 'counter' : counter, 'grupa' : grupa,}, context_instance=RequestContext(request))

def student_show(request, student_id):
    user_group = check_user_group(request)
    student = Student.objects.get(pk=student_id)
    return render_to_response('archiwum/student_show.html', {'user_group' : user_group, 'student' : student, }, context_instance=RequestContext(request))
