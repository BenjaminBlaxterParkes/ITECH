from django import forms
from django.contrib.auth.models import User
from fan_theory.models import Category, UserProfile, Comment, FanTheory, Tag

class CategoryForm(forms.ModelForm):
	name = forms.CharField(max_length=128, help_text="Please enter the category name:")
	views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
	likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
	slug = forms.CharField(widget=forms.HiddenInput(), required=False)
	
	class Meta:
		model = Category
		fields = ('name',)

class FanTheoryForm(forms.ModelForm):

	def __init__(self,*args,**kwargs):
		self.category_name = kwargs.pop('category_name')
		super(FanTheoryForm,self).__init__(*args,**kwargs)
		self.fields["tags"].widget = forms.CheckboxSelectMultiple()
		self.fields["tags"].queryset = Tag.objects.filter(category=self.category_name)


	title = forms.CharField(max_length=128, help_text="Please enter the title of the fan theory:")
	text_content = forms.CharField(widget=forms.Textarea(attrs={'rows':15, 'cols':100}), max_length=5000, help_text="Please enter the fan theory:")
	views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
	slug = forms.CharField(widget=forms.HiddenInput(), required=False)

	# Comedy Sci-Fi Action Romance Horror

	# some_choices = (('Comedy', 'Comedy'),('Sci-Fi', 'Sci-Fi'),('Action', 'Action'),('Romance', 'Romance'),('Horror', 'Horror'))

	# tags = forms.ModelMultipleChoiceField(
    #     queryset = Tag.objects.all(), # not optional, use .all() if unsure
    #     widget  = forms.CheckboxSelectMultiple,
    # )
	

	
	class Meta:
		model = FanTheory
		exclude = ('author', 'category',)
	comment_count = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())
	
	class Meta:
		model = User
		fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
	biography = forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols':100}), max_length=256)
	class Meta:
		model = UserProfile
		fields = ('biography', 'picture')

class CommentForm(forms.ModelForm):
	comment = forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols':100}), max_length=128, help_text="Enter the comment:")
	
	class Meta:
		model = Comment
		fields = ('comment', 'reply_id', )
	reply_id = forms.IntegerField(widget=forms.HiddenInput(), initial=-1)
