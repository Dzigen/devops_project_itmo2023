from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseNotFound
from .models import BoxModel, ItemModel, UserModel, SessionModel 
from collections import Counter
from .utils import *
from django.urls import reverse, reverse_lazy
import hashlib
import random
from datetime import datetime
from django.db.models import Count
from django.db.models import Q


# Представление главной страницы сайта
class MainView(DataMixin, View):
    
    #
    def get(self, request):
        cur_context = self.context.copy()

        # Вычисляем количество
        # существующих коробок в системе
        boxes_c = BoxModel.objects.count()

        cur_context['boxes_count'] = boxes_c

        #
        add_auth_context(request, cur_context)

        print(f"box count: {cur_context}")

        return render(request, 'boxes/main_page.html', cur_context)

# 
class RoomView(DataMixin, View):

    # Список имён, добавленных в комнату
    room_names = []

    # Поле для передачи имени пользователя через
    # POST-запрос c целью его добавления в комнату
    name_param = 'name'

    def add_user_in_room(self, name):
        cur_name = f"{name}"
        if len(cur_name):
            self.room_names.append(cur_name)

    #
    def post(self, request):
        # Проверяем запрос на наличие атрибута
        # для добавления имени пользователя в комнату
        if self.name_param in request.POST.keys():
            self.add_user_in_room(request.POST[self.name_param])

        return redirect('room')

    #
    def get(self, request):
        cur_context = self.context.copy()

        # Сообщения для отображения в случае пустой комнаты
        people_info = 'The room is full of people who care…'

        # Проверяем запрос на наличие атрибута
        # для добавления имени пользователя в комнату
        if self.name_param in request.GET.keys():
            self.add_user_in_room(request.GET[self.name_param])

        # В зависимости от количества людей в комнате
        # формируем сообщение со списком имён для отображения
        if len(self.room_names) > 1:
            first_names = ', '.join(self.room_names[:-1])
            last_name = self.room_names[-1]
            people_info = f'There are {first_names} and {last_name} in the room.'
        elif len(self.room_names) == 1:
            people_info = f'There is {self.room_names[0]} in the room.'
        
        cur_context['people_info'] = people_info

        #
        add_auth_context(request, cur_context)

        print("room context: ", cur_context)

        return render(request, 'boxes/room_page.html', cur_context)

