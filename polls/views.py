from typing import Any
from django.db.models import Q, Count
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Question, Choice

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions (not including those published in the future)."""
        query = Question.objects.filter(
            pub_date__lte=timezone.now()
            ).order_by(
                "-pub_date"
                ).annotate(
                    num_choices=Count('choice')
                    ).filter(
                        num_choices__gte=2
                        )[:5]
        
        return query


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/details.html"
    
    def get_queryset(self):
        """Excludes any questions that aren't published yet."""
        queryset = super().get_queryset()
        
        filtered_queryset = queryset.filter(
            pub_date__lte=timezone.now()
        ).annotate(
            num_choices=Count('choice')
        ).filter(
            num_choices__gte=2
        )
        return filtered_queryset


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"
    
    def get_queryset(self):
        """Excludes any questions that aren't published yet."""
        queryset = super().get_queryset()
        
        filtered_queryset = queryset.filter(
            pub_date__lte=timezone.now()
        ).annotate(
            num_choices=Count('choice')
        ).filter(
            num_choices__gte=2
        )
        return filtered_queryset

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if question.pub_date > timezone.now():
        return HttpResponseBadRequest("Voting is not allowed for questions with future publication date.")

    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(request, "polls/details.html", {"question": question, "error_message": "You didn't select a choice."})
    else:
        selected_choice.votes += 1
        selected_choice.save()
        
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
