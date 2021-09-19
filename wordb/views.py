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
from django.views.decorators.csrf import csrf_exempt

import datetime
from urllib.parse import urlencode
import urllib.request
import json,re
import string,secrets

from .filters import ItemFilter, ItemFilterEditkey
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


# not allowing empty editkey
class ItemFilterEditkeyView(FilterView):
    model = Item
    filterset_class = ItemFilterEditkey
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

class ItemFilterView(FilterView):
    model = Item
    filterset_class = ItemFilter
    queryset = Item.objects.filter(Q(end_date__gte=timezone.now())).order_by('-end_date')
    template_name = "wordb/item_list.html"

    strict = False  ## empty query return all objects
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


class LineMessage():
    def __init__(self, messages):
        self.messages = messages
        self.REPLY_ENDPOINT_URL = "https://api.line.me/v2/bot/message/reply"
        self.ACCESSTOKEN = "YNMkV3odM2lXeGD8An5xjABbX7Bj+NsNO6T/bTzeUWnTPSgYt+1K9V8TsYdfU5VpIXgMiWjrAjZK6dIGqtfJCNWK3Wi02alzYQyI2ypEgNsNl4ZL5TRHoi7uQyI5+5/0q7NkPJ3D7N9nAzoA3RlgxAdB04t89/1O/w1cDnyilFU="
        self.HEADER = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.ACCESSTOKEN
        }

    def reply(self, reply_token):
        body = {
            'replyToken': reply_token,
            'messages': self.messages
        }
        print(body)
        req = urllib.request.Request(self.REPLY_ENDPOINT_URL, json.dumps(body).encode(), self.HEADER)
        try:
            with urllib.request.urlopen(req) as res:
                body = res.read()
        except urllib.error.HTTPError as err:
            print(err)
        except urllib.error.URLError as err:
            print(err.reason)


## normalise Words (remove double space etc)
def normaliseWords(q_word, modifier="@"):
    flags = dict()
    words = []

    # replace symbols with space
    clean_words = re.sub(r'[^\w%@-]', r' ', q_word)
    # replace ZENKAKU symbols with space
    clean_words = re.sub(u'[■-♯]', ' ', clean_words)

    for w in clean_words.lower().split():
        if w.startswith(modifier):
            flags[w[len(modifier):]] = True
        else:
            words.append(w)
    return(" ".join(words), flags)

## check if the given string is URL
def is_url(text) :
    URL_PTN = re.compile(r"^(http|https)://")
    return URL_PTN.match(text)

## password-like strings generator for default Editkey
def pass_gen(size=12):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    chars += '%&$#()'
    return ''.join(secrets.choice(chars) for x in range(size))


####### Views
@csrf_exempt
def linebot(request):
    if request.method == 'POST':
        request_json = json.loads(request.body.decode('utf-8'))
        events = request_json['events']
        if len(events)==0: # not message received
            return HttpResponse("ok")
        data = events[0]
        reply_token = data['replyToken']
        words = data['message']['text']
        #words = request.POST.get('message')
        redirect_url = request.build_absolute_uri(reverse('index'))
        parameters = urlencode({'query': words})
        url = f'{redirect_url}?{parameters}'
        messages =  [{'type': 'text',
                'text': 'Jump to {}'.format(words),
                'quickReply': {"items": [{
                        "type": "action",
                        "action": {
                            "type": "uri",
                            "label": "Jump",
                            "uri": url
                        }
                    }]}}]
        line_message = LineMessage(messages)
        line_message.reply(reply_token)
    return HttpResponse("ok")

