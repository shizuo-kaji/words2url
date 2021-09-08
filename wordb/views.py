#https://qiita.com/okoppe8/items/54eb105c9c94c0960f14
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import DetailView,ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Q,F
from django_filters.views import FilterView
from django.contrib import messages
import datetime
from urllib.parse import urlencode
import string,secrets

from .filters import ItemFilter
from .models import Item
from .form import ItemForm, ItemEditForm

class ItemUpdateView(UpdateView): # LoginRequiredMixin #NOT_USED_YET
    model = Item
    form_class = ItemEditForm
    template_name = "wordb/item_edit.html"

    def get(self, request, **kwargs):
        if request.GET:
            if request.session.editkey != self.object.editkey:
                return reverse("list")
        return super().get(request, **kwargs)

    def get_success_url(self):
        # app_name:url_name, as defined in the corresponding path() `name` argument in urls.py
        return reverse("index", kwargs={"pk": self.object.pk})


class ItemFilterView(FilterView):
    model = Item
    filterset_class = ItemFilter
    queryset = Item.objects.all().order_by('-end_date')

    strict = True  ## empty query return all objects
    paginate_by = 10
    
    def get(self, request, **kwargs):
        if request.GET: # save session
            request.session['query'] = request.GET
        else: # load session
            request.GET = request.GET.copy()
            if 'query' in request.session.keys():
                for key in request.session['query'].keys():
                    request.GET[key] = request.session['query'][key]

        return super().get(request, **kwargs)


def pass_gen(size=12):
   chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
   chars += '%&$#()'
   return ''.join(secrets.choice(chars) for x in range(size))

def ask(request):
    words = request.GET.get('words')
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            #print(post.begin_date)
            object_list = Item.objects.filter(Q(words_text__iexact=post.words_text) & Q(end_date__gte=post.begin_date))
            if len(object_list)>0: # the key is already taken
                messages.error(request, 'The Words are already taken.')
                return render(request, 'wordb/form.html', {'form': form, 'taken_till':object_list[0].end_date})
            else:
                if post.length==1:
                    post.end_date = post.begin_date + datetime.timedelta(days=1)
                elif post.length==2:
                    post.end_date = post.begin_date + datetime.timedelta(weeks=1)
                elif post.length==3:
                    post.end_date = post.begin_date + datetime.timedelta(days=31)
                else:
                    messages.error(request, 'Something is wrong with the dates')
                    return redirect('/')
                post.save()
                messages.success(request, 'Thanks for your purchase')
                return redirect('/')
    else:
        init_params = {'words_text': words,
                                 'editkey': pass_gen(20),
                                 'begin_date': timezone.now(),
                                 }
        form = ItemForm(initial=init_params)
    return render(request, 'wordb/form.html', {'form': form, 'words':words})


def edit(request, pk):
    #if request.user.is_authenticated and request.user == article.author:
    item = Item.objects.get(id=pk)
    editkey = ''
    if 'query' in request.session.keys():
        if 'editkey' in request.session['query'].keys():
            editkey = request.session['query']['editkey']
        
    print(pk,item,request.method)
    if editkey != item.editkey:
        messages.error(request, 'wrong editkey')
        return redirect('itemlist')
    elif request.method == 'POST': # update
        form = ItemEditForm(request.POST, instance=item)
        if form.is_valid():
            post = form.save(commit=False)
            print(post.length)
            # extend rental duration
            if post.length==1:
                post.end_date = post.end_date + datetime.timedelta(days=1)
            elif post.length==2:
                post.end_date = post.end_date + datetime.timedelta(weeks=1)
            elif post.length==3:
                post.end_date = post.end_date + datetime.timedelta(days=31)
            post.save()
            messages.success(request, 'Your Words are successfully updated!')
            return redirect('/')
            #return render(request, 'wordb/item_list.html', {'object_list':[form],'bought_words':post.words_text})
    else:
        form = ItemEditForm(instance=item , initial={'length': 0})
        print(form.instance.begin_date)
        return render(request, 'wordb/item_edit.html', {'form': form, 'item':item})

    return redirect('itemlist')


def index(request):
    q_word = request.GET.get('query')
    if hasattr(request, 'session'):
        request.session.pop('query','') # clear search key
    #print(q_word)
    if not q_word:
        return render(request, 'wordb/item_list.html', {'object_list':[]})
    q_word = q_word.split()
    flags = dict()
    words = []
    for w in q_word:
        if w[0] == "@": # modifier
            flags[w[1:]] = True
        else:
            words.append(w)

    words = " ".join(words)

    #print("key: ",q_word)
    object_list = Item.objects.filter(Q(words_text__iexact=words) & Q(end_date__gte=timezone.now()))
    if len(object_list)==0 and not 'list' in flags.keys():
        # redirect_url = reverse('ask')
        # parameters = urlencode({'words': words})
        # url = f'{redirect_url}?{parameters}'
        # return(redirect(url))
        messages.error(request, '{} not found'.format(words))
        return render(request, 'wordb/item_list.html', {'object_list':object_list, 'not_found_words': words})
    elif 'list' in flags.keys():
        object_list = Item.objects.filter(Q(words_text__icontains=words))
        #object_list = Item.objects.all()
        return render(request, 'wordb/item_list.html', {'object_list':object_list})
    elif len(object_list)==1: # hit and show
        item = object_list[0]
        item.count = F('count') + 1
        item.save()
        if item.data_text.startswith("http"):
            return redirect(item.data_text)
        else:
            return HttpResponse(item.data_text)
            
    return render(request, 'wordb/item_list.html', {'object_list':object_list})



##
def dummy_add_key():
    keywords = request.GET.get('words')
    if keywords:
        object_list = Item.objects.filter(Q(words_text__iexact=keywords))
        print(object_list)
        if len(object_list)==1: # hit
            item = object_list[0]
            item.words_text = keywords
            item.owner = request.GET.get('owner')
            item.data_text = request.GET.get('data_text')
            item.begin_date = timezone.now()
            item.end_date = timezone.now() + datetime.timedelta(days=1)
            item.save()
        else:
            item = Item.objects.create(
                words_text = keywords,
                owner = request.GET.get('owner'),
                data_text = request.GET.get('data_text'),
                begin_date = timezone.now(),
                end_date = timezone.now() + datetime.timedelta(days=1),
            )
            item.save()
        return render(request, 'wordb/item_list.html', {'object_list':[item]})
        #return redirect("ask/")
        #return HttpResponse("Word {} updated.".format(words))
