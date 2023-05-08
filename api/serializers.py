from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.validators import UnicodeUsernameValidator
from .models import *
from django.db import transaction
from django.contrib.auth.models import Group
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.db.models import Sum


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
		# logins = LastLogin.objects.all()
		# if(logins):
		# 	last_login = logins.first()
		# 	last_login.date = timezone.now()
		# 	last_login.save()
		# else:
		# 	LastLogin().save()
		return data

class GroupSerializer(serializers.ModelSerializer):

	class Meta:
		model = Group
		fields = "__all__"
		depth=2

class LastLoginSerializer(serializers.ModelSerializer):

	def to_representation(self, obj):
		representation = super().to_representation(obj)
		representation['user'] = str(obj.user)
		return representation
		
	class Meta:
		model = LastLogin
		fields = "__all__"


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
	total = serializers.SerializerMethodField()


	def get_total(self, obj):
		totaux= Salle.objects.all().aggregate(total=Sum('quantite_oeuf'))
		return totaux["total"]
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
		# representation['produit'] = str(obj.produit)
		representation['user'] = str(obj.user)
		return representation

	def get_produit_id(self, obj):
		return obj.produit.id

	class Meta:
		model = Achat
		fields = "__all__"
		read_only_fields = "date", "user", "prix_unitaire"
		depth=1

class VenteSerializer(serializers.ModelSerializer):
	commande_id = serializers.SerializerMethodField()
	produit_id = serializers.SerializerMethodField()

	def to_representation(self, obj):
		representation = super().to_representation(obj)
		representation['produit'] = str(obj.produit)
		representation['commande'] = str(obj.commande)
		return representation

	def get_produit_id(self, obj):
		return obj.produit.id

	def get_commande_id(self, obj):
		return obj.commande.id	

	class Meta:
		model = Vente
		fields = '__all__'
		depth=1

class RationSerializer(serializers.ModelSerializer):
	user_id = serializers.SerializerMethodField()
	responsable_id = serializers.SerializerMethodField()
	user = serializers.ReadOnlyField()

	def to_representation(self, obj):
		representation = super(RationSerializer, self).to_representation(obj)
		representation['user'] = str(obj.user)
		representation['responsable'] = str(obj.responsable)
		# last_login = LastLogin.objects.first()
		# try:
		# 	last_login = LastLogin.objects.first()
		# 	last_login.date = timezone.now()
		# except:
		# 	last_login = LastLogin()
		# 	last_login.save()
		return representation

	def get_user_id(self, obj):
		return obj.user.id

	def get_responsable_id(self, obj):
		if(obj.responsable): return obj.responsable.id
		return None

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

	def to_representation(self, obj):
		representation = super().to_representation(obj)
		representation['client'] = str(obj.client)
		representation['salle'] = str(obj.salle)
		return representation
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
	user_id = serializers.SerializerMethodField()
	client_id = serializers.SerializerMethodField()
	prix_id = serializers.SerializerMethodField()
	user = serializers.ReadOnlyField()

	def to_representation(self, obj):
		representation = super(OeufVenduSerializer, self).to_representation(obj)
		representation['user'] = str(obj.user)
		representation['client'] = str(obj.client)
		representation['prix'] = str(obj.prix)
		# last_login = LastLogin.objects.first()
		# try:
		# 	last_login = LastLogin.objects.first()
		# 	last_login.date = timezone.now()
		# except:
		# 	last_login = LastLogin()
		# 	last_login.save()
		return representation

	def get_user_id(self, obj):
		return obj.user.id

	def get_client_id(self, obj):
		if(obj.client): return obj.client.id
		return None
	def get_prix_id(self, obj):
		if(obj.prix): return obj.prix.id
		return None

	class Meta:
		model = Commande
		fields = '__all__'
		# depth=1

class PerteSerializer(serializers.ModelSerializer):
	salle_id = serializers.SerializerMethodField()

	def to_representation(self, obj):
		representation = super().to_representation(obj)
		representation['salle'] = str(obj.salle)
		# representation['user'] = str(obj.user)
		return representation

	def get_salle_id(self, obj):
		return obj.salle.id

	class Meta:
		model = Perte
		fields = '__all__'
		read_only_fields = "date", 
		depth=1

class TransferSerializer(serializers.ModelSerializer):

	def to_representation(self, obj):
		representation = super().to_representation(obj)
		representation['taux'] = str(obj.taux)
		representation['user'] = str(obj.user)
		return representation
	class Meta:
		model = Transfer
		fields = '__all__'
		depth=1

class TauxSerializer(serializers.ModelSerializer):

	class Meta:
		model = Taux
		fields = '__all__'
		depth=1

class DepenseSerializer(serializers.ModelSerializer):

	# def to_representation(self, obj):
	# 	representation = super().to_representation(obj)
	# 	representation['user']=str(obj.user)
	# 	return representation

	class Meta:
		model = Depense
		fields = '__all__'
		depth=1

class PaymentSerializer(serializers.ModelSerializer):

	def to_representation(self, obj):
		representation = super().to_representation(obj)
		representation['responsable']=str(obj.responsable)
		return representation
		
	class Meta:
		model = Payment
		fields = '__all__'
		# depth=1


class StatSerializer(serializers.Serializer):
	date = serializers.DateTimeField()
	salle = serializers.CharField(max_length=200)
	pouletmorte = serializers.CharField(max_length=200)
	pouletvendu = serializers.CharField(max_length=200)
	pouletrestant = serializers.CharField(max_length=200)


