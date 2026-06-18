from django.contrib.auth.models import User


def admin_context(request):
    """
    Inyecta el usuario administrador (autenticado vía sesión propia)
    en todos los templates de portal_admin.
    """
    uid = request.session.get('portal_admin_uid')
    admin_username = request.session.get('portal_admin_username', '')

    if uid and not admin_username:
        # Por si acaso, reconstruir desde BD
        try:
            user = User.objects.get(pk=uid)
            admin_username = user.username
        except User.DoesNotExist:
            pass

    return {'admin_username': admin_username}
