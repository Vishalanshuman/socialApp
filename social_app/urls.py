from django.contrib import admin
from django.urls import path
from . import views,friends_view

urlpatterns = [
    path("signup/",views.SignupView.as_view(),name="register"),
    path("login/",views.LoginView.as_view(),name="login"),
    path("logout/",views.LogoutView.as_view(),name="logout"),
    path("user-search/",views.UserSearchView.as_view(),name="user_search"),

    # friend requests
    path('friend-request/send/', friends_view.SendFriendRequestView.as_view(), name='send_friend_request'),
    path('friend-request/respond/', friends_view.RespondFriendRequestView.as_view(), name='respond_friend_request'),
    path('friends/', friends_view.ListFriendsView.as_view(), name='list-friends'),
    path('friend-request/pending/', friends_view.ListPendingRequestsView.as_view(), name='list_pending_requests'),


]