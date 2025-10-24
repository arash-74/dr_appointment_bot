from rest_framework import serializers
from jdatetime import datetime
from app.models import Appointment, User


class AppointmentSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(read_only=True, source='user.chat_id')

    class Meta:
        model = Appointment
        fields = '__all__'


class AppointmentBookingSerializer(serializers.ModelSerializer):
    chat_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Appointment
        fields = ['chat_id']

    def update(self, instance, validated_data):
        try:
            user = User.objects.get(chat_id=int(validated_data['chat_id']))
        except Exception as e:
            raise serializers.ValidationError({'error': e})
        if user.is_active:
            instance.user = user
            instance.booking_date = datetime.now()
            instance.save()
        return instance


class UserBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'from_date', 'booking_date']


class UserCreateSerializer(serializers.ModelSerializer):
    chat_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = User
        fields = ['chat_id']
class UserUnbookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id']
    def update(self, instance, validated_data):
        print(instance)
        instance.user = None
        instance.save()
        return instance
