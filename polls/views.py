# from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.core.urlresolvers import reverse
from .models import Choice, Question


def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:10]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

def most_voted(request):
    from django.db.models import Sum
    mostVoted = Question.objects.annotate(mostvoted=Sum('choice__votes')) \
                .order_by('-mostvoted')[:5]
    context = {'most_voted_list': mostVoted}
    return render(request, 'polls/most_voted.html', context)


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})

def modal_choice(request):
    from django.core import serializers
    question_id = request.GET['id']
    question = get_object_or_404(Question, pk=question_id)
    predata = question.choice_set.all()
    data = serializers.serialize('json', predata,
                    fields=('choice_text', 'votes'))
    return HttpResponse(data, content_type='application/json')

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})

def create(request):
    from django.utils import timezone
    from django.utils.datastructures import MultiValueDictKeyError
    try:
        title = request.POST.get('title', False)
        if title:
            q = Question(question_text=request.POST['title'], pub_date=timezone.now())
            q.save()
            for row in [request.POST.get('ch%s' % row, False) for row in range(1,5)]:
                if row:
                    q.choice_set.create(choice_text=row, votes=0)
            latest_question_list = Question.objects.order_by('-pub_date')[:5]
            context = {'latest_question_list': latest_question_list}
            return render(request, 'polls/index.html', context)
        else:
            return render(request, 'polls/create.html')
    except MultiValueDictKeyError:
        return render(request, 'polls/create.html')


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))