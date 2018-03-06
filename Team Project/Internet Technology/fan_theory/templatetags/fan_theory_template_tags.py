from django import template
from fan_theory.models import Category

register = template.Library()

@register.inclusion_tag('fan_theory/cats.html')
def get_category_list(cat=None):
	return {'cats': Category.objects.all(), 'act_cat': cat}

@register.filter
def fetch_item(dictionary, key_name):
	return dictionary[str(key_name)]