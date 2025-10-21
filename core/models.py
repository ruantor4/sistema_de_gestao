from django.db import models
from django.contrib.auth.models import User


class LogSystem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    message = models.TextField()

    def __str__(self):
        return f"{self.timestamp} - {self.user.username} - {self.action} - {self.status}"

    class Meta:
        db_table = 'log_system'