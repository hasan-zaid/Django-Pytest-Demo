import datetime
import pytest

# from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question, Choice

class TestQuestionModel:
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        assert future_question.was_published_recently() is False
        
    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        assert old_question.was_published_recently() is False

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        assert recent_question.was_published_recently() is True

# class QuestionModelTests(TestCase):
#     def test_was_published_recently_with_future_question(self):
#         """was_published_recently() returns False for questions whose pub_date is in the future."""
#         time = timezone.now() + datetime.timedelta(days=30)
        
#         future_question = Question(pub_date=time)
        
#         self.assertIs(future_question.was_published_recently(), False)
        
#     def test_was_published_recently_with_old_question(self):
#         """
#         was_published_recently() returns False for questions whose pub_date
#         is older than 1 day.
#         """
#         time = timezone.now() - datetime.timedelta(days=1, seconds=1)
#         old_question = Question(pub_date=time)
#         self.assertIs(old_question.was_published_recently(), False)


#     def test_was_published_recently_with_recent_question(self):
#         """
#         was_published_recently() returns True for questions whose pub_date
#         is within the last day.
#         """
#         time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
#         recent_question = Question(pub_date=time)
#         self.assertIs(recent_question.was_published_recently(), True)
        
def create_question(question_text, days):
    """Create a question with the given `question_text` and published the given number of `days` offset to now (negative for questions published in the past, positive for questions that have yet to be published)."""
    time = timezone.now() + datetime.timedelta(days=days)
    
    return Question.objects.create(question_text=question_text, pub_date=time)

@pytest.mark.django_db
class TestQuestionIndexView:
    def test_no_questions(self, client):
        response = client.get(reverse("polls:index"))
        assert response.status_code == 200
        assert "No polls are available." in response.content.decode()
        assert len(response.context["latest_question_list"]) == 0

    def test_past_question(self, client):
        question = create_question("Past question.", days=-30)
        create_choice(question, "Choice 1")
        create_choice(question, "Choice 2")
        response = client.get(reverse("polls:index"))
        assert question.question_text in response.content.decode()

    def test_future_question(self, client):
        create_question("Future question.", days=30)
        response = client.get(reverse("polls:index"))
        assert "No polls are available." in response.content.decode()
        assert len(response.context["latest_question_list"]) == 0

    def test_future_question_and_past_question(self, client):
        q1 = create_question("Past question.", days=-30)
        create_choice(q1, "Choice 1")
        create_choice(q1, "Choice 2")
        
        q2 = create_question("Future question.", days=30)
        create_choice(q2, "Choice 1")
        create_choice(q2, "Choice 2")
        
        response = client.get(reverse("polls:index"))
        assert q1.question_text in response.content.decode()
        assert len(response.context["latest_question_list"]) == 1

    def test_two_past_questions(self, client):
        q1 = create_question("Past question 1.", days=-30)
        create_choice(q1, "Choice 1")
        create_choice(q1, "Choice 2")
        
        q2 = create_question("Past question 2.", days=-5)
        create_choice(q2, "Choice 1")
        create_choice(q2, "Choice 2")
        
        response = client.get(reverse("polls:index"))
        assert q1.question_text in response.content.decode()
        assert q2.question_text in response.content.decode()

# class QuestionIndexViewTests(TestCase):
#     def test_no_questions(self):
#         """If no questions exist, an appropriate message is displayed."""
#         response = self.client.get(reverse("polls:index"))
        
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "No polls are available.")
#         self.assertQuerySetEqual(response.context["latest_question_list"], [])
        
#     def test_past_question(self):
#         """Questions with a pub_date in the past are displayed on the index page."""
#         question = create_question(question_text="Past question.", days=-30)
#         create_choice(question, "Choice 1")
#         create_choice(question, "Choice 2")
        
#         response = self.client.get(reverse("polls:index"))
        
#         self.assertContains(response, question.question_text)
        
#     def test_future_question(self):
#         """Questions with a pub_date in the future aren't displayed on the index page."""
#         create_question(question_text="Future question.", days=30)
        
#         response = self.client.get(reverse("polls:index"))
        
#         self.assertContains(response, "No polls are available.")
#         self.assertQuerySetEqual(response.context["latest_question_list"], [])
        
#     def test_future_question_and_past_question(self):
#         """Even if both past and future questions exist, only past questions are displayed."""
#         q1 = create_question(question_text="Past question.", days=-30)
#         create_choice(q1, "Choice 1")
#         create_choice(q1, "Choice 2")
        
#         q2 = create_question(question_text="Future question.", days=30)
#         create_choice(q2, "Choice 1")
#         create_choice(q2, "Choice 2")
        
#         response = self.client.get(reverse("polls:index"))
        
#         self.assertContains(response, q1.question_text)
    
#     def test_two_past_questions(self):
#         """The questions index page may display multiple questions."""
#         q1 = create_question(question_text="Past question 1.", days=-30)
#         create_choice(q1, "Choice 1")
#         create_choice(q1, "Choice 2")
        
#         q2 = create_question(question_text="Past question 2.", days=-5)
#         create_choice(q2, "Choice 1")
#         create_choice(q2, "Choice 2")
        
#         response = self.client.get(reverse("polls:index"))
        
#         self.assertContains(response, q1.question_text)

