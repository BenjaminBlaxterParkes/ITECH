from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey


# Create your models here.

class Category(models.Model):
	name = models.CharField(max_length=128, unique=True)
	views = models.IntegerField(default=0)
	likes = models.IntegerField(default=0)
	slug = models.SlugField(unique=True)

	class Meta:
		verbose_name_plural = 'Categories'

	def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super(Category, self).save(*args, **kwargs)
	
	def __str__(self):
		return self.name

class Tag(models.Model):
	name = models.CharField(max_length=32)
	category = models.ForeignKey(Category)

	def __str__(self):
		return self.name

class FanTheory(models.Model):
	category = models.ForeignKey(Category)
	author = models.ForeignKey(User)
	title = models.CharField(max_length=128, unique=True)
	text_content = models.CharField(max_length=5000)
	views = models.IntegerField(default=0)
	slug = models.SlugField(unique=True)
	comment_count = models.IntegerField(default=0)
	tags = models.ManyToManyField(Tag)

	class Meta:
		verbose_name_plural = 'FanTheories'

	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		super(FanTheory, self).save(*args, **kwargs)

	def __str__(self):
		return self.title

class UserProfile(models.Model):
	user = models.OneToOneField(User)

	biography = models.CharField(max_length=256)
	picture = models.ImageField(default='profile_images/profile-pictures.png', upload_to='profile_images', blank=True)
	slug = models.SlugField(unique=True)
	tags = models.ManyToManyField(Tag)

	def save(self, *args, **kwargs):
		self.slug = slugify(self.user.username)
		super(UserProfile, self).save(*args, **kwargs)

	def __str__(self):
		return self.user.username

class Comment(MPTTModel):
	author = models.ForeignKey(User)
	commented_on = models.ForeignKey(FanTheory)
	parent = TreeForeignKey('self', related_name='children', null=True, db_index=True)
	comment = models.CharField(max_length=512)
	posted_at = models.DateTimeField(auto_now_add=True)
	reply_id = models.IntegerField(default=-1)

	def __str__(self):
		return self.comment

class User2Comment(models.Model):
	user = models.ForeignKey(User)
	comment = models.ForeignKey(Comment)
	direction = models.SmallIntegerField(default=0)

class Following(models.Model):
	followee = models.ForeignKey(User, related_name='followers')
	follower = models.ForeignKey(User, related_name='followees')

	def __str__(self):
		return self.follower.username + " follows " + self.followee.username
