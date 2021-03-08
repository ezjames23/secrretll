from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Topic, Entry
from .forms import TopicForm, EntryForm

# Create your views here.
def index(request):
    """The homepage for learning Log"""
    return render(request, 'learning_logs/index.html')

def _get_topics_for_user(user):
    " returns a queryset of topics the user can access "
    q = Q(public=True)
    # if django < 1.10 you want "user.is_authenticated()" (with parens)
    if user.is_authenticated:
       # adds user's own private topics to the query
       q = q | Q(public=False, owner=user)

    return Topic.objects.filter(q)

def topics(request):
    """show all topics"""
    topics = _get_topics_for_user(request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)


def topic(request, topic_id):
    """Show a single topic and all its entries"""
    topics = _get_topics_for_user(request.user)
    topic = get_object_or_404(topics, id=topic_id)
    # make sure that the topic belongs to the current user
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic':topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    """Add a new topic"""
    if request.method != 'POST':
        #No date submitted then create a blank form
        form = TopicForm()
    else:
        # POST data submitted; process date
        form =  TopicForm(request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return HttpResponseRedirect(reverse('learning_logs:topics'))

    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    """add a new entry for a particular topic"""
    topic = Topic.objects.get(id=topic_id)

    if request.method != 'POST':
        #no data submitted; create a blank form
        form = EntryForm()
    else:
        # POST data submitted; process data
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return HttpResponseRedirect(reverse('learning_logs:topic',
args=[topic_id]))

    context = {'topic': topic, 'form': form, 'topic_id':topic_id}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    """edit an existing entry"""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        """initial request;pre-fill form with the current entry"""
        form = EntryForm(instance=entry)
    else:
        # POST data submitted;process data
        form = EntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('learning_logs:topic', args=[topic.id]))
    
    context = {'entry': entry, 'topic': topic, 'form':form}
    return render(request, 'learning_logs/new_entry.html', context)