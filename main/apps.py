from django.apps import AppConfig, apps


# Patch from_persistent_id, since it only supports int-IDs by default (and we have a uuid)
@classmethod
def from_persistent_id_patched(cls, persistent_id, for_verify=False):
    from django_otp.models import Device
    """
    Loads a device from its persistent id::

        device == Device.from_persistent_id(device.persistent_id)

    :param bool for_verify: If ``True``, we'll load the device with
        :meth:`~django.db.models.query.QuerySet.select_for_update` to
        prevent concurrent verifications from succeeding. In which case,
        this must be called inside a transaction.

    """
    device = None

    try:
        model_label, device_id = persistent_id.rsplit('/', 1)
        app_label, model_name = model_label.split('.')

        device_cls = apps.get_model(app_label, model_name)
        if issubclass(device_cls, Device):
            # don't assume all IDs are int
            try:
                device_id = int(device_id)
            except ValueError:
                pass
            device_set = device_cls.objects.filter(id=device_id)
            if for_verify:
                device_set = device_set.select_for_update()
            device = device_set.first()
    except (ValueError, LookupError):
        pass

    return device


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        from django_otp.models import Device
        # Patch OTP
        Device.from_persistent_id = from_persistent_id_patched
