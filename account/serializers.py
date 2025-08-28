from rest_framework import serializers
from .models import organization, User

class OrganizationSerializer(serializers.ModelSerializer):
    """
    Serializer for Organization model
    """
    class Meta:
        model = organization
        fields =['id', 'name', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    """
    serializer for User model
    """

    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id','email','name','role','organization']
        read_only_fields = ['is_active','is_staff','created_at']

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True,required=True,style={'input_type':'password'})
    organization_name = serializers.CharField(write_only=True, required=True, max_length=255)

    class Meta:
        model = User
        fields = ['email','name','password','role','organization_name']

    def create(self,validated_data):
        organization_name = validated_data.pop('organization_name')
        organization_name, created = organization.objects.get_or_create(name=organization_name)

        user = User.objects.create_user(
            email=validated_data['email'],
            name = validated_data['name'],
            password=validated_data['password'],
            role=validated_data['role'],
            organization=organization_name
        )
        return user