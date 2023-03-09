from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.validators import UnicodeUsernameValidator
from .models import *
from django.db import transaction
from django.contrib.auth.models import Group
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password


class TokenPairSerializer(TokenObtainPairSerializer):
	def validate(self, attrs):
		data = super(TokenPairSerializer, self).validate(attrs)
		data['groups'] = [group.name for group in self.user.groups.all()]
		data['id'] = self.user.id
		data['username'] = self.user.username
		data['first_name'] = self.user.first_name
		data['last_name'] = self.user.last_name
		data['is_staff'] = self.user.is_staff
		return data


class GroupSerializer(serializers.ModelSerializer):

	class Meta:
		model = Group
		fields = "__all__"
		depth=2


class UserSerializer(serializers.ModelSerializer):
	@transaction.atomic()
	def update(self, instance, validated_data):
		user = instance
		username = validated_data.get('username')
		first_name = validated_data.get('first_name')
		last_name = validated_data.get('last_name')
		nouv_password = validated_data.get('nouv_password')
		anc_password = validated_data.get('anc_password')
		if check_password(anc_password, self.context['request'].user.password):
			if username:
				user.username = username
			if first_name:
				user.first_name = first_name
			if last_name:
				user.last_name = last_name
			if password:
				user.set_password(password)
			user.save()
			return user
		return user

	class Meta:
		model = User
		read_only_fields = "is_active", "is_staff"
		exclude = "last_login", "is_staff", "date_joined"
		extra_kwargs = {
			'username': {
				'validators': [UnicodeUsernameValidator()]
			}
		}



class ClientSerializer(serializers.ModelSerializer):
	class Meta:
		model = Client
		fields = '__all__'
		# depth=1


class ResponsableSerializer(serializers.ModelSerializer):
	class Meta:
		model = Responsable
		fields = '__all__'
		# depth=1


class SalleSerializer(serializers.ModelSerializer):
	class Meta:
		model = Salle
		fields = '__all__'
		# depth=1


class ProduitSerializer(serializers.ModelSerializer):
	class Meta:
		model = Produit
		fields = '__all__'
		# depth=1


class RationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Ration
		fields = '__all__'
		# depth=1


class PoulleMorteSerializer(serializers.ModelSerializer):
	class Meta:
		model = PoulleMorte
		fields = '__all__'
		# depth=1


class PoulleVenduSerializer(serializers.ModelSerializer):
	class Meta:
		model = PoulleVendu
		fields = '__all__'
		# depth=1

class OeufSerializer(serializers.ModelSerializer):
	class Meta:
		model = Oeuf
		fields = '__all__'
		# depth=1

class OeufVenduSerializer(serializers.ModelSerializer):
	class Meta:
		model = OeufVendu
		fields = '__all__'
		# depth=1

class PerteSerializer(serializers.ModelSerializer):
	class Meta:
		model = Perte
		fields = '__all__'
		# depth=1
