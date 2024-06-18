from django.urls import path
from dj_rest_auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
    LogoutView,
)
from dj_rest_auth.registration.views import RegisterView
from thecart_auth.views import (
    UsersListView,
    UserDetailView,
    TokenBasedLoginView,
    migrate_stuff,
    RegisterUSerView,
)

app_name = "thecart_auth"
urlpatterns = [
    path("signup/", RegisterUSerView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("login/token/", TokenBasedLoginView.as_view(), name="token_login"),
    path("password/reset/", PasswordResetView.as_view(), name="password_reset"),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("password/change/", PasswordChangeView.as_view(), name="change"),
    path("users/", UsersListView.as_view(), name="users"),
    path("users/<uuid:pk>/", UserDetailView.as_view(), name="user_details"),
    path("users/details/", UserDetailView.as_view(), name="own_details"),
]
