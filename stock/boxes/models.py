from django.db import models
from datetime import datetime
from django.urls import reverse

#
class BoxModel(models.Model):
	APPROPRIATE_COLORS = [
    ('red', 'red color'),
    ('green', 'green color'),
    ('blue', 'blue color'),
    ('yellow', 'yellow color'),
    ('magenta', 'magenta')]

	name = models.CharField(max_length=255, blank=False) 
	color = models.CharField(max_length=20, blank=False, 
		choices=APPROPRIATE_COLORS)
	author = models.ForeignKey('UserModel', on_delete=models.PROTECT, blank=False)
	create_date = models.DateField(auto_now_add=True)

	#
	def get_absolute_url(self):
		return reverse('box_items', kwargs={'box_name': self.name})  

#
class ItemModel(models.Model):
	name = models.CharField(max_length=255, blank=False) 
	box = models.ForeignKey('BoxModel', on_delete=models.PROTECT, blank=False)
	add_date = models.DateField(auto_now_add=True)
#
class UserModel(models.Model):
	name = models.CharField(max_length=255, blank=False) 
	password = models.TextField(blank=False) 
	create_date = models.DateField(auto_now_add=True)

#
class SessionManager(models.Manager):
	def get_queryset(self):
		# deleting expired sessions
		date_now = datetime.now().strftime("%Y-%m-%d")
		print("date now: ", date_now)

		#expired_session = SessionModel.objects.all().filter(expired_date__lte=date_now) 
		#expired_session.delete()
		
		#
		return super().get_queryset()

#
class SessionModel(models.Model):
	objects = SessionManager()

	user = models.ForeignKey('UserModel', on_delete=models.CASCADE, blank=False)
	data = models.TextField(blank=False)
	create_date = models.DateField(auto_now_add=True)
	expired_date = models.DateField()

