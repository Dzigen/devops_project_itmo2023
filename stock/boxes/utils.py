from .models import UserModel, SessionModel 
import datetime
from django.urls import reverse, reverse_lazy

SESSION_PARAM = 'session_id'

#
def valid_user_auth(reuqest):
    user_id = None
    is_user_auth = False

	#
    cookies_params = reuqest.COOKIES.keys()
    if SESSION_PARAM in cookies_params:
		#
        cur_session = reuqest.COOKIES[SESSION_PARAM]
        session_info = SessionModel.objects.filter(data=cur_session)

		#
        if len(session_info):
            user_id = session_info[0].user.pk
            is_user_auth = True
        else:
            pass
            #print("HERE")
            #reuqest.delete_cookie(SESSION_PARAM)

    return user_id, is_user_auth

#
def set_cookie(response, key, value, days_expire=7):
    if days_expire is None:
        max_age = 24 * 60 * 60  # one day
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
        "%Y-%m-%d",
    )

    response.set_cookie(key, value, expires=expires)
    return expires

#
def add_auth_context(request, context):
    user_id, is_user_auth = valid_user_auth(request)
    context['is_auth'] = is_user_auth
    if is_user_auth:
        user_name = UserModel.objects.get(pk=user_id).name
        context['user_name'] = user_name

class DataMixin:
    context = {
        'login_page': reverse_lazy('login'),
        'logout_page': reverse_lazy('logout'),
        'signup_page': reverse_lazy('register'),
        'room_page': reverse_lazy('room'),
        'boxes_page': reverse_lazy('boxes'),
        'main_page': reverse_lazy('home')
    }