def ask(request):
    words = request.GET.get('words')
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            words, flags = normaliseWords(post.words_text)
            post.words_text = words
            #print(post.begin_date)
            object_list = Item.objects.filter(Q(words_text__iexact=post.words_text) & Q(end_date__gte=post.begin_date))
            if len(object_list)>0: # the key is already taken
                messages.error(request, 'The Words are already taken.')
                return render(request, 'wordb/item_ask.html', {'form': form, 'taken_till':object_list[0].end_date})
            else:
                if post.length==1:
                    post.end_date = post.begin_date + datetime.timedelta(days=1)
                elif post.length==2:
                    post.end_date = post.begin_date + datetime.timedelta(weeks=1)
                elif post.length==3:
                    post.end_date = post.begin_date + datetime.timedelta(days=31)
                elif post.length==4:
                    post.end_date = post.begin_date + datetime.timedelta(days=365)
                else:
                    messages.error(request, 'Something is wrong with the dates')
                    return redirect('/')
                post.save()
                messages.success(request, 'successfully registered "{}"'.format(post.words_text))
                return redirect('/')
    else:
        init_params = {'words_text': words,
                                 'editkey': pass_gen(20),
                                 'begin_date': timezone.now(),
                                 'length': 3
                                 }
        form = ItemForm(initial=init_params)
    return render(request, 'wordb/item_ask.html', {'form': form, 'words':words})


def edit(request, pk):
    #if request.user.is_authenticated and request.user == article.author:
    item = Item.objects.get(id=pk)
    editkey = ''
    if 'query' in request.session.keys():
        if 'editkey' in request.session['query'].keys():
            editkey = request.session['query']['editkey']
        
    if editkey != item.editkey:
        messages.error(request, 'wrong editkey')
        return redirect('update')
    elif request.method == 'POST': # update
        form = ItemEditForm(request.POST, instance=item)
        if form.is_valid():
            post = form.save(commit=False)
            words, flags = normaliseWords(post.words_text)
            post.words_text = words
            # extend rental duration
            if post.length==1:
                post.end_date = post.end_date + datetime.timedelta(days=1)
            elif post.length==2:
                post.end_date = post.end_date + datetime.timedelta(weeks=1)
            elif post.length==3:
                post.end_date = post.end_date + datetime.timedelta(days=31)
            elif post.length==4:
                post.end_date = post.end_date + datetime.timedelta(days=365)
            post.save()
            messages.success(request, 'Your Words are successfully updated!')
            return redirect('/')
    else:
        form = ItemEditForm(instance=item , initial={'length': 0})
        print(form.instance.begin_date)
        return render(request, 'wordb/item_edit.html', {'form': form, 'item':item})

    return redirect('update')

def about(request):
    if request.method == 'POST':
        if request.POST.get('stripeToken'):
            messages.success(request, 'Thank you for your support!')
    return render(request, 'wordb/about.html')
    

# showing searchbox and handling search query
def index(request):
    q_word = request.GET.get('query')
    if hasattr(request, 'session'):
        request.session.pop('query','') # clear search key
    #print(q_word)
    if not q_word:
        return render(request, 'wordb/item_index.html', {'object_list':[]})
    words, flags = normaliseWords(q_word)

    #print("key: ",q_word)
    object_list = Item.objects.filter(Q(words_text__iexact=words) & Q(end_date__gte=timezone.now()))
    if 'admin' in flags.keys():
        return redirect('admin:index')
    elif len(object_list)==0 and not 'list' in flags.keys():
        messages.error(request, '{} not found'.format(words))
        return render(request, 'wordb/item_index.html', {'object_list':object_list, 'not_found_words': words})
    elif 'list' in flags.keys():
        redirect_url = reverse('list')
        parameters = urlencode({'words_text': words})
        url = f'{redirect_url}?{parameters}'
        return redirect(url)
    elif len(object_list)==1: # hit and show
        item = object_list[0]
        item.count = F('count') + 1
        item.save()
        if item.data_text.startswith("http"):
            return redirect(item.data_text)
        else:
            return HttpResponse(item.data_text)
            
    return render(request, 'wordb/item_index.html', {'object_list':object_list})

## testing url
def test(request):
    msg = "google-site-verification: google28cb9145886e77d6.html"
    return HttpResponse(msg)

##
def dummy_add_key(request):
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
        return render(request, 'wordb/item_index.html', {'object_list':[item]})
        #return redirect("ask/")
        #return HttpResponse("Word {} updated.".format(words))
