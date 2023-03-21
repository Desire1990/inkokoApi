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

	def getGroups(self, user):
		groups = []
		if user.is_superuser:
			groups.append("admin")
		for group in user.groups.all():
			groups.append(group.name)
		return groups

	def validate(self, attrs):
		data = super(TokenPairSerializer, self).validate(attrs)
		data['services'] = [group.name for group in self.user.groups.all()]
		data['is_admin'] = self.user.is_superuser
		data['groups'] = self.getGroups(self.user)
		data['username'] = self.user.username
		data['id'] = self.user.id
		logins = LastLogin.objects.all()
		if(logins):
			last_login = logins.first()
			last_login.date = timezone.now()
			last_login.save()
		else:
			LastLogin().save()
		return data

class GroupSerializer(serializers.ModelSerializer):

	class Meta:
		model = Group
		fields = "__all__"
		depth=2



class UserSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True)
	groups = serializers.SerializerMethodField()

	def get_groups(self, user):
		groups = []
		if user.is_superuser:
			groups.append("admin")
		for group in user.groups.all():
			groups.append(group.name)
		return groups

	class Meta:
		model = User
		exclude = "last_login","is_staff","email","date_joined","user_permissions"

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
		depth=1


class ProduitSerializer(serializers.ModelSerializer):
	class Meta:
		model = Produit
		fields = '__all__'
		# depth=1

class AchatSerializer(serializers.ModelSerializer):
	produit_id = serializers.SerializerMethodField()

	def to_representation(self, obj):
		representation = super().to_representation(obj)
		representation['produit'] = str(obj.produit)
		representation['user'] = str(obj.user)
		return representation

	def get_produit_id(self, obj):
		return obj.produit.id

	class Meta:
		model = Achat
		fields = "__all__"
		read_only_fields = "date", "user", "prix_unitaire"

class RationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Ration
		fields = '__all__'
		depth=1


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

class PrixSerializer(serializers.ModelSerializer):
	class Meta:
		model = Prix
		fields = '__all__'
		# depth=1
		
class PouletPrixSerializer(serializers.ModelSerializer):
	class Meta:
		model = PouletPrix
		fields = '__all__'
		# depth=1

class OeufSerializer(serializers.ModelSerializer):
	class Meta:
		model = Oeuf
		fields = '__all__'
		depth=1

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

class TransferSerializer(serializers.ModelSerializer):
	class Meta:
		model = Transfer
		fields = '__all__'
		depth=1
