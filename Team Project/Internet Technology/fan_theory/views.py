from datetime import datetime
from django.shortcuts import render
from fan_theory.models import Category, UserProfile, Comment, FanTheory, User2Comment, Following, Tag
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from fan_theory.forms import CategoryForm, UserForm, UserProfileForm, CommentForm, FanTheoryForm
from django.shortcuts import redirect
from django.db.models import FieldDoesNotExist
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from social_django.models import UserSocialAuth
from django.contrib.auth.models import User


def index(request):
	category_list = Category.objects.order_by('-likes')[:5]
	fan_theories_list = FanTheory.objects.order_by('-views')[:5]
	context_dict = {'categories': category_list, 'fan_theories': fan_theories_list}

	visitor_cookie_handler(request)
	context_dict['visits'] = request.session['visits']
	
	if not request.user.is_anonymous:
		context_dict['my_fan_theories'] = FanTheory.objects.filter(author=request.user).order_by('-views')[:5]
		context_dict['followers'] = request.user.followers.all()[:5]
		context_dict['following'] = request.user.followees.all()[:5]

	response = render(request, 'fan_theory/index.html', context=context_dict)
	return response

def about(request):
	context_dict = {}
	print(request.method)
	print(request.user)
	if request.session.test_cookie_worked():
		print("TEST COOKIE WORKED!")
		request.session.delete_test_cookie()
	visitor_cookie_handler(request)
	context_dict['visits'] = request.session['visits']

	return render(request, 'fan_theory/about.html', context_dict)

def show_category_list(request):
	try:
		category_list = Category.objects.all
		context_dict = {'category_list' : category_list}
	except Category.DoesNotExist:
		context_dict['category'] = None

	return render(request, 'fan_theory/category_list.html', context_dict)

def show_category(request, category_name_slug):
	context_dict = {}
	default_sort_method = 'title'
	
	try:
		category = Category.objects.get(slug=category_name_slug)
		
		sort_method = request.GET.get('order_by')
		try:
			FanTheory._meta.get_field(sort_method)
		except FieldDoesNotExist:
			sort_method = default_sort_method
		if sort_method != 'title' and sort_method != 'author':
			sort_method = "-"+sort_method
		fan_theories = FanTheory.objects.filter(category=category).order_by(sort_method)
		context_dict['sort_method'] = sort_method
		
		context_dict['fan_theories'] = fan_theories
		context_dict['category'] = category
		try:
			tags = Tag.objects.filter(category=category)
			context_dict['tags'] = tags
		except Tag.DoesNotExist:
			context_dict['tags'] = None
	except Category.DoesNotExist:
		context_dict['category'] = None
		context_dict['fan_theories'] = None

	return render(request, 'fan_theory/category.html', context_dict)

def show_fan_theory(request, category_name_slug, fan_theory_name_slug):
	context_dict = {}
	try:
		fan_theory = FanTheory.objects.get(slug=fan_theory_name_slug)
		context_dict['fan_theory'] = fan_theory
		comments = Comment.objects.filter(commented_on=fan_theory)
		context_dict['user_id'] = request.user.id
		for comment in comments:
			comment.votes = User2Comment.objects.filter(comment=comment, direction=1).count() - \
							User2Comment.objects.filter(comment=comment, direction=-1).count()
			user2comment = User2Comment.objects.filter(comment=comment, user=request.user.id)
			comment.downvote = ''
			comment.upvote = ''
			if user2comment.count() > 0 and user2comment[0].direction == -1:
				comment.downvote = 'downvote-on'
			if user2comment.count() > 0 and user2comment[0].direction == 1:
				comment.upvote = 'upvote-on'
		#comments_by_likes = list(Comment.objects.filter(commented_on=fan_theory).order_by('tree_id', 'level', '-created'))
	except Category.DoesNotExist:
		context_dict['fan_theory'] = None
	except Comment.DoesNotExist:
		context_dict['comments'] = None

	context_dict['comments'] = comments

	if fan_theory:
		fan_theory.views = view_counter(request, fan_theory)
		fan_theory.save()

	form = CommentForm()
	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			#form.save(commit=True)
			comment_form = form.save(commit=False)
			if request.user.is_authenticated():
				comment_form.author = request.user
				comment_form.commented_on = fan_theory
				print(comment_form.reply_id)
				if comment_form.reply_id >= 0:
					comment_form.parent = Comment.objects.filter(id=int(comment_form.reply_id)).first()
				fan_theory.comment_count += 1
				fan_theory.save()
				comment_form.save()

				return HttpResponseRedirect(reverse('show_fan_theory', args=(category_name_slug, fan_theory_name_slug)))
			else:
				print("User not logged in!")
				return index(request)
		else:
			print(form.errors)
			return index(request)

	context_dict['form'] = form

	return render(request, 'fan_theory/fan_theory.html', context_dict)

