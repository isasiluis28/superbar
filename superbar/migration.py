import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'superbar.settings')
django.setup()

from django.db import connections
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import ConnectionDoesNotExist
from django.utils import timezone
from django.contrib.auth.models import User, Permission


def setup_cursor():
    try:
        cursor = connections['legacy'].cursor()
    except ConnectionDoesNotExist:
        print "Legacy database is not configured"
        return None
    else:
        return cursor


def import_users():
    cursor = setup_cursor()
    if cursor is None:
        return
    ## it's important selecting the id field, so that we can keep the publisher - book relationship
    sql = """SELECT id, password, last_login, is_superuser, first_name, last_name, email, is_staff,
             is_active, date_joined, username FROM auth_user
     """
    cursor.execute(sql)
    for row in cursor.fetchall():
        usuario = User(id=row[0], password=row[1], last_login=timezone.make_aware(row[2]), is_superuser=row[3],
                       first_name=row[4], last_name=row[5], email=row[6], is_staff=row[7], is_active=row[8],
                       date_joined=timezone.make_aware(row[9]), username=row[10])
        usuario.save()


# importar los permisos de usuarios
def import_user_permissions():
    cursor = setup_cursor()
    if cursor is None:
        return
    sql = """
        SELECT id, user_id, permission_id FROM auth_user_user_permissions
    """
    cursor.execute(sql)
    for row in cursor.fetchall():
        try:
            usuario = User.objects.get(id=row[1])
        except ObjectDoesNotExist:
            print "user not found with id %s" % row[1]
            continue
        else:
            permiso = Permission.objects.get(id=row[2])
            usuario.user_permissions.add(permiso)


def main():
    # pass
    import_users()
    import_user_permissions()


if __name__ == "__main__":
    main()