# Представлене страницы со списком 
# существующих коробок в системе
class BoxesView(DataMixin, View):
    
    # Поля для передачи названия коробки и цвета через
    # POST-запрос c целью её создания
    name_param = 'name'
    color_param = 'color'
    
    # Поле для возвращения статуса выполнения операции
    # создания новой коробки
    post_status_param = 'post_status'

    # Словарь возможных статусов выполнения
    # операции создания новой коробки
    response_codes = {
        'no_auth': 'user_not_auth',
        'box_exist': 'box_exist',
        'bad_color': 'bad_color',
        'bad_name': 'bad_name',
        'success': 'box_create',
        'undefined': 'undefinded_post'
    }

    response_info = {
        'user_not_auth' : {'return': 'err', 'msg': 'Error: Not authenticated user!'},
        'box_exist': { 'return': 'err', 'msg': 'Error: Similar box already exist!'},
        'bad_color' : {'return': 'err', 'msg': 'Error: That color is not appropriate!'},
        'bad_name': {'return': 'err', 'msg': 'Error: That name is not appropriate!'},
        'box_create': {'return': 'suc', 'msg': 'Success: Box has been created!'},
        'undefinded_post': {'return': 'warn', 'msg': ''}
    }

    #
    def post(self, request):

        # Создание url-адреса для перенаправления 
        # со статусом выполнения операции создания новой коробки
        def format_url(status):
            return f"{request.path}?{self.post_status_param}={status}"

        # Проверка на наличие нужных полей в запросе
        # для создания новой коробки
        post_params = request.POST.keys()
        is_post_have_name = self.name_param in post_params
        is_post_have_color = self.color_param in post_params
        if is_post_have_name and is_post_have_color:

            #
            cur_name = f"{request.POST[self.name_param]}"
            cur_color = f"{request.POST[self.color_param]}"
            print(f"posted name: {cur_name}")
            print(f"posted color: {cur_color}")

            # Валидация поля 'name'
            if not len(cur_name):
                return redirect(format_url(self.response_codes['bad_name']))

            # Валидация поля 'color'
            appropriate_colors = [pair[0] for pair in BoxModel.color.field.choices]
            if cur_color not in appropriate_colors:
                return redirect(format_url(self.response_codes['bad_color']))

            # Проверка на наличие активной
            # сессии для данного пользователя
            user_id, is_user_auth = valid_user_auth(request)
            print("user info: ", user_id, is_user_auth)
            if not is_user_auth:
                return redirect(format_url(self.response_codes['no_auth']))

            # Проверка на пересечение информации
            # существующих коробок cо значениями,
            # переданными в запросе
            box_info, is_box_exist = self.validate_box_exist(
                cur_name, cur_color)
            print("existed box info: ", box_info, is_box_exist)
            if is_box_exist:
                return redirect(format_url(self.response_codes['box_exist']))

            # В случае успешного прохождения всех проверок
            # создаём новую коробку
            BoxModel.objects.create(name=cur_name, color=cur_color, author=UserModel.objects.get(id=user_id))
            
            # Перенаправляем пользователя на страницу со списком коробок
            # и возвращаем статус успешной операции
            return redirect(format_url(self.response_codes['success']))
        
        # Перенаправляем пользователя на страницу со списком коробок
        # и возвращаем статус нераспознанного POST-запроса
        # для данного ресурса
        return redirect(format_url(self.response_codes['undefined']))

    # Проверка на существование коробки с заданной информацией
    def validate_box_exist(self, new_name, new_color):
        #
        finded_box = BoxModel.objects.all().filter(Q(name=new_name) | Q(color=new_color))
        
        #
        is_box_exist = True if len(finded_box) else False
        box_info = None
        if is_box_exist:
            box_info = 'name' if finded_box[0].name == new_name else 'color'

        return  box_info, is_box_exist 

    #
    def get(self, request):
        cur_context = self.context.copy()

        # Получаем из БД список с информацией 
        # о существующих коробках
        raw_boxes_info = BoxModel.objects.all()
        boxes_info = []
        for box in raw_boxes_info:
            user_name = box.author.name
            boxes_info.append({
                'author': user_name,
                'name': box.name,
                'color': box.color,
                'url': box.get_absolute_url()})  

        # Если было перенаправление с POST-запроса,
        # то сохраняем его сообщение 
        # для отображения во View
        get_params = request.GET.keys()
        if self.post_status_param in get_params:
            cur_status = f"{request.GET[self.post_status_param]}"
            status_info = self.response_info.get(cur_status, None)

            if status_info:
                cur_context['status'] = status_info['return']
                cur_context['msg'] = status_info['msg']

        #
        cur_context['boxes_info'] = boxes_info
        add_auth_context(request, cur_context)

        print("boxes context: ", cur_context)

        return render(request, 'boxes/box_list.html', cur_context)