@pytest.mark.django_db
class TestQuestionDetailView:
    def test_future_question(self, client):
        question = create_question(question_text="future question", days=5)
        response = client.get(reverse("polls:detail", args=(question.id,)))
        assert response.status_code == 404
    
    def test_past_question(self, client):
        question = create_question("Past question.", days=-5)
        create_choice(question, "Choice 1")
        create_choice(question, "Choice 2")
        response = client.get(reverse("polls:detail", args=(question.id,)))
        assert question.question_text in response.content.decode()
        
# class QuestionDetailViewTests(TestCase):
#     def test_future_question(self):
#         """ The detail view of a question with a pub_date in the future returns a 404 not found. """
#         time = timezone.now() + datetime.timedelta(days=5)
    
#         question = Question.objects.create(question_text="future question", pub_date=time)
        
#         response = self.client.get(reverse("polls:detail", args=(question.id,)))
        
#         self.assertEqual(response.status_code, 404)
    
#     def test_past_question(self):
#         """ The detail view of a question with a pub_date in the past displays the question's text. """
        
#         question = create_question(question_text="Past question.", days=-5)
#         create_choice(question, "Choice 1")
#         create_choice(question, "Choice 2")
        
#         response = self.client.get(reverse("polls:detail", args=(question.id,)))
        
#         self.assertContains(response, question.question_text)
        
def create_choice(question, choice_text):
    """ Create a choice with the given `question` and `choice_text`. """
    Choice.objects.create(question=question, choice_text=choice_text)

@pytest.mark.django_db
class TestQuestionChoices:
    def test_question_without_choices_view(self, client):
        question = create_question("Question without choices.", days=-5)
        response = client.get(reverse("polls:index"))
        assert len(response.context["latest_question_list"]) == 0
        
    def test_question_with_choices_view(self, client):
        question = create_question("Question with choices.", days=-5)
        create_choice(question, "Choice 1")
        create_choice(question, "Choice 2")
        response = client.get(reverse("polls:index"))
        assert question.question_text in response.content.decode()

    def test_question_without_choices_detail(self, client):
        question = create_question("Question without choices.", days=-5)
        response = client.get(reverse("polls:detail", args=(question.id,)))
        assert response.status_code == 404
    
    def test_question_with_choices_detail(self, client):
        question = create_question("Question with choices.", days=-5)
        create_choice(question, "Choice 1")
        create_choice(question, "Choice 2")
        response = client.get(reverse("polls:detail", args=(question.id,)))
        assert question.question_text in response.content.decode()       


# class QuestionChoicesTest(TestCase):
#     def test_question_without_choices_view(self):
#         """ The view of a question without choices shouldn't be listed. """
        
#         question = create_question(question_text="Question without choices.", days=-5)
        
#         response = self.client.get(reverse("polls:index"))
        
#         self.assertNotContains(response, question.question_text)
        
#     def test_question_with_choices_view(self):
#         """ The view of a question with at least two choices should be listed. """
        
#         question = create_question(question_text="Question with choices.", days=-5)
#         create_choice(question, "Choice 1")
#         create_choice(question, "Choice 2")
        
#         response = self.client.get(reverse("polls:index"))
        
#         self.assertContains(response, question.question_text)
    
#     def test_question_without_choices_detail(self):
#         """ The detail view of a question without choices should return 404. """
        
#         question = create_question(question_text="Question without choices.", days=-5)
        
#         response = self.client.get(reverse("polls:detail", args=(question.id,)))
        
#         self.assertEqual(response.status_code, 404)
    
#     def test_question_with_choices_detail(self):
#         """ The detail view of a question with at least two choices should display the question's text. """
        
#         question = create_question(question_text="Question with choices.", days=-5)
#         create_choice(question, "Choice 1")
#         create_choice(question, "Choice 2")
        
#         response = self.client.get(reverse("polls:detail", args=(question.id,)))
        
#         self.assertContains(response, question.question_text)
        
        
@pytest.mark.django_db
class TestQuestionResultsView:
    def test_future_question_results(self, client):
        question = create_question("Future question.", days=5)
        response = client.get(reverse("polls:results", args=(question.id,)))
        assert response.status_code == 404
        
    def test_past_question_results(self, client):
        question = create_question("Past question.", days=-5)
        create_choice(question, "Choice 1")
        create_choice(question, "Choice 2")
        response = client.get(reverse("polls:results", args=(question.id,)))
        assert question.question_text in response.content.decode()
        
    def test_past_question_without_choices_result(self, client):
        question = create_question("Past question.", days=-5)
        response = client.get(reverse("polls:results", args=(question.id,)))
        assert response.status_code == 404

@pytest.mark.django_db        
class TestVote:
    def test_vote_without_selected_choice_past_question(self, client):
        question = create_question("Question without choices.", days=-5)
        response = client.post(reverse("polls:vote", args=(question.id,)))
        assert response.status_code == 200
    
    def test_vote_with_selected_choice_past_question(self, client):
        question = create_question("Question with choices.", days=-5)
        create_choice(question, "Choice 1")
        create_choice(question, "Choice 2")
        response = client.post(reverse("polls:vote", args=(question.id,)), {"choice": 1})
        assert response.status_code == 302
        
    def test_vote_without_selected_choice_future_question(self, client):
        question = create_question("Question without choices.", days=5)
        response = client.post(reverse("polls:vote", args=(question.id,)))
        assert response.status_code == 400
    
    def test_vote_with_selected_choice_future_question(self, client):
        question = create_question("Future question.", days=5)
        create_choice(question, "Choice 1")
        create_choice(question, "Choice 2")
        response = client.post(reverse("polls:vote", args=(question.id,)), {"choice": 1})
        assert response.status_code == 400