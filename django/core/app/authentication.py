from app.models import User


class UserBackEnd:
    def authenticate(self, request,username=None, password=None):
        if username is None:
            return None
        try:
            if username.isdigit():
                user = User.objects.get(chat_id=int(username))
                return user
            else:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    return user
                return None
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None
    def get_user(self,user_id):
        try:
            return User.objects.get(pk=user_id)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None