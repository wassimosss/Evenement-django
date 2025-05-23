from django.urls import path
from . import views
urlpatterns = [
    path('',views.home,name='home'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('consultation/', views.consultation, name='consultation'),
    path('evenement/<int:evenement_id>/', views.evenement_detail, name='evenement_detail'),
    path('modifier_profil/', views.modifier_profile, name='modifier_profile'),
    path('reservation/<int:evenement_id>/', views.reserver_evenement, name='reserver_evenement'),
    path('reservation/<int:reservation_id>/validate/', views.validate_reservation, name='validate_reservation'),
    path('reservation/<int:reservation_id>/delete/', views.delete_reservation, name='delete_reservation'),
    path('reservation/<int:reservation_id>/paiement/', views.paiement_view, name='paiement_view'),
    path('paiement/confirmation/<int:paiement_id>/', views.confirmation_paiement, name='confirmation_paiement'),
    path('download_ticket/', views.download_ticket, name='download_ticket'),
    path('profile/update-image/', views.update_profile_image, name='update_profile_image'),
    path('historique-paiement/', views.historique_paiement, name='historique_paiement'),
]