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
	date = models.DateTimeField(default=timezone.now, editable=False)


class Client(models.Model):
	id = models.SmallAutoField(primary_key=True)
	nom = models.CharField(max_length=100)
	prenom = models.CharField(max_length=100)
	addresse = models.CharField(max_length=100)
	telephone = models.CharField(max_length=100)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.nom} {self.prenom}"

class Responsable(models.Model):
	id = models.SmallAutoField(primary_key=True)
	nom = models.CharField(max_length=100)
	prenom = models.CharField(max_length=100)
	addresse = models.CharField(max_length=100)
	telephone = models.CharField(max_length=100)
	date = models.DateTimeField(auto_now_add=True)



	def __str__(self):
		return f"{self.nom} {self.prenom}"


class PouletPrix(models.Model):
	id = models.SmallAutoField(primary_key=True)
	prix = models.IntegerField(default=30000)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.prix}"


class Salle(models.Model):
	id = models.SmallAutoField(primary_key=True)
	responsable = models.ForeignKey(Responsable, on_delete=models.CASCADE)
	prix = models.ForeignKey(PouletPrix, on_delete=models.CASCADE)
	nom = models.CharField(max_length=200, null=False, blank=False, unique=True)
	type_poulle = models.CharField(max_length= 200, choices=type_poulet)
	quantite = models.IntegerField(default=0)
	# quantite = models.IntegerField(default=0)
	quantite_oeuf = models.IntegerField(default=0, editable=False)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.nom}"

class Prix(models.Model):
	id = models.SmallAutoField(primary_key=True)
	prix = models.IntegerField(default=500)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.prix}"

class Oeuf(models.Model):
	id = models.SmallAutoField(primary_key=True)
	salle = models.ForeignKey(Salle, on_delete=models.CASCADE)
	prix = models.ForeignKey(Prix, on_delete=models.CASCADE)
	commentaire = models.CharField(max_length=200)
	quantite = models.IntegerField(default=0)
	quantite_total = models.IntegerField(default=0, editable=False)
	date = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return f"{self.salle.nom} {self.quantite}"


	def save(self, *args, **kwargs):
		self.quantite_total += self.quantite
		super(Oeuf, self).save(*args, **kwargs)
		# super(Salle, self).save(*args, **kwargs)


class Produit(models.Model):
	id = models.SmallAutoField(primary_key=True) 
	designation = models.CharField(max_length=200)
	quantite = models.IntegerField(default = 0)
	unite = models.CharField(max_length=64, verbose_name='unité de mesure')
	prix_unitaire = models.IntegerField(default=0)
	prix_total = models.IntegerField(default=0, editable=False)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.designation}"

	def save(self, *args, **kwargs):
		if self.quantite<0:
			raise Exception("Produit.quantite cannot be negative number")
		super().save(*args, **kwargs)

	class Meta:
		ordering = "designation",


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
		ordering = ["produit"]

class Ration(models.Model):
	id = models.SmallAutoField(primary_key=True)
	salle = models.ForeignKey(Salle, on_delete=models.CASCADE)
	produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
	commentaire = models.CharField(max_length=200)
	quantite = models.IntegerField(default=0)
	date = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return f"{self.salle.nom} {self.quantite}"


class PoulleVendu(models.Model):
	id = models.SmallAutoField(primary_key=True)
	salle = models.ForeignKey(Salle, on_delete=models.CASCADE)
	client = models.ForeignKey(Client, on_delete=models.CASCADE)
	commentaire = models.CharField(max_length=200)
	quantite = models.IntegerField(default=0)
	prix_total = models.IntegerField(default=0, editable=False)
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
	salle = models.ForeignKey(Salle, on_delete=models.CASCADE)
	client = models.ForeignKey(Client, on_delete=models.CASCADE)
	commentaire = models.CharField(max_length=200)
	quantite = models.IntegerField(default=0)
	prix_unitaire = models.IntegerField(default=0)
	prix_total = models.IntegerField(default=0, editable=False)
	date = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return f"{self.salle.nom} {self.quantite}"

class OeufVendu(models.Model):
	id = models.SmallAutoField(primary_key=True)
	client = models.ForeignKey(Client, on_delete=models.CASCADE)
	quantite = models.IntegerField(default = 0)
	prix_unitaire  = models.IntegerField(default=0)
	prix_total = models.IntegerField(default=0, editable=False)
	date = models.DateTimeField(auto_now_add=True)


class Perte(models.Model):
	id  = models.SmallAutoField(primary_key=True)
	oeuf = models.ForeignKey(Oeuf, on_delete=models.CASCADE)
	commentaire = models.CharField(max_length=300)
	quantite = models.IntegerField(default=0)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.date}"


class Transfer(models.Model):
	id = models.SmallAutoField(primary_key=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	nom = models.CharField(max_length=200)
	prenom = models.CharField(max_length=200)
	adresse = models.CharField(max_length=200)
	telephone = models.CharField(max_length=200)
	montant = models.IntegerField(default=0)
	validated = models.BooleanField(default=False)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.nom} {self.prenom}"


