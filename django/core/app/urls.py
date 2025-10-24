from django.urls import path

from app import views

app_name = 'app'
urlpatterns = [
    path('create-user/',views.CreateUserAPI.as_view(),name="create user"),
    path('appointment/list/', views.AppointmentListView.as_view(), name='appointment list'),
    path('appointment/list/<str:filter>', views.AppointmentListView.as_view(), name='appointment list booking'),
    path('appointment/booking/<int:pk>', views.AppointmentBookingView.as_view(), name='appointment create'),
    path('user-booking/<int:chat_id>', views.UserBookList.as_view(), name='user booking'),
    path('appointment/user-booking/<int:chat_id>', views.user_booking_list, name='user booking detail'),
    path('user-unbook/<int:pk>',views.AppointmentRemove.as_view(),name='user unbook')
]