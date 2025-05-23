from django.shortcuts import render,redirect,get_object_or_404
from .models import Evenement,Reservation,Billet,Paiement
from Auth.models import Utilisateur,Profile
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from django.http import HttpResponse
from django.views import View
@login_required
def home(request):
    evenements = Evenement.objects.all().order_by('date_evenement')
    q = lieu = categorie = date = ""
    if request.method == "POST":
        q = request.POST.get("q", "")
        lieu = request.POST.get("lieu", "")
        categorie = request.POST.get("categorie", "")
        date = request.POST.get("date", "")
        if q:
            evenements = evenements.filter(titre__icontains=q)
        if lieu:
            evenements = evenements.filter(lieu__icontains=lieu)
        if categorie:
            evenements = evenements.filter(categorie__iexact=categorie)
        if date:
            evenements = evenements.filter(date_evenement__date=date)
    return render(request, "home.html", {
        "evenements": evenements,
        "q": q,
        "lieu": lieu,
        "categorie": categorie,
        "date": date,
    })
@login_required
def consultation(request):
    reservations = Reservation.objects.filter(client=request.user)
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'consultation.html', {
        'reservations': reservations,
        'profile': profile
    })
def logout_view(request):
    logout(request)
    return redirect('login')
@login_required
def evenement_detail(request, evenement_id):
    evenement = get_object_or_404(Evenement, id=evenement_id)
    return render(request, 'evenement_detail.html', {'evenement': evenement})
@login_required
def reserver_evenement(request, evenement_id):
    evenement = get_object_or_404(Evenement, id=evenement_id)
    if evenement.nombre_place <= 0:
        messages.error(request, "Il n'y a plus de places disponibles pour cet événement.")
        return redirect('evenement_detail', evenement_id=evenement.id)
    if request.method == 'POST':
        try:
            nombre_places_reservees = int(request.POST.get('nombre_places', 0))
        except (KeyError, ValueError):
            messages.error(request, "Veuillez entrer un nombre valide de places.")
            return redirect('evenement_detail', evenement_id=evenement.id)
        if nombre_places_reservees <= 0 or nombre_places_reservees > evenement.nombre_place:
            messages.error(request, f"Veuillez sélectionner un nombre valide de places (max {evenement.nombre_place}).")
            return redirect('evenement_detail', evenement_id=evenement.id)
        evenement.nombre_place -= nombre_places_reservees
        evenement.save()
        reservation = Reservation.objects.create(
            client=request.user,
            evenement_id=evenement,
            nombre_place_reservee=nombre_places_reservees,
            statut='en cours',
            prix=evenement.prix * nombre_places_reservees,
            created_by=request.user.username,
            modified_by=request.user.username,
        )
        Billet.objects.create(
            num_reservation=reservation,
            status='en cours',
            prix=reservation.prix,
            created_by=request.user.username,
            modified_by=request.user.username,
        )
        messages.success(request, "Votre réservation a été effectuée avec succès.")
        return redirect('consultation')
    return render(request, 'reserver_evenement.html', {'evenement': evenement})
@login_required
def delete_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, client=request.user)
    billet = Billet.objects.get(num_reservation=reservation)
    if reservation.statut == 'confirmée':
        messages.error(request, "Vous ne pouvez pas supprimer une réservation déjà confirmée.")
    else:
        evenement = reservation.evenement_id
        nouvel_total = evenement.nombre_place + reservation.nombre_place_reservee
        evenement.nombre_place = min(nouvel_total, evenement.capacite_maximale)
        reservation.statut = 'annulée'
        billet.status = 'annulée'
        evenement.save()
        reservation.save()
        billet.save()
        messages.success(request, "Votre réservation a été annulée.")
    return redirect('home')
