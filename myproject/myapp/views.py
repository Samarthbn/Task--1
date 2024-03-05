from django.shortcuts import render
from .models import *
from rest_framework.decorators import api_view
from django.shortcuts import render
import random
from .serializers import *
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect
from django.contrib.auth.models import User



def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        hashed_password = make_password(password)  # Hash the password
        user = User.objects.create_user(username=username, email=email, password=hashed_password)
        customer = Customer.objects.create(first_name=first_name, last_name=last_name, username=username, email=email, password=hashed_password)

        return redirect('login')  
    return render(request, 'registration.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = Customer.objects.get(username=username)
        except Customer.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid username or password'})

        if check_password(password, user.password):
            # Reset user's score when they log in
            if 'user_score' in request.session:
                del request.session['user_score']
            request.session['user_id'] = user.username
            return redirect('/get-random-question/')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')



def get_random_question(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/login/')
    
    # Reset user's score at the beginning of each session
    if 'user_score' not in request.session:
        request.session['user_score'] = 0

    if request.method == 'POST':
        question_id = request.POST.get('question_id')
        user_answer = request.POST.get('user_answer')

        try:
            question = Question.objects.get(question=question_id)
        except Question.DoesNotExist:
            return redirect('/login/')  

        correct_answer = question.correct_answer

        # Fetch the Customer instance corresponding to the user_id
        try:
            customer = Customer.objects.get(username=user_id)
        except Customer.DoesNotExist:
            return redirect('/login/')

        # Save user's answer with the Customer instance
        user_answer_obj = UserAnswer(user=customer, question=question, user_answer=user_answer)
        user_answer_obj.save()

        # Check if the user's answer is correct
        if user_answer.strip().lower() == correct_answer.strip().lower():
            # Increment user's score by 1
            request.session['user_score'] += 1

        # Check if the user has passed or failed based on the score logic
        if request.session['user_score'] >= 3:
            customer.is_passed = True
        else:
            customer.is_passed = False
        customer.save()

        # Check if the user has answered 5 questions
        user_answer_count = UserAnswer.objects.filter(user=customer).count()
        if user_answer_count >= 5:
            # User has answered 5 questions, show the result
            res = "Passed" if customer.is_passed else "Failed"
            return render(request, 'result.html', {'username': user_id, 'score': request.session['user_score'], 'res': res})

        # Retrieve a new random question
        all_question_ids = Question.objects.exclude(question=question_id).values_list('pk', flat=True)
        new_question_id = random.choice(all_question_ids)
        new_question = Question.objects.get(pk=new_question_id)
        return render(request, 'question.html', {'question': new_question.question})

    else:
        # Retrieve a random question
        all_question_ids = Question.objects.values_list('pk', flat=True)
        random_question_id = random.choice(all_question_ids)
        random_question = Question.objects.get(pk=random_question_id)
        return render(request, 'question.html', {'question': random_question.question})
