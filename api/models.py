from django.db import models


type_poulet=(
	('poulet en chair', 'poulet en chair'),
	('poulet pondeuse', 'poulet pondeuse'),
	)

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

class Salle(models.Model):
	id = models.SmallAutoField(primary_key=True)
	responsable = models.ForeignKey(Responsable, on_delete=models.CASCADE)
	nom = models.CharField(max_length=200, null=False, blank=False, unique=True)
	type_poulle = models.CharField(max_length= 200, choices=type_poulet)
	quantite = models.IntegerField(default=0)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.nom}"

class Produit(models.Model):
	id = models.SmallAutoField(primary_key=True)
	designation = models.CharField(max_length=200)
	quantite = models.IntegerField(default = 0)
	prix_unitaire = models.IntegerField(default=0)
	prix_total = models.IntegerField(default=0, editable=False)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.designation}"

	def save(self, *args, **kwargs):
		self.prix_total = self.quantite*self.prix_unitaire
		super(Produit, self).save(*args, **kwargs)

# class Approvision(models.Model):
# 	pass

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
	prix_unitaire = models.IntegerField(default=0)
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

class Oeuf(models.Model):
	id = models.SmallAutoField(primary_key=True)
	salle = models.ForeignKey(Salle, on_delete=models.CASCADE)
	commentaire = models.CharField(max_length=200)
	quantite = models.IntegerField(default=0)
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
	quantite = models.IntegerField(default=0)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.date}"



