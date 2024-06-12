from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import DocumentUploadForm, FormationForm, NewConversationForm
from .models import Document, Formation
from django.utils import timezone
from django.http import FileResponse, Http404,HttpResponse
import requests
import json
import os
from django.conf import settings


def logout_view(request):
    logout(request)
    return redirect('login')  # Redirige vers la page de connexion après la déconnexion
    
@login_required
def upload_document(request):
    if request.user.user_type != 'pro':
        return redirect('chatbot')
    
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.date_upload = timezone.now()
            
            # Define the directory structure
            access_path = 'interne' if document.niveau_acces == 'interne' else 'externe'
            category_path = document.categorie
            subcategory_path = document.sous_categorie if document.sous_categorie else ''
            formation_path = document.formation.nom if document.formation else ''
            save_path = os.path.join('documents', access_path, category_path, subcategory_path, formation_path)
            
            
            # Save the file
            document.fichier.name = os.path.join(save_path, document.fichier.name)
            document.save()

            # Send file and metadata to LangChain for indexing
            metadata = {
                'nom': document.nom,
                'fichier_name' : document.fichier.name,
                'categorie': document.categorie,
                'sous_categorie': document.sous_categorie if document.sous_categorie else '',
                'niveau_acces': document.niveau_acces,
                'formation': document.formation.nom if document.formation else '',
                'date_upload': document.date_upload.isoformat(),
            }

            with open(document.fichier.path, 'rb') as f:
                response = requests.post(
                    'http://127.0.0.1:8005/index-file/',
                    files={'file': f},
                    data={'access': document.niveau_acces, 'metadata': json.dumps(metadata)}
                )
                response_data = response.json()
                if response.status_code != 200:
                    # Handle the error
                    print("Error indexing file:", response_data)

            return redirect('document_list')
    else:
        form = DocumentUploadForm()
    
    return render(request, 'upload_document.html', {'form': form})

@login_required
def document_list(request):
    if request.user.user_type != 'pro':
        return redirect('chatbot')

    documents = Document.objects.all()
    
    formation_id = request.GET.get('formation')
    access_level = request.GET.get('access_level')
    category = request.GET.get('category')
    search_query = request.GET.get('search')

    if formation_id:
        documents = documents.filter(formation_id=formation_id)
    if access_level:
        documents = documents.filter(niveau_acces=access_level)
    if category:
        documents = documents.filter(categorie=category)

    if search_query != "None" and search_query:
        documents = documents.filter(nom__icontains=search_query)

    formations = Formation.objects.all()

    return render(request, 'document_list.html', {
        'documents': documents,
        'formations': formations,
        'formation_id': formation_id,
        'access_level': access_level,
        'category': category,
        'search_query': search_query,
    })


@login_required
def serve_pdf(request, path):
    
    file_path = os.path.join("documents/documents/", path)
    print(file_path)
    if os.path.exists(file_path):
        print("ici")
        res = open(file_path, 'rb').read()
        return HttpResponse(res, content_type="application/pdf")
    else:
        raise Http404()
        
@login_required
def view_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    return FileResponse(document.fichier.open(), content_type='application/pdf')

@login_required
def delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    
    # Supprimer le document du système de fichiers
    document.fichier.delete()
    
    # Désindexer le document de ChromaDB
    try:
        response = requests.post(
            'http://127.0.0.1:8005/deindex-file/',
            data={'name': document.nom, 'access': document.niveau_acces}
        )
        if response.status_code != 200:
            print("Error deindexing document:", response.json())
    except Exception as e:
        print("Error communicating with LangChain server:", str(e))
    
    # Supprimer le document de la base de données
    document.delete()
    
    return redirect('document_list')

