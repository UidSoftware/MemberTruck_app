from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import transaction
from django.contrib.auth import authenticate

from .models import (
    Pessoa, Endereco, Departamento, Cargo, Plano, 
    Veiculo, Funcionario, Associado, MensagemWhatsApp
)
from .serializers import (
    PessoaSerializer, EnderecoSerializer, DepartamentoSerializer, 
    CargoSerializer, PlanoSerializer, VeiculoSerializer, 
    FuncionarioSerializer, AssociadoSerializer, MensagemWhatsAppSerializer,
    MyTokenObtainPairSerializer, FuncionarioCompletoSerializer, 
    AssociadoCompletoSerializer
)


# =================== VIEWS DE AUTENTICAÇÃO ===================

class CustomTokenObtainPairView(TokenObtainPairView):
    """View customizada para login com JWT"""
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            return response
        except Exception as e:
            return Response({
                'error': 'Erro no login',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """View para logout - adiciona token à blacklist se configurado"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Se usar token blacklisting
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'message': 'Logout realizado com sucesso'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Erro no logout',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# =================== VIEWS DE PESSOA ===================

class PessoaCreateView(generics.CreateAPIView):
    queryset = Pessoa.objects.all()
    serializer_class = PessoaSerializer
    permission_classes = [AllowAny]  # Para permitir criação inicial
    
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'error': 'Erro ao criar pessoa',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class PessoaListView(generics.ListAPIView):
    queryset = Pessoa.objects.all()
    serializer_class = PessoaSerializer
    permission_classes = [IsAuthenticated]


class PessoaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pessoa.objects.all()
    serializer_class = PessoaSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'idPess'


# =================== VIEWS DE FUNCIONÁRIO ===================

class FuncionarioListView(generics.ListCreateAPIView):
    queryset = Funcionario.objects.select_related(
        'idPessFunc', 'idDepaFunc', 'idCargFunc', 'gestor__idPessFunc'
    ).all()
    serializer_class = FuncionarioSerializer
    permission_classes = [IsAuthenticated]


class FuncionarioDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Funcionario.objects.select_related(
        'idPessFunc', 'idDepaFunc', 'idCargFunc', 'gestor__idPessFunc'
    ).all()
    serializer_class = FuncionarioSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'idFunc'


class FuncionarioCompletoCreateView(APIView):
    """Cria Pessoa + Funcionário em uma única transação"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = FuncionarioCompletoSerializer(data=request.data)
        if serializer.is_valid():
            try:
                funcionario = serializer.save()
                response_data = FuncionarioSerializer(funcionario).data
                return Response(response_data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': 'Erro ao criar funcionário completo',
                    'message': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GestoresListView(generics.ListAPIView):
    """Lista apenas funcionários que são gestores"""
    queryset = Funcionario.objects.filter(is_gestor=True).select_related('idPessFunc')
    serializer_class = FuncionarioSerializer
    permission_classes = [IsAuthenticated]


class ConsultoresPorGestorView(generics.ListAPIView):
    """Lista consultores de um gestor específico"""
    serializer_class = FuncionarioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        gestor_id = self.kwargs['gestor_id']
        return Funcionario.objects.filter(
            gestor_id=gestor_id, 
            is_gestor=False
        ).select_related('idPessFunc')


# =================== VIEWS DE ASSOCIADO ===================

class AssociadoListView(generics.ListCreateAPIView):
    queryset = Associado.objects.select_related(
        'idPessAsso', 'idPlanAsso', 'consultor__idPessFunc'
    ).prefetch_related('veiculos').all()
    serializer_class = AssociadoSerializer
    permission_classes = [IsAuthenticated]


class AssociadoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Associado.objects.select_related(
        'idPessAsso', 'idPlanAsso', 'consultor__idPessFunc'
    ).prefetch_related('veiculos').all()
    serializer_class = AssociadoSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'idAsso'


class AssociadoCompletoCreateView(APIView):
    """Cria Pessoa + Associado em uma única transação"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = AssociadoCompletoSerializer(data=request.data)
        if serializer.is_valid():
            try:
                associado = serializer.save()
                response_data = AssociadoSerializer(associado).data
                return Response(response_data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': 'Erro ao criar associado completo',
                    'message': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssociadosPorConsultorView(generics.ListAPIView):
    """Lista associados de um consultor específico"""
    serializer_class = AssociadoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        consultor_id = self.kwargs['consultor_id']
        return Associado.objects.filter(consultor_id=consultor_id).select_related(
            'idPessAsso', 'idPlanAsso', 'consultor__idPessFunc'
        ).prefetch_related('veiculos')


# =================== VIEWS AUXILIARES (ComboBox) ===================

class EnderecoListView(generics.ListCreateAPIView):
    queryset = Endereco.objects.all()
    serializer_class = EnderecoSerializer
    permission_classes = [IsAuthenticated]


class EnderecoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Endereco.objects.all()
    serializer_class = EnderecoSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'idEnde'


class DepartamentoListView(generics.ListCreateAPIView):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    permission_classes = [IsAuthenticated]


class DepartamentoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'idDepa'


class CargoListView(generics.ListCreateAPIView):
    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer
    permission_classes = [IsAuthenticated]


class CargoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'idCarg'


class PlanoListView(generics.ListCreateAPIView):
    queryset = Plano.objects.all()
    serializer_class = PlanoSerializer
    permission_classes = [IsAuthenticated]


class PlanoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plano.objects.all()
    serializer_class = PlanoSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'idPlan'


# =================== VIEWS DE VEÍCULO ===================

class VeiculoListView(generics.ListCreateAPIView):
    queryset = Veiculo.objects.select_related('associado__idPessAsso').all()
    serializer_class = VeiculoSerializer
    permission_classes = [IsAuthenticated]


class VeiculoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Veiculo.objects.select_related('associado__idPessAsso').all()
    serializer_class = VeiculoSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'idVeic'


class VeiculosPorAssociadoView(generics.ListAPIView):
    """Lista veículos de um associado específico"""
    serializer_class = VeiculoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        associado_id = self.kwargs['associado_id']
        return Veiculo.objects.filter(associado_id=associado_id)


# =================== VIEWS DE MENSAGEM WHATSAPP ===================

class MensagemWhatsAppListView(generics.ListCreateAPIView):
    queryset = MensagemWhatsApp.objects.select_related('associado__idPessAsso').all()
    serializer_class = MensagemWhatsAppSerializer
    permission_classes = [IsAuthenticated]


class MensagemWhatsAppDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MensagemWhatsApp.objects.select_related('associado__idPessAsso').all()
    serializer_class = MensagemWhatsAppSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'idMensagem'


class EnviarMensagemWhatsAppView(APIView):
    """View para enviar mensagens via WhatsApp"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            associado_id = request.data.get('associado_id')
            tipo_mensagem = request.data.get('tipo_mensagem')
            conteudo = request.data.get('conteudo')
            
            if not all([associado_id, tipo_mensagem, conteudo]):
                return Response({
                    'error': 'Dados obrigatórios: associado_id, tipo_mensagem, conteudo'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Buscar associado
            try:
                associado = Associado.objects.select_related('idPessAsso').get(
                    idAsso=associado_id
                )
            except Associado.DoesNotExist:
                return Response({
                    'error': 'Associado não encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Criar registro da mensagem
            mensagem = MensagemWhatsApp.objects.create(
                associado=associado,
                tipoMensagem=tipo_mensagem,
                conteudo=conteudo,
                status='pendente'
            )
            
            # Aqui você implementaria o envio via PyWhatsKit
            # Por enquanto, simular sucesso
            telefone = associado.idPessAsso.telefonePess
            if telefone:
                # TODO: Implementar PyWhatsKit aqui
                # pywhatkit.sendwhatmsg(f"+55{telefone}", conteudo, hora, minuto)
                mensagem.status = 'enviada'
                mensagem.save()
                
                return Response({
                    'message': 'Mensagem enviada com sucesso',
                    'mensagem_id': mensagem.idMensagem
                }, status=status.HTTP_200_OK)
            else:
                mensagem.status = 'erro'
                mensagem.save()
                return Response({
                    'error': 'Associado não possui telefone cadastrado'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': 'Erro ao enviar mensagem',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =================== VIEWS DE DASHBOARD/RELATÓRIOS ===================

class DashboardView(APIView):
    """View para dados do dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            data = {
                'total_associados': Associado.objects.count(),
                'total_funcionarios': Funcionario.objects.count(),
                'total_gestores': Funcionario.objects.filter(is_gestor=True).count(),
                'total_consultores': Funcionario.objects.filter(is_gestor=False).count(),
                'total_veiculos': Veiculo.objects.count(),
                'mensagens_enviadas_hoje': MensagemWhatsApp.objects.filter(
                    dataEnvio__date=timezone.now().date(),
                    status='enviada'
                ).count()
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Erro ao buscar dados do dashboard',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =================== VIEW DE TESTE DE CONEXÃO ===================

class TesteConexaoView(APIView):
    """View simples para testar a conexão da API"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'message': 'API funcionando corretamente',
            'timestamp': timezone.now()
        }, status=status.HTTP_200_OK)