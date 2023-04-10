from .dependencies import *


class Pagination(PageNumberPagination):
	page_size = 10
	def get_paginated_response(self, data):
		return Response(OrderedDict([
			('next', self.get_next_link()),
			('previous', self.get_previous_link()),
			('count', self.page.paginator.count),
			('page', self.page.number),
			('num_page', self.page.paginator.num_pages),
			('results', data)
		]))
class LastLoginViewset(mixins.ListModelMixin,
					viewsets.GenericViewSet):
	queryset = LastLogin.objects.all()
	def list(self, request, *args, **kwargs):
		logins = LastLogin.objects.all()
		if(logins):
			last_login = logins.first()
		else:
			last_login = LastLogin()
			last_login.save()
		serializer = LastLoginSerializer(last_login, many=False)
		return Response(serializer.data, 204)

class TokenPairView(TokenObtainPairView):
	serializer_class = TokenPairSerializer


class GroupViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Group.objects.all()
	serializer_class = GroupSerializer



class UserViewSet(viewsets.ModelViewSet):
	authentication_classes = (JWTAuthentication, SessionAuthentication)
	permission_classes = [IsAuthenticated,]
	queryset = User.objects.all()
	serializer_class = UserSerializer

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = request.data
		user = User(
			username = data.get("username"),
			first_name = data.get("first_name"),
			last_name = data.get("last_name"),
		)
		user.set_password("password")
		user.save()
		serializer = UserSerializer(user, many=False)
		return Response(serializer.data, 201)

	@transaction.atomic
	def update(self, request, *args, **kwargs):
		data = request.data
		user = self.get_object()
		if not request.user.is_superuser:
			if(user.id != request.user.id):
				return Response(
					{'status': "permissions non accordée"}
				, 400)

		username = data.get("username")
		if username:user.username = username

		last_name = data.get("last_name")
		if last_name : user.last_name = last_name

		first_name = data.get("first_name")
		if first_name : user.first_name = first_name

		password = data.get("password")
		if password : user.set_password(password)

		is_active = data.get("is_active")
		if is_active!=None : user.is_active = is_active

		group = data.get("group")
		if group:
			user.groups.clear()
			user.is_superuser = False
			if group == "admin":
				user.is_superuser = True
			else:
				try:
					group = Group.objects.get(name=group)
					user.groups.add(group)
				except:
					return Response({"status":"groupe invalide"}, 400)

		user.save()
		serializer = UserSerializer(user, many=False)
		return Response(serializer.data, 200)

	def patch(self, request, *args, **kwargs):
		return self.update(request, *args, **kwargs)

	@transaction.atomic
	def destroy(self, request, *args, **kwargs):
		user = self.get_object()
		user.is_active = False
		user.save()
		return Response({'status': 'success'}, 204)


class ClientViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Client.objects.all()
	serializer_class = ClientSerializer


class ResponsableViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Responsable.objects.all()
	serializer_class = ResponsableSerializer



class SalleViewSet(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated,]
	permission_classes = IsAuthenticated,
	queryset = Salle.objects.all()
	serializer_class = SalleSerializer
	# filter_backends = (filters.SearchFilter,)
	# search_fields = ('nom',)

	# def get_queryset(self):
	# 	return Salle.objects.filter(user = self.request.user)

	@transaction.atomic
	def create(self, request):
		data = request.data
		prix:PouletPrix=PouletPrix.objects.all().latest('id')
		dict_responsable = data.get("responsable")
		responsable = None
		if(dict_responsable.get("telephone")):
			responsable, created = Responsable.objects.get_or_create(
				telephone = dict_responsable.get("telephone")
			)
			if(not responsable.nom):
				responsable.nom = dict_responsable.get("nom")
				responsable.save()
		nom = (data.get('nom'))
		type_poulle = (data.get('type_poulle'))
		quantite = (data.get('quantite'))
		salle = Salle(
			# user=request.user,
			nom=nom,
			responsable=responsable,
			type_poulle=type_poulle,
			quantite=quantite,
			prix=prix
			)
		salle.save()
		serializer = SalleSerializer(salle, many=False, context={"request":request}).data
		return Response(serializer,200)



class ProduitViewSet(mixins.ListModelMixin,
					mixins.UpdateModelMixin,
					mixins.RetrieveModelMixin,
					mixins.CreateModelMixin,
					viewsets.GenericViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated]
	queryset = Produit.objects.all().order_by("nom")
	serializer_class = ProduitSerializer

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		many = True if isinstance(request.data, list) else False
		serializer = self.get_serializer(data=request.data, many=many)
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, 201)



class AchatViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated]
	queryset = Achat.objects.select_related('produit').all()
	serializer_class = AchatSerializer
	filter_backends = filters.DjangoFilterBackend,
	filterset_fields = {
		'date': ['gte', 'lte'],
	}

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = request.data

		produit:Produit = Produit.objects.get(id=data.get("produit"))
		prix_total = float(data.get("prix_total"))
		quantite = float(data.get("quantite"))
		prix_unitaire=prix_total/quantite

		achat = Achat(
			quantite=quantite, details=data.get("details"),
			prix_total=prix_total, produit=produit,
			prix_unitaire=prix_unitaire, user = request.user
		)

		# produit_old_pa = produit.quantite*(produit.prix_achat or 0)
		produit.quantite += float(achat.quantite)
		# produit_new_pa = (produit_old_pa+prix_total)/produit.quantite
		# produit.prix_achat = produit_new_pa

		produit.save();
		achat.save()

		serializer = self.serializer_class(achat, many=False)
		return Response(serializer.data, 201)

	@transaction.atomic
	def update(self, request, *args, **kwargs):
		achat:Achat = self.get_object()
		produit:Produit = achat.produit
		data = request.data
		prix_achat = float(data.get("prix_total"))
		quantite = float(data.get("quantite"))
		prix_unitaire = prix_achat/quantite
		if prix_achat :
			achat.prix_total = prix_achat
			achat.prix_unitaire = prix_unitaire
			produit.prix_achat = prix_unitaire
		if quantite :
			produit.quantite -= achat.quantite
			produit.quantite += quantite
			achat.quantite = quantite
		achat.save()
		produit.save()
		serializer = AchatSerializer(achat, many=False)
		return Response(serializer.data, 201)

	def patch(self, request, *args, **kwargs):
		return self.update(request, *args, **kwargs)

	@transaction.atomic
	def destroy(self, request, *args, **kwargs):
		achat = self.get_object()
		produit = achat.produit
		produit.quantite += achat.quantite
		produit.save()
		achat.delete()
		return Response(None, 204)

	@action(methods=['GET'], detail=False, url_name=r'achatsfilter',
		url_path=r"achatsfilter/(?P<since>\d{4}-\d{2}-\d{2})/(?P<to>\d{4}-\d{2}-\d{2})")
	def achatsFilterDate(self, request, since, to):
		since = datetime.strptime(since, "%Y-%m-%d").date()
		to = datetime.strptime(to, "%Y-%m-%d").date()+timedelta(days=1)
		query = []
		with connection.cursor() as cursor:
			cursor.execute(f"""
				SELECT
					* 
				FROM 
					api_achat 
				WHERE
					date between "{since}" AND "{to}" 
			""")
			columns = [col[0] for col in cursor.description]
			query = [
				dict(zip(columns, row))
				for row in cursor.fetchall()
			]
		return Response(query)



