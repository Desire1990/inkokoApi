from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group

from datetime import datetime, timedelta, date


type_poulet=(
	('poulet en chair', 'poulet en chair'),
	('poulet pondeuse', 'poulet pondeuse'),
	)

class LastLogin(models.Model):
	id = models.SmallAutoField(primary_key=True)
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	date = models.DateTimeField(default=timezone.now, editable=False)

class Client(models.Model):
	id = models.SmallAutoField(primary_key=True)
	nom = models.CharField(max_length=32)
	tel = models.CharField(max_length=24, unique=True)

	class Meta:
		unique_together = ('nom', 'tel')

	def __str__(self):
		return f"{self.nom} {self.tel}"

class Responsable(models.Model):
	id = models.SmallAutoField(primary_key=True)
	nom = models.CharField(max_length=100)
	telephone = models.CharField(max_length=24, unique=True)
	date = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('nom', 'telephone')

	def __str__(self):
		return f"{self.nom} {self.telephone}"


class PouletPrix(models.Model):
	id = models.SmallAutoField(primary_key=True)
	prix = models.FloatField(default=30000)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.prix}"


class Salle(models.Model):
	id = models.SmallAutoField(primary_key=True)
	responsable = models.ForeignKey(Responsable, on_delete=models.PROTECT)
	prix = models.ForeignKey(PouletPrix, on_delete=models.PROTECT)
	nom = models.CharField(max_length=200, null=False, blank=False, unique=True)
	type_poulle = models.CharField(max_length= 200, choices=type_poulet)
	quantite = models.FloatField(default=0)
	quantite_oeuf = models.FloatField(default=0, editable=False)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.nom}"

class Prix(models.Model):
	id = models.SmallAutoField(primary_key=True)
	prix = models.FloatField(default=500)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.prix}"

class Oeuf(models.Model):
	id = models.SmallAutoField(primary_key=True)
	salle = models.ForeignKey(Salle, on_delete=models.PROTECT)
	# prix = models.ForeignKey(Prix, on_delete=models.PROTECT)
	commentaire = models.CharField(max_length=200)
	quantite = models.FloatField(default=0)
	quantite_total = models.FloatField(default=0, editable=False)
	date = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return f"{self.salle.nom} {self.quantite}"

class Produit(models.Model):
	id = models.SmallAutoField(primary_key=True) 
	nom = models.CharField(max_length=200)
	quantite = models.FloatField(default = 0)
	unite = models.CharField(max_length=64, verbose_name='unité de mesure')
	prix_unitaire = models.FloatField(default=0)
	prix_total = models.FloatField(default=0, editable=False)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.nom}"

	def save(self, *args, **kwargs):
		if self.quantite<0:
			raise Exception("Produit.quantite cannot be negative number")
		super().save(*args, **kwargs)

	class Meta:
		ordering = "nom",


class Achat(models.Model):
	id = models.BigAutoField(primary_key=True)
	produit = models.ForeignKey("Produit", on_delete=models.PROTECT)
	quantite = models.FloatField()
	date = models.DateTimeField(blank=True, default=timezone.now)
	user = models.ForeignKey(User, default=1, on_delete=models.PROTECT)
	details = models.TextField(blank=True, null=True)
	prix_total = models.FloatField()
	prix_unitaire = models.FloatField()

	def __str__(self):
		return f"{self.produit.nom} par {self.user.username}"

	def save(self, *args, **kwargs):
		if self.quantite<0:
			raise Exception("Achat.quantite cannot be negative number")
		super().save(*args, **kwargs)

	class Meta:
		ordering = ["-date"]

class Ration(models.Model):
	id = models.BigAutoField(primary_key=True)
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	responsable = models.ForeignKey(Responsable, blank=True, null=True, on_delete=models.SET_NULL)
	quantite = models.FloatField(default=0)
	date = models.DateTimeField(blank=True, default=timezone.now)
	a_payer = models.FloatField(default=0, editable=False)
	payee = models.FloatField(default=0., editable=False)
	reste = models.FloatField(default=0., editable=False)
	uncommited = models.FloatField(default=0, editable=False)
	date = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return f"ration valant {self.a_payer}"

	def save(self, *args, **kwargs):
		if self.payee > self.a_payer:
			raise Exception("Ration.payee cannot be greater than Ration.a_payer")
		super().save(*args, **kwargs)

	class Meta:
		ordering = "-pk",



class Vente(models.Model):
	id = models.BigAutoField(primary_key=True)
	produit = models.ForeignKey("Produit", on_delete=models.PROTECT)
	quantite = models.FloatField()
	commande = models.ForeignKey("Ration", on_delete=models.PROTECT)
	details = models.TextField(blank=True, null=True)
	prix_achat = models.FloatField(editable=False, null=True)
	prix_vente = models.FloatField(editable=False, default=0)

	def save(self, *args, **kwargs):
		if self.quantite<=0:
			raise Exception("Vente.quantite cannot be negative number")
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.quantite} {self.produit} {self.commande.date}"



class PoulleVendu(models.Model):
	id = models.SmallAutoField(primary_key=True)
	salle = models.ForeignKey(Salle, on_delete=models.PROTECT)
	client = models.ForeignKey(Client, on_delete=models.PROTECT)
	commentaire = models.CharField(max_length=200)
	quantite = models.FloatField(default=0)
	prix_total = models.FloatField(default=0, editable=False)
	date = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return f"{self.salle.nom} {self.quantite}"


	def save(self, *args, **kwargs):
		self.prix_total = self.quantite*self.prix_unitaire
		self.salle.quantite -= self.quantite
		super(PoulleVendu, self).save(*args, **kwargs)
		# super(Salle, self).save(*args, **kwargs)


class PoulleMorte(models.Model):
	id = models.SmallAutoField(primary_key=True)
	salle = models.ForeignKey(Salle, on_delete=models.PROTECT)
	client = models.ForeignKey(Client, on_delete=models.PROTECT)
	commentaire = models.CharField(max_length=200)
	quantite = models.FloatField(default=0)
	prix_unitaire = models.FloatField(default=0)
	prix_total = models.FloatField(default=0, editable=False)
	date = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return f"{self.salle.nom} {self.quantite}"

class Commande(models.Model):
	id = models.SmallAutoField(primary_key=True)
	client = models.ForeignKey(Client, on_delete=models.PROTECT)
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	salle=models.ForeignKey(Salle, on_delete= models.PROTECT)
	prix=models.ForeignKey(Prix, on_delete= models.PROTECT)
	quantite = models.FloatField(default = 0, null=True)
	date = models.DateTimeField(auto_now_add=True)


class Perte(models.Model):
	id  = models.SmallAutoField(primary_key=True)
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	salle = models.ForeignKey(Salle, on_delete=models.PROTECT)
	commentaire = models.CharField(max_length=300)
	quantite = models.FloatField(default=0)
	prix_unitaire = models.FloatField(default=0)
	prix_vente = models.FloatField(editable=False, default=0)
	validated = models.BooleanField(default=False)
	date = models.DateTimeField(blank=True, default=timezone.now)

	def __str__(self):
		return f"{self.date}"


class Transfer(models.Model):
	id = models.SmallAutoField(primary_key=True)
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	nom = models.CharField(max_length=200)
	prenom = models.CharField(max_length=200)
	adresse = models.CharField(max_length=200)
	telephone = models.CharField(max_length=200)
	montant = models.FloatField(default=0)
	validated = models.BooleanField(default=False)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.nom} {self.prenom}"

	class Meta:
		ordering='-pk',