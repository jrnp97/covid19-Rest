from rest_framework.serializers import ModelSerializer

from api.models import GeneralData


class GeneralDataSerializer(ModelSerializer):
    class Meta:
        model = GeneralData
        fields = '__all__'
