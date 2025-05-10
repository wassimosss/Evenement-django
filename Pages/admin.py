from django.contrib import admin
from .models import Evenement,Reservation
class EvenementAdmin(admin.ModelAdmin):
    list_display = ('titre', 'lieu', 'date_evenement','image','prix')
    search_fields = ('titre', 'lieu', 'categorie')
    list_filter = ('categorie', 'date_evenement')

    def save_model(self, request, obj, form, change):
        if not obj.pk:  
            obj.created_by = request.user.username
        obj.modified_by = request.user.username 
        super().save_model(request, obj, form, change)
admin.site.register(Evenement, EvenementAdmin)
admin.site.register(Reservation)
