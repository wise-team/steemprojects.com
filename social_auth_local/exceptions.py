from social_core.exceptions import AuthCanceled


class AuthCanceled__RedirectToLogin(AuthCanceled):
    def __init__(self, backend_name):
        self.backend_name = backend_name
