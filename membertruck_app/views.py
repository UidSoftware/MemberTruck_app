from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Pessoa, Endereco, Departamento, Cargo, Plano, Veiculo, Funcionario, Associado
from .serializers import (
    PessoaSerializer, EnderecoSerializer, DepartamentoSerializer, CargoSerializer,
    PlanoSerializer, VeiculoSerializer, FuncionarioSerializer, AssociadoSerializer,
    MyTokenObtainPairSerializer # Para o login, embora não seja usado diretamente em uma view
)

# View de criação de Pessoa (para criar usuários, incluindo funcionários e associados)
class PessoaCreateView(generics.CreateAPIView):
    queryset = Pessoa.objects.all()
    serializer_class = PessoaSerializer
    permission_classes = [AllowAny] # Permite criar pessoas sem autenticação inicial

    def perform_create(self, serializer):
        # Sobrescreve para usar create_user do manager
        password = serializer.validated_data.pop('password', None) # Pega a senha (que será write_only)
        user = Pessoa.objects.create_user(**serializer.validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

# Views de listagem e detalhe (para demonstrar)
class PessoaListView(generics.ListAPIView):
    queryset = Pessoa.objects.all()
    serializer_class = PessoaSerializer
    permission_classes = [IsAuthenticated] # Exige autenticação para ver Pessoas

class PessoaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pessoa.objects.all()
    serializer_class = PessoaSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'idPess' # Usa idPess como o campo de lookup na URL

# Outras Views (exemplo)
class FuncionarioListView(generics.ListCreateAPIView):
    queryset = Funcionario.objects.all()
    serializer_class = FuncionarioSerializer
    permission_classes = [IsAuthenticated] # Somente autenticados podem ver/criar

class FuncionarioDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Funcionario.objects.all()
    serializer_class = FuncionarioSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'idFunc'

class AssociadoListView(generics.ListCreateAPIView):
    queryset = Associado.objects.all()
    serializer_class = AssociadoSerializer
    permission_classes = [IsAuthenticated]

class AssociadoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Associado.objects.all()
    serializer_class = AssociadoSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'idAsso'

# Você pode criar views semelhantes para Endereco, Departamento, Cargo, Plano, Veiculo.