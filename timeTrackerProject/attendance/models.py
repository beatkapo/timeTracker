from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    user_id = models.ForeignKey(User, null=False, unique=True, on_delete=models.CASCADE)
    is_working = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.employee} - {self.check_in}"