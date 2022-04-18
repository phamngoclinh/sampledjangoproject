from functools import wraps
from django.shortcuts import redirect, reverse
from django.contrib import messages


def partners_only(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
    if not request.partner:
      messages.error(request, message='Vui lòng đăng nhập để truy cập trang này')
      return redirect(reverse('login') + f'?next={request.path}')
    return function(request, *args, **kwargs)
  return wrap
