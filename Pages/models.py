from django.db import models
from django.conf import settings 
# Create your models here.
class Evenement(models.Model):
    titre=models.CharField(max_length=50,blank=False,null=False)
    description=models.TextField(blank=False,null=False)
    prix=models.DecimalField(max_digits=10, decimal_places=2, blank=False,null=False,default=0.0)
    date_evenement=models.DateTimeField(blank=False,null=False)
    lieu=models.CharField(max_length=50,blank=False,null=False)
    nombre_place=models.PositiveIntegerField(blank=False,null=False)
    categorie=models.CharField(max_length=50,blank=False,null=False)
    image=models.ImageField(upload_to='evenement_photos/', blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.CharField(max_length=50,blank=False,null=False)
    modified_at=models.DateTimeField(auto_now=True)
    modified_by=models.CharField(max_length=50,blank=False,null=False)
    capacite_maximale = models.PositiveIntegerField(default=0)
    def __str__(self):
        return f"Evenement {self.titre} at {self.lieu} on {self.date_evenement}"
    def save(self, *args, **kwargs):
        if not self.capacite_maximale:
            self.capacite_maximale = self.nombre_place  # Initialise à la première sauvegarde
        super().save(*args, **kwargs)
class Reservation(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    evenement_id = models.ForeignKey(Evenement, on_delete=models.CASCADE)  # Clé étrangère vers Evenement
    nombre_place_reservee = models.PositiveIntegerField(default=0)  # Champ pour stocker le nombre de places réservées
    STATUT_CHOICES = [
        ('confirmée', 'Confirmée'),
        ('en cours', 'En cours'),
        ('annulée', 'Annulée'), 
    ]
    prix = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False, default=0.0)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en cours')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=50, blank=False, null=False)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(max_length=50, blank=False, null=False)
    def __str__(self):
        return f"Reservation {self.id} for {self.client.username} on {self.evenement_id.titre}"
class Billet(models.Model):
    num_reservation=models.ForeignKey(Reservation,on_delete=models.CASCADE)
    date_reservation=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=50,blank=False,null=False)
    prix=models.DecimalField(max_digits=10, decimal_places=2, blank=False,null=False,default=0.0)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.CharField(max_length=50,blank=False,null=False)
    modified_at=models.DateTimeField(auto_now=True)
    modified_by=models.CharField(max_length=50,blank=False,null=False)
    def __str__(self):
        return f"Billet {self.id} for {self.num_reservation}"
class Paiement(models.Model):
    bilet_id=models.ForeignKey(Billet,on_delete=models.CASCADE)
    full_name=models.CharField(max_length=50, blank=False, null=False, default='NOne')
    mode_paiement = models.CharField(max_length=20, choices=[
        ('visa', 'Visa'),
        ('mastercard', 'MasterCard'),
    ] ,
     default='NOne')
    STATUT_CHOICES = [
        ('confirmée', 'Confirmée'),
        ('en cours', 'En cours'),
        ('annulée', 'Annulée'),
    ]
    card_number = models.CharField(max_length=16, blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en cours')
    date_paiement=models.DateTimeField(auto_now_add=True)
    date_expiration=models.CharField(max_length=7, blank=True, null=True)  
    montant=models.DecimalField(max_digits=10, decimal_places=2, blank=False,null=False)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.CharField(max_length=50,blank=False,null=False)
    modified_at=models.DateTimeField(auto_now=True)
    modified_by=models.CharField(max_length=50,blank=False,null=False)
    def __str__(self):
        return f"Paiement {self.mode_paiement} with status {self.statut}"
