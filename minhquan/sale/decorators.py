from functools import wraps
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.sessions.models import Session

def logged_in_required(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
    if not request.session.session_key:
      return JsonResponse({
        'success': False,
        'message': 'Unauthorized'
      })
    session = Session.objects.get(session_key=request.session.session_key)
    return function(request, *args, **kwargs)
  return wrap
