from user.models import ScheduleUser


def getProfileById(userId: int):
    user = ScheduleUser.objects.get(id=userId)
    return {
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'profile_image_url': user.profile_image_url,
        'locale': user.locale,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
    }
