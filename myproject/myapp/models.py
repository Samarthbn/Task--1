from django.db import models


class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=128)
    is_passed = models.BooleanField(default=False)  # Indicates whether the user passed or failed


    def __str__(self):
        return self.username

class Question(models.Model):
    question = models.TextField()
    correct_answer = models.CharField(max_length=255)

class UserAnswer(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=255)
