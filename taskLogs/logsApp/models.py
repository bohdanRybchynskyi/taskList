from django.db import models


class LogEntry(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    user = models.CharField(max_length=100)
    operation = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.datetime} - {self.operation} - {self.title} - {self.user} - {self.message}"