class RationViewSet(mixins.RetrieveModelMixin,
					  mixins.ListModelMixin,
					  mixins.CreateModelMixin,
					  viewsets.GenericViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated]
	queryset = Ration.objects.select_related("responsable").all()
	serializer_class = RationSerializer

	def list(self, request, *args, **kwargs):
		str_du = request.query_params.get('du')
		str_au = request.query_params.get('au')
		if bool(str_du) & bool(str_au):
			du = datetime.strptime(str_du, "%Y-%m-%d").date()
			au = datetime.strptime(str_au, "%Y-%m-%d").date()+timedelta(days=1)
		else:
			du = date.today()-timedelta(days=7)
			au = date.today()+timedelta(days=1)
		self.queryset = self.queryset.filter(
			date__gte=du, date__lte=au
		)
		return super().list(request, *args, **kwargs)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		data = request.data
		dict_responsable = data.get("responsable")
		responsable = None
		if(dict_responsable.get("telephone")):
			responsable, created = Responsable.objects.get_or_create(
				telephone = dict_responsable.get("telephone")
			)
			if(not responsable.nom):
				responsable.nom = dict_responsable.get("nom")
				responsable.save()
		str_payee = data.get("payee")
		a_payer = int(data.get("a_payer"))
		payee = int(str_payee) if str_payee else 0
		commande = Ration(
			user=request.user, a_payer=a_payer, responsable=responsable,
			payee=payee, reste=a_payer-payee
		)
		commande.save()
		for item in data.get("items"):
			produit:Produit = Produit.objects.get(id=item.get("id"))
			quantite = float(item.get("quantite"))
			vente = Vente(
				produit=produit, commande=commande, quantite=quantite,
				prix_vente=produit.prix_total, prix_achat=produit.prix_unitaire, 
			)
			vente.save()
			produit.quantite-=quantite
			produit.save();
		# if payee:
		# 	Paiement.objects.create(commande=commande, somme=payee, validated=True)
		serializer = self.serializer_class(commande, many=False)
		return Response(serializer.data, 201)

	@action(methods=['GET'], detail=False, url_name=r'dettes',
		url_path=r"dettes/(?P<since>\d{4}-\d{2}-\d{2})/(?P<to>\d{4}-\d{2}-\d{2})")
	def dettes(self, request, since, to):
		since = datetime.strptime(since, "%Y-%m-%d").date()
		to = datetime.strptime(to, "%Y-%m-%d").date()+timedelta(days=1)
		queryset = self.queryset.filter(
			date__gte=since, date__lte=to, reste__gt=0
		)
		serializer = self.serializer_class(queryset, many=True)
		return Response(serializer.data)

	@action(methods=['GET'], detail=False, url_path=r"dettes",
		url_name=r'today_dettes')
	def weekDettes(self, request):
		last_today = datetime.today()-timedelta(days=7)
		last_today_str = last_today.strftime("%Y-%m-%d")
		today = datetime.today().strftime("%Y-%m-%d")
		print(today)
		return self.dettes(request, last_today_str, today)
		

class VenteViewSet(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated]
	queryset = Vente.objects.select_related("produit", "commande").all()
	serializer_class = VenteSerializer
	filter_backends = filters.DjangoFilterBackend, SearchFilter
	search_fields = "produit__nom",
	filterset_fields = {
		'prix_achat': ['gte', 'lte', 'isnull'],
		'prix_vente': ['gte', 'lte'],
		'commande__date': ['gte', 'lte'],
		'commande': ['exact'],
	}

	# def list(self, request, *args, **kwargs):
	# 	commande_id = request.query_params.get('commande')
	# 	if(commande_id):
	# 		self.queryset = self.queryset.filter(commande__id=commande_id)
	# 	return super(VenteViewset, self).list(request, *args, **kwargs)

	@transaction.atomic
	def update(self, request, *args, **kwargs):
		vente:Vente = self.get_object()
		produit:Produit = vente.produit
		commande:Commande = vente.commande
		data = request.data
		quantite = float(data.get("quantite"))

		if quantite:
			produit.quantite += vente.quantite
			produit.quantite -= quantite
			commande.a_payer -= vente.prix_vente*vente.quantite
			commande.a_payer += vente.prix_vente*quantite
			vente.quantite = quantite

		vente.save()
		produit.save()
		commande.save()
		serializer = VenteSerializer(vente, many=False)
		return Response(serializer.data, 201)

	def patch(self, request, *args, **kwargs):
		return self.update(request, *args, **kwargs)

	@transaction.atomic
	def destroy(self, request, *args, **kwargs):
		vente = self.get_object()
		produit = vente.produit
		commande = vente.commande

		produit.quantite += vente.quantite
		commande.a_payer -= vente.prix_vente
		produit.save()
		commande.save()
		vente.delete()
		return Response(None, 204)
			

class TauxViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Taux.objects.all()
	serializer_class = TauxSerializer			

class PoulleVenduViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = PoulleVendu.objects.all()
	serializer_class = PoulleVenduSerializer

	@transaction.atomic()
	def create(self, request, *args, **kwargs):
		data = request.data
		dict_client = data.get("client")
		client = None
		if(dict_client.get("tel")):
			client, created = Client.objects.get_or_create(
				tel = dict_client.get("tel")
			)
			if(not client.nom):
				client.nom = dict_client.get("nom")
				client.save()
		salle:Salle=Salle.objects.get(id=data.get("salle"))
		# client:Client=Client.objects.get(id=data.get("client"))
		quantite = float(data.get("quantite"))
		poids = (data.get("poids"))
		prix_unitaire = float(data.get("prix_unitaire"))
		commentaire = (data.get("commentaire"))
		pouletvendu = PoulleVendu(
			quantite=quantite, 
			client=client, 
			salle=salle, 
			prix_unitaire=prix_unitaire, 
			poids=poids, 
			commentaire=commentaire
		)
		salle.quantite-=float(pouletvendu.quantite)
		pouletvendu.prix_total+=pouletvendu.prix_unitaire*pouletvendu.quantite
		salle.save()
		pouletvendu.save()
		serializer = self.serializer_class(pouletvendu, many=False)
		return Response(serializer.data, 201)

class PrixpouletViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = PouletPrix.objects.all()
	serializer_class = PouletPrixSerializer

class PoulleMorteViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = PoulleMorte.objects.all()
	serializer_class = PoulleMorteSerializer

class PrixViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Prix.objects.all()
	serializer_class = PrixSerializer

class OeufViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Oeuf.objects.all()
	serializer_class = OeufSerializer

	
	def list(self, request, *args, **kwargs):
		str_du = request.query_params.get('du')
		str_au = request.query_params.get('au')
		if bool(str_du) & bool(str_au):
			du = datetime.strptime(str_du, "%Y-%m-%d").date()
			au = datetime.strptime(str_au, "%Y-%m-%d").date()+timedelta(days=1)
		else:
			du = date.today()-timedelta(days=7)
			au = date.today()+timedelta(days=1)
		self.queryset = self.queryset.filter(
			date__gte=du, date__lte=au
		)
		return super().list(request, *args, **kwargs)


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = request.data
		salle:Salle = Salle.objects.get(id=data.get("salle"))
		quantite = float(data.get("quantite"))

		oeuf = Oeuf(
			quantite=quantite, commentaire=data.get("commentaire"),
			salle=salle,
		)
		oeuf.save()
		salle.quantite_oeuf += float(oeuf.quantite)
		salle.save();

		serializer = self.serializer_class(oeuf, many=False)
		return Response(serializer.data, 201)

	@transaction.atomic
	def update(self, request, *args, **kwargs):
		achat:Achat = self.get_object()
		produit:Produit = achat.produit
		data = request.data
		prix_achat = float(data.get("prix_total"))
		quantite = float(data.get("quantite"))
		prix_unitaire = prix_achat/quantite
		if prix_achat :
			achat.prix_total = prix_achat
			achat.prix_unitaire = prix_unitaire
			produit.prix_achat = prix_unitaire
		if quantite :
			produit.quantite -= achat.quantite
			produit.quantite += quantite
			achat.quantite = quantite
		achat.save()
		produit.save()
		serializer = AchatSerializer(achat, many=False)
		return Response(serializer.data, 201)

	def patch(self, request, *args, **kwargs):
		return self.update(request, *args, **kwargs)

 
	@action(methods=['GET'], detail=False, url_name=r'achatsfilter',
		url_path=r"achatsfilter/(?P<since>\d{4}-\d{2}-\d{2})/(?P<to>\d{4}-\d{2}-\d{2})")
	def achatsFilterDate(self, request, since, to):
		since = datetime.strptime(since, "%Y-%m-%d").date()
		to = datetime.strptime(to, "%Y-%m-%d").date()+timedelta(days=1)
		query = []
		with connection.cursor() as cursor:
			cursor.execute(f"""
				SELECT
					* 
				FROM 
					api_achat 
				WHERE
					date between "{since}" AND "{to}" 
			""")
			columns = [col[0] for col in cursor.description]
			query = [
				dict(zip(columns, row))
				for row in cursor.fetchall()
			]
		return Response(query)

class OeufVenduViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Commande.objects.all()
	serializer_class = OeufVenduSerializer


	def list(self, request, *args, **kwargs):
		str_du = request.query_params.get('du')
		str_au = request.query_params.get('au')
		if bool(str_du) & bool(str_au):
			du = datetime.strptime(str_du, "%Y-%m-%d").date()
			au = datetime.strptime(str_au, "%Y-%m-%d").date()+timedelta(days=1)
		else:
			du = date.today()-timedelta(days=7)
			au = date.today()+timedelta(days=1)
		self.queryset = self.queryset.filter(
			date__gte=du, date__lte=au
		)
		return super().list(request, *args, **kwargs)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		data = request.data
		salle:Salle = Salle.objects.all().latest('id')
		prix:Prix = Prix.objects.all().latest('id')
		dict_client = data.get("client")
		client = None
		if(dict_client.get("tel")):
			client, created = Client.objects.get_or_create(
				tel = dict_client.get("tel")
			)
			if(not client.nom):
				client.nom = dict_client.get("nom")
				client.save()
		quantite = (data.get("quantite"))
		oeufvendu = Commande(
			user=request.user, quantite=quantite, client=client, salle=salle, prix=prix
		)
		salle.quantite_oeuf-=float(oeufvendu.quantite)
		salle.save()
		oeufvendu.save()
		serializer = self.serializer_class(oeufvendu, many=False)
		return Response(serializer.data, 201)