@login_required
def validate_reservation(request, reservation_id):
    reservation = Reservation.objects.get(id=reservation_id, client=request.user)
    billet= Billet.objects.get(num_reservation=reservation)
    if reservation.statut == 'confirmée':
        messages.error(request, "Cette réservation a déjà été validée.")
        return redirect('consultation')
    return redirect('paiement_view', reservation_id=reservation.id)
def mask_card_number(card_number):
    return '*' * (len(card_number) - 4) + card_number[-4:]
@login_required
def paiement_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, client=request.user)
    billet = get_object_or_404(Billet, num_reservation=reservation)
    if reservation.statut != 'en cours':
        messages.error(request, "Cette réservation ne peut pas être confirmée car elle est déjà annulée.")
        return redirect('consultation')
    if request.method == 'POST':
        action = request.POST.get('action_type')
        mode_paiement = request.POST.get('payment_mode')
        full_name = request.POST.get("cardholder_name")
        card_number = request.POST.get("card_number")
        month= request.POST.get("expiry_month")
        year= request.POST.get("expiry_year")
        masked_card_number = mask_card_number(card_number)
        if action == 'annuler':
            paiement = Paiement.objects.create(
                bilet_id=billet,
                montant=reservation.prix,
                created_by=request.user,
                full_name=full_name,
                card_number=masked_card_number,
                statut='Annuluée',
                mode_paiement=mode_paiement,
                date_expiration=f"{month}/{year}",
            )
            messages.info(request, "Le paiement a été annulé.")
            return redirect('consultation')
        elif action == 'payer':
            mode_paiement = request.POST.get('payment_mode')
            full_name = request.POST.get("cardholder_name")
            card_number = request.POST.get("card_number")
            paiement = Paiement.objects.create(
                bilet_id=billet,
                montant=reservation.prix,
                created_by=request.user,
                full_name=full_name,
                card_number= masked_card_number,
                statut='en cours',
                mode_paiement=mode_paiement,
                date_expiration=f"{month}/{year}",
            )
            reservation.statut = 'confirmée'
            billet.status = 'confirmée'
            reservation.save()
            billet.save()
            return redirect('confirmation_paiement', paiement_id=paiement.id)
    return render(request, 'paiement.html', {'reservation': reservation})
@login_required
def confirmation_paiement(request, paiement_id):
    paiement = Paiement.objects.get(id=paiement_id)
    paiement.statut = 'confirmée'
    paiement.save()
    return render(request, 'confirmation_paiement.html', {'paiement': paiement})
@login_required
def profile(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'profile.html', {
        'user': request.user,
        'profile': profile
    })
@login_required
def modifier_profile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')  
        address = request.POST.get('address')
        bio = request.POST.get('bio')
        image = request.FILES.get('profile_picture') 
        if not first_name or not last_name or not email:
            messages.error(request, "Tous les champs obligatoires ne sont pas remplis.")
            return render(request, 'modifier_profile.html', {'user': user, 'profile': profile})
        if Utilisateur.objects.exclude(id=user.id).filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé par un autre compte.")
            return render(request, 'modifier_profile.html', {'user': user, 'profile': profile})
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        profile.phone_number = phone_number
        profile.address = address
        profile.bio = bio
        if image:  
            profile.image = image
        profile.save()
        messages.success(request, "Votre profil a été mis à jour avec succès.")
        return redirect('profile')  
    return render(request, 'modifier_profile.html', {'user': user, 'profile': profile})
@login_required
def update_profile_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        profile = request.user.profile
        profile.image = request.FILES['image']
        profile.save()
        messages.success(request, "Image de profil mise à jour avec succès")
    return redirect('profile')
