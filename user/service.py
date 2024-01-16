from user.models import ScheduleUser


def getProfileById(id: int):
    user = ScheduleUser.objects.get(id=id)
    return {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'profile_image_url': user.profile_image_url,
        'locale': user.locale,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
    }