#
class BoxItemsView(DataMixin, View):
    
    #
    response_codes = {
        "success": "item_added",
        "undefined": "undefined_post",
        "bad_user": "dont_have_permission",
        "bad_name": "item_name_invalid"
    }

    response_info = {
        "item_added": {"return": "suc", "msg": "Success: Item has been added!"},
        "undefined_post": {"return": "warn", "msg": ''},
        "dont_have_permission": {"return": "err", "msg": "Error: dont have permission!"},
        "item_name_invalid": {"return": "err", "msg": "Error: Item name have invalid format!"}
    }

    # Поле для возвращения статуса выполнения операции
    # добавления предмета в коробку
    post_status_param = 'post_status'
    
    #
    item_param = 'item_name'


    #
    def format_url(self, path, param, status):
        return f"{path}?{param}={status}"

    #
    def post(self, request, box_name):
        
        # Проверка на существование коробки
        # с заданным именем
        cur_box = f"{box_name}"
        box_id, is_box_valid = self.validate_boxinfo_request(cur_box)
        print("existed box: ", box_id, is_box_valid, cur_box)
        if not is_box_valid:
            raise Http404()

        # Проверка на наличие нужных атрибутов в запросе
        # для добавления нового предмета в текущую коробку
        post_params = request.POST.keys()
        is_post_have_item = self.item_param in post_params
        print("have item param: ", is_post_have_item)
        if not is_post_have_item:
            return redirect(self.format_url(request.path,
                self.response_codes['undefined']))
    
        # Проверка на наличие прав для POST-запроса
        is_author = self.validate_additem_request(request, cur_box)
        print("have perms: ", is_author)
        if not is_author:
            return redirect(self.format_url(request.path,
                self.post_status_param, 
                self.response_codes['bad_user']))
    
        # В случае прохождения проверок
        # добавляем информацию о новом предмете в коробку
        cur_item = f"{request.POST[self.item_param]}"
        ItemModel.objects.create(box_id=box_id, name=cur_item)

        #
        return redirect(self.format_url(request.path,
            self.post_status_param, self.response_codes["success"]))

    #   
    def get(self, request, box_name):
        cur_context = self.context.copy()

        # Проверка на существование коробки
        # с заданным именем
        cur_box = f"{box_name}"
        box_id, is_box_valid = self.validate_boxinfo_request(cur_box)
        if not is_box_valid:
            raise Http404()

        # Если было перенаправление с POST-запроса,
        # то сохраняем его сообщение 
        # для отображения во View
        get_params = request.GET.keys()
        if self.post_status_param in get_params:
            cur_status = f"{request.GET[self.post_status_param]}"
            status_info = self.response_info.get(cur_status, None)

            if status_info:
                cur_context['status'] = status_info['return']
                cur_context['msg'] = status_info['msg']

        #
        items_info = ItemModel.objects.filter(box_id=box_id).values('name').annotate(total=Count('*'))
        cur_context['items_info'] = list(items_info)

        #
        box_meta = BoxModel.objects.get(id=box_id)
        author_name = UserModel.objects.get(id=box_meta.author_id).name
        cur_context['box_info'] = { 'name': box_meta.name, 'color': box_meta.color, 'author': author_name }        

        #
        is_author = self.validate_additem_request(request, cur_box)
        cur_context['is_author'] = is_author

        #
        add_auth_context(request, cur_context)

        print("box items context: ", cur_context)

        return render(request, 'boxes/box_items.html', cur_context)

    # Проверка на обращение к существующей коробке
    def validate_boxinfo_request(self, box_name):
        finded_boxes = BoxModel.objects.filter(name=box_name)
        return (finded_boxes[0].pk, True) if len(finded_boxes) else (None, False)

    # Проверка на наличие необходимых прав
    # для добавления предмета в коробку
    def validate_additem_request(self, request, box_name):
        box_info = BoxModel.objects.get(name=box_name)

        session_id = request.COOKIES.get(SESSION_PARAM, False)
        if not session_id:
            return False

        user_id = SessionModel.objects.get(data=session_id).user

        return box_info.author == user_id


#
class RegisterView(DataMixin, View):
    
    #
    response_codes = {
        "user_exist": "user_already_exist",
        "success": "user_created",
        "undefined": "undefined_post",
        "bad_user": "invalid_user_data"
    }

    response_info = {
        "user_already_exist": {'return': 'err', 'msg': 'Error: That user already exist!'},
        "user_created": {'return': 'suc', 'msg': ''},
        "undefined": {'return': 'warn', 'msg': ''},
        "bad_user": {'return': 'err', 'msg': 'Error: Invalid user data!'}
    }

    #
    post_status_param = 'post_status'

    #
    name_param = 'name'
    password_param = 'password'

    #
    def post(self, request):

        #
        def format_url(path, status):
            return f"{path}?{self.post_status_param}={status}"
    
        # Проверка на наличие нужных атрибутов в запросе
        post_params = request.POST.keys()
        is_post_have_name = self.name_param in post_params
        is_post_have_pass = self.password_param in post_params
        if is_post_have_name and is_post_have_pass:

            #
            cur_name = f"{request.POST[self.name_param]}"
            cur_pass = f"{request.POST[self.password_param]}"
            print("user: ", cur_name, cur_pass)

            #
            is_data_valid = self.validate_new_user(cur_name, cur_pass)
            if not is_data_valid:
                return redirect(format_url(request.path, self.response_codes['user_exist']))

            #
            hashed_passwd = hashlib.md5(cur_pass.encode()).hexdigest()
            UserModel.objects.create(name=cur_name, password=hashed_passwd)
            return redirect(format_url(reverse('login'), self.response_codes["success"]))

        #
        return redirect(format_url(request.path, 
            self.response_codes['undefined']))
    
    #
    def validate_new_user(self, name, passwd):
        hashed_passwd = hashlib.md5(passwd.encode()).hexdigest()
        same_users = UserModel.objects.all().filter(name=name, password=hashed_passwd)
        return True if not len(same_users) else False

    #   
    def get(self, request):
        cur_context = self.context.copy()

        # Проверка на наличие активной
        # сессии для данного пользователя
        user_id, is_user_auth = valid_user_auth(request)
        print("auth: ", user_id, is_user_auth)
        if is_user_auth:
            return redirect('boxes')

        # Проверка наличия информации об ошибке
        # при регистрации для отображения во View
        get_params = request.GET.keys()
        if self.post_status_param in get_params:
            cur_status = f"{request.GET[self.post_status_param]}"
            status_info = self.response_info.get(cur_status, None)

            if status_info:
                cur_context['status'] = status_info['return']
                cur_context['msg'] = status_info['msg']

        cur_context['form_name'] = 'SignUp'
        print("signup context: ", cur_context)        
        
        return render(request, 'boxes/form_page.html', cur_context)