@login_required
def download_ticket(request):
    paiement = Paiement.objects.filter(bilet_id__created_by=request.user.username).last()
    if not paiement:
        return HttpResponse("Aucun billet trouvé", status=404)
    reservation = paiement.bilet_id.num_reservation
    evenement = reservation.evenement_id
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="billet.pdf"'
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    p.setFillColor(colors.HexColor('#003366')) 
    p.rect(0, height - 80, width, 80, fill=1, stroke=0)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, height - 50, "EventPro.COM")
    p.setFont("Helvetica-Bold", 14)
    p.drawRightString(width - 50, height - 50, f"Billet N°: {paiement.bilet_id.id}") 
    y_position = height - 120
    p.setStrokeColor(colors.HexColor('#CCCCCC'))
    p.setFillColor(colors.white)
    p.rect(40, y_position - 350, width - 80, 350, fill=1, stroke=1)
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(colors.HexColor('#003366'))
    p.drawString(60, y_position - 30, "INFORMATIONS ÉVÉNEMENT")
    p.setFont("Helvetica", 12)
    p.setFillColor(colors.black)
    event_details_y = y_position - 60
    p.drawString(60, event_details_y, f"Événement: {evenement.titre}")
    p.drawString(60, event_details_y - 25, f"Lieu: {evenement.lieu}")
    p.drawString(60, event_details_y - 50, f"Date: {evenement.date_evenement.strftime('%d/%m/%Y %H:%M')}")
    p.drawString(60, event_details_y - 75, f"Nombre de Places: {reservation.nombre_place_reservee}")
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(colors.HexColor('#003366'))
    p.drawString(width/2 + 20, y_position - 30, "INFORMATIONS CLIENT")
    p.setFont("Helvetica", 12)
    p.setFillColor(colors.black)
    p.drawString(width/2 + 20, y_position - 60, f"Nom: {request.user.last_name}")
    p.drawString(width/2 + 20, y_position - 85, f"Prénom: {request.user.first_name}")
    p.drawString(width/2 + 20, y_position - 110, f"Type: Standard")
    separator_x = width / 2
    top_y = y_position - 20
    bottom_y = y_position - 130 
    p.setStrokeColor(colors.HexColor('#CCCCCC'))  
    p.setLineWidth(1)
    p.line(separator_x, top_y, separator_x, bottom_y)
    p.setStrokeColor(colors.HexColor('#003366'))
    p.setLineWidth(1)
    p.line(50, event_details_y - 100, width - 50, event_details_y - 100)
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(colors.HexColor('#003366'))
    p.drawString(60, event_details_y - 130, f"PRIX TOTAL: {paiement.montant} MAD")
    qr_value = f"paiement:{paiement.id}"
    qr_code = qr.QrCodeWidget(qr_value)
    bounds = qr_code.getBounds()
    qr_size = 100
    width_qr = bounds[2] - bounds[0]
    height_qr = bounds[3] - bounds[1]
    d = Drawing(qr_size, qr_size, transform=[qr_size/width_qr, 0, 0, qr_size/height_qr, 0, 0])
    d.add(qr_code)
    renderPDF.draw(d, p, width - 150, y_position - 300)
    p.setFont("Helvetica", 8)
    p.setFillColor(colors.HexColor('#666666'))
    p.drawString(width - 150, y_position - 310, "Scannez ce code pour")
    p.drawString(width - 150, y_position - 320, "vérifier votre billet")
    p.setFillColor(colors.HexColor('#003366'))
    p.rect(0, 40, width, 40, fill=1, stroke=0)
    p.setFont("Helvetica", 10)
    p.setFillColor(colors.white)
    p.drawCentredString(width/2, 55, "Contact: EventPro@gmail.com | Tél: +212 6 12 34 56 78")
    p.setFont("Helvetica-Bold", 12)
    p.setFillColor(colors.HexColor('#4CAF50'))
    p.drawCentredString(width/2, y_position - 380, "Merci pour votre confiance et bon événement !")
    p.showPage()
    p.save()
    return response
@login_required
def historique_paiement(request):
    paiements = Paiement.objects.filter(bilet_id__created_by=request.user.username).order_by('-date_paiement')
    return render(request, 'historique_paiement.html', {'paiements': paiements})





