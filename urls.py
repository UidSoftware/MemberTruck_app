from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # =================== AUTENTICAÇÃO ===================
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # =================== TESTE ===================
    path('teste/', views.TesteConexaoView.as_view(), name='teste_conexao'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # =================== PESSOA ===================
    path('pessoas/', views.PessoaListView.as_view(), name='pessoa_list'),
    path('pessoas/create/', views.PessoaCreateView.as_view(), name='pessoa_create'),
    path('pessoas/<int:idPess>/', views.PessoaDetailView.as_view(), name='pessoa_detail'),
    
    # =================== FUNCIONÁRIO ===================
    path('funcionarios/', views.FuncionarioListView.as_view(), name='funcionario_list'),
    path('funcionarios/<int:idFunc>/', views.FuncionarioDetailView.as_view(), name='funcionario_detail'),
    path('funcionarios/completo/', views.FuncionarioCompletoCreateView.as_view(), name='funcionario_completo_create'),
    
    # Hierarquia
    path('gestores/', views.GestoresListView.as_view(), name='gestores_list'),
    path('gestores/<int:gestor_id>/consultores/', views.ConsultoresPorGestorView.as_view(), name='consultores_por_gestor'),
    
    # =================== ASSOCIADO ===================
    path('associados/', views.AssociadoListView.as_view(), name='associado_list'),
    path('associados/<int:idAsso>/', views.AssociadoDetailView.as_view(), name='associado_detail'),
    path('associados/completo/', views.AssociadoCompletoCreateView.as_view(), name='associado_completo_create'),
    path('consultores/<int:consultor_id>/associados/', views.AssociadosPorConsultorView.as_view(), name='associados_por_consultor'),
    
    # =================== VEÍCULO ===================
    path('veiculos/', views.VeiculoListView.as_view(), name='veiculo_list'),
    path('veiculos/<int:idVeic>/', views.VeiculoDetailView.as_view(), name='veiculo_detail'),
    path('associados/<int:associado_id>/veiculos/', views.VeiculosPorAssociadoView.as_view(), name='veiculos_por_associado'),
    
    # =================== AUXILIARES (ComboBox) ===================
    path('enderecos/', views.EnderecoListView.as_view(), name='endereco_list'),
    path('enderecos/<int:idEnde>/', views.EnderecoDetailView.as_view(), name='endereco_detail'),
    
    path('departamentos/', views.DepartamentoListView.as_view(), name='departamento_list'),
    path('departamentos/<int:idDepa>/', views.DepartamentoDetailView.as_view(), name='departamento_detail'),
    
    path('cargos/', views.CargoListView.as_view(), name='cargo_list'),
    path('cargos/<int:idCarg>/', views.CargoDetailView.as_view(), name='cargo_detail'),
    
    path('planos/', views.PlanoListView.as_view(), name='plano_list'),
    path('planos/<int:idPlan>/', views.PlanoDetailView.as_view(), name='plano_detail'),
    
    # =================== WHATSAPP ===================
    path('mensagens/', views.MensagemWhatsAppListView.as_view(), name='mensagem_list'),
    path('mensagens/<int:idMensagem>/', views.MensagemWhatsAppDetailView.as_view(), name='mensagem_detail'),
    path('mensagens/enviar/', views.EnviarMensagemWhatsAppView.as_view(), name='enviar_mensagem'),
]