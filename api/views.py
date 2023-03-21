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
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Salle.objects.all()
	serializer_class = SalleSerializer


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
		data = self.request.data
		responsable: Responsable = Responsable.objects.get(telephone=(data.get('responsable')))
		nom = (data.get('nom'))
		type_poulle = (data.get('type_poulle'))
		quantite = (data.get('quantite'))
		salle = Salle(
			# user=request.user,
			nom=nom,
			responsable=responsable,
			type_poulle=type_poulle,
			quantite=quantite
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
	queryset = Produit.objects.all().order_by("designation")
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


class RationViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Ration.objects.all()
	serializer_class = RationSerializer

class PoulleVenduViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = PoulleVendu.objects.all()
	serializer_class = PoulleVenduSerializer

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

		serializer = self.serializer_class(salle, many=False)
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

class OeufVenduViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = OeufVendu.objects.all()
	serializer_class = OeufVenduSerializer

class PerteViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Perte.objects.all()
	serializer_class = PerteSerializer

class TransferViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Transfer.objects.all()
	serializer_class = TransferSerializer


	@transaction.atomic
	def create(self, request):
		data = self.request.data
		nom = (data.get('nom'))
		prenom = (data.get('prenom'))
		adresse = (data.get('adresse'))
		montant = (data.get('montant'))
		telephone = (data.get('telephone'))
		transaction = Transfer(
			user=self.request.user,
			nom=nom,
			prenom=prenom,
			adresse=adresse,
			montant=montant,
			telephone=telephone,
			)
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