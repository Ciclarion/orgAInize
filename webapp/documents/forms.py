from django import forms
from .models import Document, Formation

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['nom', 'categorie', 'sous_categorie', 'niveau_acces', 'formation', 'fichier']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sous_categorie'].queryset = Document.objects.none()

        if 'categorie' in self.data:
            try:
                categorie = self.data.get('categorie')
                if categorie == 'pedagogique':
                    self.fields['sous_categorie'].queryset = Document.objects.filter(categorie=categorie).values_list('sous_categorie', flat=True).distinct()
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['sous_categorie'].queryset = self.instance.categorie.sous_categorie_set.all()


class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        fields = ['nom', 'date', 'nombre_personnes', 'frais_inscription', 'pre_requis', 'diplome', 'metier', 'syllabus_pdf']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            # Vous pouvez personnaliser d'autres champs ici si nécessaire
        }
        
        
class NewConversationForm(forms.Form):
    name = forms.CharField(label='Conversation Name', max_length=255)