class PerteViewSet(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated]
	queryset = Perte.objects.all()
	serializer_class = PerteSerializer

	def list(self, request, *args, **kwargs):
		str_du = request.query_params.get('du')
		str_au = request.query_params.get('au')
		if bool(str_du) & bool(str_au):
			du = datetime.strptime(str_du, "%Y-%m-%d").date()
			au = datetime.strptime(str_au, "%Y-%m-%d").date()
		else:
			du = date.today()-timedelta(days=7)
			au = date.today()+timedelta(days=1)
		self.queryset = self.queryset.filter(
			date__gte=du, date__lte=au
		)
		return super().list(request, *args, **kwargs)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = request.data
		salle = Salle.objects.get(id=data.get("salle"))
		quantite = float(data.get("quantite"))
		prix_unitaire = float(data.get("prix_unitaire"))
		perte = Perte(
			user =request.user, salle=salle, quantite=quantite,prix_unitaire=prix_unitaire,
			commentaire=data.get("commentaire")
		)
		perte.prix_vente+=float(salle.prix.prix)*perte.quantite
		salle.quantite -= perte.quantite
		perte.save()
		salle.save()
		serializer = PerteSerializer(perte, many=False)
		return Response(serializer.data, 201)

	def patch(self, request, *args, **kwargs):
		return self.update(request, *args, **kwargs)

	@transaction.atomic
	def destroy(self, request, *args, **kwargs):
		perte = self.get_object()
		if perte.validated:
			return Response({'status': "the validated one cannot be deleted"}, 400)

		perte.salle.quantite += perte.quantite
		perte.salle.save()
		perte.delete()
		serializer = PerteSerializer(perte, many=False)
		return Response(serializer.data, 201)

	@action(methods=['GET'], detail=False, url_name=r'perte_stats',url_path=r"stats")
	def stats_today(self, request):
		last_today =(datetime.today()-timedelta(days=30)).strftime("%Y-%m-%d")
		today = date.today().strftime("%Y-%m-%d")
		return self.stats_date(request, last_today, today)

	@action(methods=['GET'], detail=False, url_name=r'perte_stats_date',
		url_path=r"stats/(?P<du>\d{4}-\d{2}-\d{2})/(?P<au>\d{4}-\d{2}-\d{2})")
	def stats_date(self, request, du, au):
		du = datetime.strptime(du, "%Y-%m-%d").date()
		au = datetime.strptime(au, "%Y-%m-%d").date()+timedelta(days=1)
		query = []

		with connection.cursor() as cursor:
			cursor.execute(f"""
				SELECT
					P.id, P.nom as salle, SUM(Perte.quantite) as quantite,
					SUM(Perte.quantite*Perte.prix_unitaire) AS total
				FROM 
					api_salle as P, api_perte AS Perte
				WHERE
					Perte.date between "{du}" AND "{au}" AND
					P.id = Perte.salle_id AND Perte.validated=1
				GROUP BY P.id;
			""")
			columns = [col[0] for col in cursor.description]
			query = [
				dict(zip(columns, row))
				for row in cursor.fetchall()
			]
		return Response(query)


class TransferViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Transfer.objects.all()
	serializer_class = TransferSerializer

	def list(self, request, *args, **kwargs):
		str_du = request.query_params.get('du')
		str_au = request.query_params.get('au')
		if bool(str_du) & bool(str_au):
			du = datetime.strptime(str_du, "%Y-%m-%d").date()
			au = datetime.strptime(str_au, "%Y-%m-%d").date()+timedelta(days=1)
		else:
			du = date.today()-timedelta(days=7)
			au = date.today()+timedelta(days=1)
		self.queryset = self.queryset.filter(
			date__gte=du, date__lte=au
		)
		return super().list(request, *args, **kwargs)

	@transaction.atomic
	def create(self, request):
		data = self.request.data
		taux = Taux.objects.all().latest('id')
		nom = (data.get('nom'))
		prenom = (data.get('prenom'))
		adresse = (data.get('adresse'))
		montant_euro = float(data.get('montant_euro'))
		telephone = (data.get('telephone'))
		frais = float(data.get('frais'))
		transaction = Transfer(
			user=self.request.user,
			taux=taux,
			nom=nom,
			prenom=prenom,
			adresse=adresse,
			montant_euro=montant_euro,
			telephone=telephone,
			frais=frais,
			)
		transaction.montant_fbu+=(transaction.montant_euro*transaction.taux.taux)*transaction.frais/100
		transaction.save()
		serializer = TransferSerializer(transaction, many=False, context={"request":request}).data
		return Response(serializer,200)
	
	def patch(self, request, *args, **kwargs):
		return self.update(request, *args, **kwargs)

	@transaction.atomic
	def destroy(self, request, *args, **kwargs):
		transaction = self.get_object()
		transaction.delete()
		return Response(None, 204)

	@action(methods=["GET"], detail=True, url_path=r'valider', url_name=r'valider')
	@transaction.atomic()
	def valider(self, request, pk):
		user=request.user
		transaction: Transfer = Transfer.objects.get(id=pk)
		transaction.validated = True
		print(transaction)
		transaction.save()
		return Response({"status": "transaction validée avec success"}, 201)

# stats
class StatsViewSet(viewsets.ViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]

	@action(methods=['GET'], detail=False, url_name=r'products',
		url_path=r"products")
	def weekSolded(self, request):
		last_today =(datetime.today()-timedelta(days=7)).strftime("%Y-%m-%d")
		today = date.today().strftime("%Y-%m-%d")
		return self.solded(request, last_today, today)

	@action(methods=['GET'], detail=False, url_name=r'clients',
		url_path=r"clients/(?P<du>\d{4}-\d{2}-\d{2})/(?P<au>\d{4}-\d{2}-\d{2})")
	def client(self, request, du, au):
		du = datetime.strptime(du, "%Y-%m-%d").date()
		au = datetime.strptime(au, "%Y-%m-%d").date()+timedelta(days=1)
		query = []
		with connection.cursor() as cursor:
			cursor.execute(f"""
				SELECT
					C.id, C.nom, C.tel, COUNT (COM.id) AS commande ,
					SUM(COM.prix*COM.quantite) AS total 
				FROM 
					api_client as C, api_commande AS COM
				WHERE
					date between "{du}" AND "{au}" AND
					C.id = COM.client_id
				GROUP BY C.id;
			""")
			columns = [col[0] for col in cursor.description]
			query = [
				dict(zip(columns, row))
				for row in cursor.fetchall()
			]
		return Response(query)

	@action(methods=['GET'], detail=False, url_name=r'clients',
		url_path=r"clients")
	def weekClient(self, request):
		last_today =(datetime.today()-timedelta(days=7)).strftime("%Y-%m-%d")
		today = date.today().strftime("%Y-%m-%d")
		return self.client(request, last_today, today)

	@action(methods=['GET'], detail=False, url_name=r'clients_dettes',
		url_path=r"clients_dettes/(?P<du>\d{4}-\d{2}-\d{2})/(?P<au>\d{4}-\d{2}-\d{2})")
	def clientsDettes(self, request, du, au):
		du = datetime.strptime(du, "%Y-%m-%d").date()
		au = datetime.strptime(au, "%Y-%m-%d").date()+timedelta(days=1)
		query = []

		with connection.cursor() as cursor:
			cursor.execute(f"""
				SELECT
					C.id, C.nom, C.tel, SUM (COM.reste) AS tot_dete 
				FROM 
					api_client as C, api_oeufVendu AS COM
				WHERE
					date between "{du}" AND "{au}" AND
					C.id = COM.client_id AND
					COM.payee < COM.a_payer
				GROUP BY C.id;
			""")
			columns = [col[0] for col in cursor.description]
			query = [
				dict(zip(columns, row))
				for row in cursor.fetchall()
			]
		return Response(query)

	@action(methods=['GET'], detail=False, url_name=r'clients_dettes',
		url_path=r"clients_dettes")
	def weekClientsDettes(self, request):
		last_today =(datetime.today()-timedelta(days=7)).strftime("%Y-%m-%d")
		today = date.today().strftime("%Y-%m-%d")
		return self.clientsDettes(request, last_today, today)
