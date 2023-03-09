from django.urls import path, include
from rest_framework import routers
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

router = routers.DefaultRouter()
router.register("user",UserViewSet)
router.register("groups",GroupViewSet)
router.register("client",ClientViewSet)
router.register("responsable",ResponsableViewSet)
router.register("salle",SalleViewSet)
router.register("produit",ProduitViewSet)
router.register("poulle_vendu",PoulleVenduViewSet)
router.register("poulle_morte",PoulleMorteViewSet)
router.register("oeuf",OeufViewSet)
router.register("oeuf_vendu",OeufVenduViewSet)
router.register("perte",PerteViewSet)
router.register("ration",RationViewSet)

urlpatterns = [
	path('', include(router.urls)),
	path('login/', TokenPairView.as_view()),
	path('refresh/', TokenRefreshView.as_view()),
	path('api_auth', include('rest_framework.urls'))

]
