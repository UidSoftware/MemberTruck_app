from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    PessoaCreateView, PessoaListView, PessoaDetailView,
    FuncionarioListView, FuncionarioDetailView,
    AssociadoListView, AssociadoDetailView,
    EnderecoListView, EnderecoDetailView,
    DepartamentoListView, DepartamentoDetailView,
    CargoListView, CargoDetailView,
    PlanoListView, PlanoDetailView,
    VeiculoListView, VeiculoDetailView
)

app_name = 'membertruck_app' # Mantenha o app_name

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
    
    # Rotas para Endereco
    path('Endereco/', EnderecoListView.as_view(), name='Endereco_list'),
    path('Endereco/<int:idEnde>/', EnderecoDetailView.as_view(), name='Endereco_detail'),

    # Rotas para Departamento
    path('Departamento/', DepartamentoListView.as_view(), name='Departamento_list'),
    path('Departamento/<int:idDepa>/', DepartamentoDetailView.as_view(), name='Departamento_detail'),

    # Rotas para Cargo
    path('Cargo/', CargoListView.as_view(), name='Cargo_list'),
    path('Cargo/<int:idCarg>/', CargoDetailView.as_view(), name='Cargo_detail'),

    # Rotas para Plano
    path('Plano/', PlanoListView.as_view(), name='Plano_list'),
    path('Plano/<int:idPlan>/', PlanoDetailView.as_view(), name='Plano_detail'),

    # Rotas para Veiculo
    path('Veiculo/', VeiculoListView.as_view(), name='Veiculo_list'),
    path('Veiculo/<int:idVeic>/', VeiculoDetailView.as_view(), name='Veiculo_detail'),
]