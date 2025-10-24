from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, UpdateAPIView, CreateAPIView
from rest_framework.response import Response

from app.models import Appointment, User
from app.serializers import AppointmentSerializer, AppointmentBookingSerializer, UserBookingSerializer, \
    UserCreateSerializer, UserUnbookSerializer


class AppointmentListView(ListAPIView):
    serializer_class = AppointmentSerializer
    queryset = Appointment.objects.all()

    def get_queryset(self):
        query = super().get_queryset()
        _filter = self.kwargs.get('filter')
        if _filter == 'only_book':
            query = query.filter(is_booking=True)
        if _filter == 'only_unbook':
            query = query.filter(is_booking=False)
        return query


# @api_view(['POST'])
# def appointment_booking_view(request, pk):
#     data = request.data
#     try:
#         appointment = Appointment.objects.get(pk=pk)
#     except Appointment.DoesNotExist:
#         return Response({'id': 'cannot find appointment'}, status=status.HTTP_404_NOT_FOUND)
#     serializer = AppointmentBookingSerializer(appointment, data=request.data)
#     serializer.is_valid(raise_exception=True)
#     serializer.save()
#     return Response({}, status=status.HTTP_200_OK)
class AppointmentBookingView(UpdateAPIView):
    serializer_class = AppointmentBookingSerializer
    queryset = Appointment.objects.all()
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        if self.get_object().is_booking:
            raise ValidationError('this appointment already is booked')
        return super().update(request, *args, **kwargs)


@api_view(['GET'])
def user_booking_list(request, chat_id):
    try:
        user = User.objects.get(chat_id=chat_id)
    except User.DoesNotExist:
        return Response({'error': 'user does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    appointments_list = user.bookings.all()
    serializer = UserBookingSerializer(appointments_list, many=True)
    return Response(serializer.data)


class UserBookList(ListAPIView):
    serializer_class = UserBookingSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        try:
            queryset = super().get_queryset().get(chat_id=self.kwargs.get('chat_id'))
        except Exception as e:
            raise ValidationError({'error': e})
        return queryset.bookings.all()


class CreateUserAPI(CreateAPIView):
    serializer_class = UserCreateSerializer
    queryset = User.objects.all()

    def perform_create(self, serializer):
        User.objects.get_or_create(chat_id=serializer.validated_data['chat_id'])

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
            except Exception as e:
                return Response({'msg': e}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'msg': 'success'}, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_400_BAD_REQUEST)


class AppointmentRemove(UpdateAPIView):
    serializer_class = UserUnbookSerializer
    queryset = Appointment.objects.all()