@login_required
def add_category(request):
	form = CategoryForm()
	if request.method == 'POST':
		form = CategoryForm(request.POST)
		if form.is_valid():
			form.save(commit=True)

			#return index(request)
			return HttpResponseRedirect(reverse('category_list'))
		else:
			print(form.errors)

	return render(request, 'fan_theory/add_category.html', {'form': form})

@login_required
def add_fan_theory(request, category_name_slug):
	try:
		category = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		category = None
	try:
		user = request.user
	except request.user.DoesNotExist:
		user = None
	# form = FanTheoryForm()
	form = FanTheoryForm(category_name=category)
	the_tags = Tag.objects.filter(category=category)

	tag_choices = []
	# for the_tag in the_tags:
	# 	tag_choices.append(tuple(the_tag))


	# form.fields["tags"].choices = tag_choices
	print(the_tags)
	if request.method == 'POST':
		form = FanTheoryForm(request.POST, category_name=category)
		# form = FanTheoryForm(request.POST)
		if form.is_valid():

			print(form['tags'])

			if category and user:
				fan_theory = form.save(commit=False)
				fan_theory.category = category
				fan_theory.author = user
				fan_theory.views = 0
				
				# thing = fan_theory.save()
				# thing.tags = Tag.objects.filter(category=category)
				fan_theory.save()
				form.save_m2m()
				
				

				return HttpResponseRedirect(reverse('show_category', args=(category_name_slug,)))
		else:
			print(form.errors)
	context_dict = {'form':form, 'category': category}
	
	return render(request, 'fan_theory/add_fan_theory.html', context_dict)

def show_user_profile(request, user_profile_name):
	user_profile = None
	try:
		user_profile = UserProfile.objects.get(user=User.objects.get(username=user_profile_name))
	except:
		user_profile = User.objects.get(username=user_profile_name)
	context_dict = {'user_profile': user_profile}

	if request.method == 'POST':
		print("POST METHOD")
		try:
			current_follow_relation = (Following.objects.filter(follower=request.user)).get(followee=user_profile.user)			
			# Already following so unfollow.
			current_follow_relation.delete()
		except Following.DoesNotExist:
			# Not following so now follow.
			follow_relationship = Following(followee=user_profile.user, follower=request.user)
			follow_relationship.save()
	
	context_dict['my_fan_theories'] = FanTheory.objects.filter(author=request.user).order_by('-views')[:5]
	context_dict['followers'] = user_profile.user.followers.all()[:5]
	context_dict['following'] = user_profile.user.followees.all()[:5]
	context_dict['you_are_following'] = False

	for relationship in context_dict['followers']:
		if relationship.follower == request.user:
			context_dict['you_are_following'] = True

	return render(request, 'fan_theory/user_profile.html', context_dict)

@login_required
def edit_user_profile(request):
	user_profile = None
	try:
		user_profile = UserProfile.objects.get(user=request.user.id)
	except:
		user_profile = request.user
	context_dict = {'user_profile': user_profile}

	if request.method == 'POST':
		profile_form = UserProfileForm(instance=context_dict['user_profile'], data=request.POST)
		if profile_form.is_valid():
			profile = profile_form.save(commit=False)
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
			profile.save()
		else:
			print(profile_form.errors)
	else:
		profile_form = UserProfileForm(instance=context_dict['user_profile'])

	context_dict['profile_form'] = profile_form

	return render(request, 'fan_theory/edit_profile.html', context_dict)

