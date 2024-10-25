from django.contrib.sessions.backends.db import SessionStore
from django_otp.middleware import OTPMiddleware as OTPInternalMiddleware
from typing import Optional
from django.contrib.auth import logout
from django.db.models import Q
from django_otp import DEVICE_ID_SESSION_KEY

from main.models import SessionTreeEdge


# helper that returns true if the current session is the master
def is_master_session(request):
        # Use the cached version if available
        cached: Optional[bool] = request.session.get("is_master_session")
        if cached is None:
            # this session is probably older than the version that introduced session trees, so log out to migrate
            if not SessionTreeEdge.objects.filter(Q(parent__session_key=request.session.session_key) | Q(child__session_key=request.session.session_key)).exists():
                logout(request)
                return False
            # We are master if we are not a child
            return not SessionTreeEdge.objects.filter(child=request.session.session_key).exists()
        return cached


# this essestially does request.user.is_verified(),
# but works with non-master sessions as well (is_verified is
# delegated to the parent in this case)
def check_is_2fa_authenticated_tree_aware(request):
    # TODO maybe cache this result? This is used in the critical login_check path
    if not request.user.is_authenticated:
        return False
    if is_master_session(request):
        return request.user.is_verified()

    else:
        try:
            parent = SessionTreeEdge.objects.get(child=request.session.session_key).parent
        # Orphan, log out in this case
        except SessionTreeEdge.DoesNotExist:
            logout(request)
            return False

        parent_session = SessionStore(session_key=parent.session_key)
        persistent_id = parent_session.get(DEVICE_ID_SESSION_KEY)
        device = (
            # black magic on internal objects (bad)
            OTPInternalMiddleware._device_from_persistent_id(None, persistent_id)
            if persistent_id
            else None
        )

        if (device is not None) and (device.user_id != request.user.pk):
            device = None

        return device is not None
