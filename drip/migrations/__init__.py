try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
else:
    User = get_user_model()

# from:
# kevindias.com/writing/django-custom-user-models-south-and-reusable-apps/
# With the default User model these will be 'auth.User' and 'auth.user'
# so instead of using orm['auth.User'] we can use orm[user_orm_label]
USER_ORM_LABEL = '{0}.{1}'.format(User._meta.app_label,
                                  User._meta.object_name)
USER_MODEL_LABEL = '{0}.{1}'.format(User._meta.app_label,
                                    User._meta.module_name)
