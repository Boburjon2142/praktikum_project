from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class OnlyLoggedSuperUser(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin to ensure the user is logged in and is an admin (staff member).
    """

    def test_func(self):
        return self.request.user.is_superuser
