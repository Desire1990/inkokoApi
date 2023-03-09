from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(Client)
admin.site.register(Responsable)
admin.site.register(Salle)
admin.site.register(Produit)
admin.site.register(Ration)
admin.site.register(PoulleVendu)
admin.site.register(PoulleMorte)
admin.site.register(Oeuf)
admin.site.register(OeufVendu)
admin.site.register(Perte)