@login_required
def create_formation(request):
    if request.user.user_type != 'pro':
        return redirect('chatbot')
    
    if request.method == 'POST':
        form = FormationForm(request.POST, request.FILES)
        if form.is_valid():
            formation = form.save()
            
            # Préparer les données à envoyer pour l'indexation
            formation_data = {
                'nom': formation.nom,
                'date': formation.date.isoformat(),
                'nombre_personnes': formation.nombre_personnes,
                'frais_inscription': str(formation.frais_inscription),
                'pre_requis': formation.pre_requis,
                'diplome': formation.diplome,
                'metier': formation.metier,
                'date_upload': formation.date_upload.isoformat(),
            }
            
            # Envoyer les données au serveur LangChain
            files = {}
            if formation.syllabus_pdf:
                files['syllabus_pdf'] = formation.syllabus_pdf.file.read()
                formation_data['syllabus_pdf_name'] = formation.syllabus_pdf.name
            
            response = requests.post(
                'http://127.0.0.1:8005/index-formation/',
                files=files,
                data={'formation_data': json.dumps(formation_data)}
            )
            
            if response.status_code != 200:
                # Gérer l'erreur
                print("Error indexing formation:", response.json())
            
            return redirect('formation_list')
    else:
        form = FormationForm()
    
    return render(request, 'create_formation.html', {'form': form})

@login_required
def formation_list(request):
    if request.user.user_type != 'pro':
        return redirect('chatbot')

    formations = Formation.objects.all()
    return render(request, 'formation_list.html', {'formations': formations})

@login_required
def pro_dashboard(request):
    if request.user.user_type != 'pro':
        return redirect('chatbot')
    return render(request, 'pro_dashboard.html')

@login_required
def edit_formation(request, formation_id):
    formation = get_object_or_404(Formation, id=formation_id)
    if request.user.user_type != 'pro':
        return redirect('chatbot')

    if request.method == 'POST':
        form = FormationForm(request.POST, request.FILES, instance=formation)
        if form.is_valid():
            # Déindexer l'ancienne formation
            # Désindexer le document de ChromaDB
            try:
                response = requests.post(
                    'http://127.0.0.1:8005/deindex-formation/',
                    data={'name': formation.nom, 'access': 'externe'}
                )
                if response.status_code != 200:
                    print("Error deindexing document:", response.json())
            except Exception as e:
                print("Error communicating with LangChain server:", str(e))


            formation = form.save()

            # Réindexer la nouvelle formation
            formation_data = {
                'nom': formation.nom,
                'date': formation.date.isoformat(),
                'nombre_personnes': formation.nombre_personnes,
                'frais_inscription': str(formation.frais_inscription),
                'pre_requis': formation.pre_requis,
                'diplome': formation.diplome,
                'metier': formation.metier,
                'date_upload': formation.date_upload.isoformat(),
            }
            
            files = {}
            if formation.syllabus_pdf:
                files['syllabus_pdf'] = formation.syllabus_pdf.file.read()
                formation_data['syllabus_pdf_name'] = formation.syllabus_pdf.name
            
            response = requests.post(
                'http://127.0.0.1:8005/index-formation/',
                files=files,
                data={'formation_data': json.dumps(formation_data)}
            )
            
            if response.status_code != 200:
                # Gérer l'erreur
                print("Error indexing formation:", response.json())

            return redirect('formation_list')
    else:
        form = FormationForm(instance=formation)
    
    return render(request, 'edit_formation.html', {'form': form, 'formation': formation})

@login_required
def delete_formation(request, formation_id):
    formation = get_object_or_404(Formation, id=formation_id)
    if request.user.user_type != 'pro':
        return redirect('chatbot')
    
    if request.method == 'POST':
        # Déindexer la formation avant de la supprimer
        
        # Désindexer le document de ChromaDB
        try:
            response = requests.post(
                'http://127.0.0.1:8005/deindex-formation/',
                data={'name': formation.nom, 'access': 'externe'}
            )
            if response.status_code != 200:
                print("Error deindexing document:", response.json())
        except Exception as e:
            print("Error communicating with LangChain server:", str(e))
                 
        formation.delete()
        return redirect('formation_list')
    
    return render(request, 'delete_formation.html', {'formation': formation})