def register(request):
	registered = False
	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)
		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			user.set_password(user.password)
			user.save()
			profile = profile_form.save(commit=False)
			profile.user = user
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
			profile.save()
			registered = True
		else:
			print(user_form.errors, profile_form.errors)
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()
	return render(request, 'fan_theory/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if user:
			if user.is_active:
				login(request, user)

				return HttpResponseRedirect(reverse('index'))
			else:
				return HttpResponse("Your fan_theory account is disabled.")
		else:
			print("Invalid login details: {0}, {1}".format(username, password))
			return HttpResponse("Invalid login details supplied.")
	else:
		return render(request, 'fan_theory/login.html', {})

@login_required
def user_logout(request):
	logout(request)

	return HttpResponseRedirect(reverse('index'))

def get_server_side_cookie(request, cookie, default_val=None):
	val = request.session.get(cookie)
	if not val:
		val = default_val
	return val

def visitor_cookie_handler(request):
	visits = int(get_server_side_cookie(request, 'visits', '1'))
	last_visit_cookie = get_server_side_cookie(request,'last_visit',str(datetime.now()))
	last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
	if (datetime.now() - last_visit_time).days > 0:
		visits = visits + 1
		request.session['last_visit'] = str(datetime.now())
	else:
		visits = 1
		request.session['last_visit'] = last_visit_cookie
	request.session['visits'] = visits

def view_counter(request, fan_theory):
	views = fan_theory.views
	last_visit_cookie = get_server_side_cookie(request,'last_visit',str(datetime.now()))
	last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
	if (datetime.now() - last_visit_time).seconds > 0:
		views = views + 1
		request.session['last_visit'] = str(datetime.now())
	else:
		request.session['last_visit'] = last_visit_cookie
	return views

@login_required
def vote(request):
	if request.method == 'GET':
		user_id = request.GET.get('user')
		comment_id = request.GET.get('comment')
		direction = request.GET.get('direction')
		comment = User2Comment.objects.filter(user_id=user_id,comment_id=comment_id)
		if direction == 0:
			User2Comment.objects.filter(user_id=user_id, comment_id=comment_id).delete()
		elif comment.count() > 0:
			com = User2Comment.objects.get(user_id=user_id, comment_id=comment_id)
			com.direction = direction
			com.save()
		else:
			user2comment = User2Comment(user_id=user_id,comment_id=comment_id,direction=direction)
			user2comment.save()
		return render(request, 'fan_theory/fan_theory.html')
	else:
		HttpResponse("Error")

@login_required
def my_comments(request):
	authorcomments = Comment.objects.filter(author_id=request.user.id)
	comments = []
	for user2comment in authorcomments:
		comment = Comment.objects.get(id = user2comment.id)
		ft = FanTheory.objects.get(id = comment.commented_on_id)
		comment.theory_slug = ft.slug
		comment.theory_title = ft.title
		comment.vote = User2Comment.objects.filter(comment_id=comment.id, direction=1).count() -\
					   User2Comment.objects.filter(comment_id=comment.id, direction=-1).count()
		comment.category_slug = Category.objects.get(id = ft.category_id).slug
		now = datetime.now()
		delta = now - comment.posted_at.replace(tzinfo=None)
		if delta.days < 1:
			if delta.seconds/3600 < 1:
				if delta.seconds/60 < 1:
					comment.delta = str(delta.seconds) + " seconds ago"
				else:
					comment.delta = str(int(delta.seconds/60)) + " minutes ago"
			else:
				comment.delta = str(int(delta.seconds/3600)) + " hours ago"
		else:
			comment.delta = str(delta.days) + " days ago"

		comments.append(comment)
	context_dict = { "comments" : comments}
	return render(request, 'fan_theory/my_comments.html', context_dict)

@login_required
def settings(request):
    user = request.user

    try:
        twitter_login = user.social_auth.get(provider='twitter')
    except UserSocialAuth.DoesNotExist:
        twitter_login = None

    try:
        facebook_login = user.social_auth.get(provider='facebook')
    except UserSocialAuth.DoesNotExist:
        facebook_login = None

    try:
        google_login = user.social_auth.get(provider='google')
    except UserSocialAuth.DoesNotExist:
        facebook_login = None

    can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

    return render(request, 'fan_theory/settings.html', {
        'twitter_login': twitter_login,
        'facebook_login': facebook_login,
        'can_disconnect': can_disconnect,
    })

@login_required
def password(request):
    if request.user.has_usable_password():
        PasswordForm = PasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm

    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordForm(request.user)
    return render(request, 'fan_theory/password.html', {'form': form})