class LoginView(DataMixin, View):

    #
    name_param = 'name'
    password_param = 'password'

    #
    response_codes = {
        'doesn_exist': 'user_doesnt_exist',
        'reg_success': 'user_created',
        'login': 'login_success',
        'undefined': 'undefinded_post'
    }

    response_info = {
        'user_doesnt_exist': {'return': 'err', 'msg': 'Error: That user doesnt exist!'},
        'user_created': {'return': 'suc', 'msg': 'Success: New user has been created!'},
        'login_success': {'return': 'suc', 'msg': ''},
        'undefinded_post': {'return': 'warn', 'msg': ''}
    }

    post_status_param = 'post_status'

    #
    session_param = 'session_id'

    #
    def post(self, request):

        #
        def format_url(path, status):
            return f"{path}?{self.post_status_param}={status}"

        # Проверка на наличие нужных атрибутов в запросе
        post_params = request.POST.keys()
        is_post_have_name = self.name_param in post_params
        is_post_have_pass = self.password_param in post_params
        if is_post_have_name and is_post_have_pass:

            #
            cur_name = f"{request.POST[self.name_param]}"
            cur_pass = f"{request.POST[self.password_param]}"
            print("user: ", cur_name, cur_pass)

            # Если таких данных пользователя нет в система,
            # то отображаем соответствующее предупреждение
            user_id, is_user_valid = self.validate_user(cur_name, cur_pass)
            if not is_user_valid:
                return redirect(format_url(request.path, self.response_codes['doesn_exist']))

            # Генерируем сессионный ключи
            # и производим успешное перенаправление
            session = self.gen_session_id()
            response = redirect(format_url(reverse('boxes'), self.response_codes['login']))
            expired_date = set_cookie(response, self.session_param, session)
            print("expired date: ", expired_date)

            SessionModel.objects.create(user_id=user_id, data=session,
                expired_date=expired_date)

            return response
   
        #
        return redirect(format_url(request.path, 
            self.response_codes['undefined']))
    
    # Генерация сессионного ключа
    # для авторизации пользователя в системе
    def gen_session_id(self):
        date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        random_num = random.random()
        raw_string = f"{date} {random_num}".encode('utf-8')
        return hashlib.md5(raw_string).hexdigest()

    # Проверка наличия зарегистрированного пользователя
    # с заданными name и password в системе
    def validate_user(self, name, passwd):
        hashed_passwd = hashlib.md5(passwd.encode()).hexdigest()
        finded_users = UserModel.objects.all().filter(name=name, password=hashed_passwd)
        return (finded_users[0].pk, True) if len(finded_users) else (None, False)

    #   
    def get(self, request):
        cur_context = self.context.copy()

        # Проверка на наличие активной
        # сессии для данного пользователя
        user_id, is_user_auth = valid_user_auth(request)
        print("auth: ", user_id, is_user_auth)
        if is_user_auth:
            return redirect('boxes')

        # Проверка наличия информации 
        # при авторизации/регистрации для отображения во View
        get_params = request.GET.keys()
        if self.post_status_param in get_params:
            cur_status = f"{request.GET[self.post_status_param]}"
            status_info = self.response_info.get(cur_status, None)

            if status_info:
                cur_context['status'] = status_info['return']
                cur_context['msg'] = status_info['msg']            

        cur_context['form_name'] = 'LogIn'        
        return render(request, 'boxes/form_page.html', cur_context)

#
def logout_view(request):
    response = redirect('home')

    print("logout context before: ",DataMixin.context)

    # Удаление активной сессии пользователя
    user_id, is_user_auth = valid_user_auth(request)
    print("auth: ", user_id, is_user_auth)
    if is_user_auth:
        SessionModel.objects.get(data=request.COOKIES[SESSION_PARAM]).delete()
        response.delete_cookie(SESSION_PARAM)

    print("logout context after: ",DataMixin.context)

    return response

#
def page_not_found(request, exception):
    return HttpResponseNotFound(f"<h1>Страница не найдена</h1><p>{exception}</p>")