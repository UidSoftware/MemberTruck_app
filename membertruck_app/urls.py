from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    PessoaCreateView, PessoaListView, PessoaDetailView,
    FuncionarioListView, FuncionarioDetailView,
    AssociadoListView, AssociadoDetailView
)

urlpatterns = [
    # Rotas de Autenticação JWT
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Rotas para Pessoa (Seu usuário principal)
    path('pessoas/register/', PessoaCreateView.as_view(), name='pessoa_register'), # Para criar novos usuários
    path('pessoas/', PessoaListView.as_view(), name='pessoa_list'),
    path('pessoas/<int:idPess>/', PessoaDetailView.as_view(), name='pessoa_detail'),

    # Rotas para Funcionario
    path('funcionarios/', FuncionarioListView.as_view(), name='funcionario_list'),
    path('funcionarios/<int:idFunc>/', FuncionarioDetailView.as_view(), name='funcionario_detail'),

    # Rotas para Associado
    path('associados/', AssociadoListView.as_view(), name='associado_list'),
    path('associados/<int:idAsso>/', AssociadoDetailView.as_view(), name='associado_detail'),

    # Adicione rotas para Endereco, Departamento, Cargo, Plano, Veiculo se necessário
]