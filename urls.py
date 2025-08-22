from django.urls import path
from .views import PessoaList, PessoaDetail # Importe suas views

urlpatterns = [
    path('pessoas/', PessoaList.as_view(), name='pessoa-list'),
    path('pessoas/<int:pk>/', PessoaDetail.as_view(), name='pessoa-detail'),
    # Adicione outras URLs do seu app aqui
    
]