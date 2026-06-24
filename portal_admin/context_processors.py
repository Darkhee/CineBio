from django.contrib.auth.models import User


def admin_context(request):  
    uid = request.session.get('portal_admin_uid')
    admin_username = request.session.get('portal_admin_username', '')

    if uid and not admin_username:
        try:
            user = User.objects.get(pk=uid)
            admin_username = user.username
        except User.DoesNotExist:
            pass

    return {'admin_username': admin_username}
