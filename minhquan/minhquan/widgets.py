from django import forms
# from django.template.loader import render_to_string
# from django.utils.safestring import mark_safe


class SearchInputWidget(forms.widgets.Input):
  class Media:
    js = ('js/forms/widgets/search-input.js',)
    
  template_name = 'forms/widgets/search_input.html'

  def __init__(self, attrs=None):
    super().__init__(attrs)

  def get_context(self, name, value, attrs):
    context = super().get_context(name, value, attrs)
    context['widget']['suffix'] = '__search_input'
    
    if 'search_url' in self.attrs:
      context['widget']['url'] = self.attrs.get('search_url')
    else:
      context['widget']['url'] = f'/search-{name}/'
    
    if 'search_key' in self.attrs:
      context['widget']['search_key'] = self.attrs.get('search_key')
    else:
      context['widget']['search_key'] = 'search_text'
    
    if 'related_data' in self.attrs:
      context['widget']['related_data'] = self.attrs.get('related_data')

    if 'search_fields' in self.attrs:
      search_fields_custom = self.attrs.get('search_fields')
      context['widget']['search_fields'] = search_fields_custom
    else:
      context['widget']['search_fields'] = 'name'

    if self.choices and value:
      context['widget']['queryset'] = self.choices.queryset
      context['widget']['selected_result'] = self.choices.queryset.get(pk=value)

    if 'add_form' in self.attrs:
      add_form = self.attrs.get('add_form')
      if not 'form' in add_form:
        raise Exception('add_form attribute must be have a key of form')
      if not 'action' in add_form:
        raise Exception('add_form attribute must be have a key of action')
      # for fieldname in add_form.get('form').fields:
      #   add_form.get('form').fields[fieldname].disabled = True
      context['widget']['add_form'] = add_form
    
    return context
    # return {
    #   "widget": {
    #     "name": name,
    #     "is_hidden": self.is_hidden,
    #     "required": self.is_required,
    #     "value": self.format_value(value),
    #     "attrs": self.build_attrs(self.attrs, attrs),
    #     "template_name": self.template_name,
    #   },
    # }

  def render(self, name, value, attrs=None, renderer=None):
    context = self.get_context(name, value, attrs)
    return super().render(name, value, attrs, renderer)
    # return mark_safe(render_to_string(self.template_name, context))