from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    Pessoa, Endereco, Departamento, Cargo, Plano, 
    Veiculo, Funcionario, Associado, MensagemWhatsApp
)


# Serializer customizado para JWT Login
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'usuarioPess'  # Campo de login customizado
    
    def validate(self, attrs):
        # Chama a validação padrão
        data = super().validate(attrs)
        
        # Adiciona informações extras ao token response
        data['user_info'] = {
            'idPess': self.user.idPess,
            'nomePess': self.user.nomePess,
            'usuarioPess': self.user.usuarioPess,
            'emailPess': self.user.emailPess,
            'is_staff': self.user.is_staff,
            'is_superuser': self.user.is_superuser,
        }
        
        # Verifica se é funcionário ou associado
        try:
            funcionario = Funcionario.objects.get(idPessFunc=self.user)
            data['user_info']['tipo_usuario'] = 'funcionario'
            data['user_info']['is_gestor'] = funcionario.is_gestor
            data['user_info']['funcionario_id'] = funcionario.idFunc
        except Funcionario.DoesNotExist:
            try:
                associado = Associado.objects.get(idPessAsso=self.user)
                data['user_info']['tipo_usuario'] = 'associado'
                data['user_info']['associado_id'] = associado.idAsso
            except Associado.DoesNotExist:
                data['user_info']['tipo_usuario'] = 'admin'
        
        return data


class PessoaSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Pessoa
        fields = [
            'idPess', 'nomePess', 'telefonePess', 'documentoPess',
            'nascimentoPess', 'emailPess', 'usuarioPess', 'password',
            'is_staff', 'is_active', 'idEndePess'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'idPess': {'read_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Pessoa.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = '__all__'


class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = '__all__'


class CargoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cargo
        fields = '__all__'


class PlanoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plano
        fields = '__all__'


class VeiculoSerializer(serializers.ModelSerializer):
    associado_nome = serializers.CharField(source='associado.idPessAsso.nomePess', read_only=True)
    
    class Meta:
        model = Veiculo
        fields = ['idVeic', 'nomeVeic', 'anoVeic', 'placaVeic', 'associado', 'associado_nome']
    
    def validate_placaVeic(self, value):
        """Valida formato da placa brasileira"""
        import re
        # Padrão antigo: ABC-1234 ou novo: ABC1D23
        if not re.match(r'^[A-Z]{3}-?\d{4}$|^[A-Z]{3}\d[A-Z]\d{2}$', value.upper()):
            raise serializers.ValidationError("Formato de placa inválido")
        return value.upper()


class FuncionarioSerializer(serializers.ModelSerializer):
    # Campos aninhados para leitura
    pessoa_nome = serializers.CharField(source='idPessFunc.nomePess', read_only=True)
    pessoa_email = serializers.CharField(source='idPessFunc.emailPess', read_only=True)
    pessoa_telefone = serializers.CharField(source='idPessFunc.telefonePess', read_only=True)
    departamento_nome = serializers.CharField(source='idDepaFunc.nomeDepa', read_only=True)
    cargo_nome = serializers.CharField(source='idCargFunc.nomeCarg', read_only=True)
    gestor_nome = serializers.CharField(source='gestor.idPessFunc.nomePess', read_only=True)
    
    # Para criação/edição, aceita apenas IDs
    idPessFunc = serializers.PrimaryKeyRelatedField(queryset=Pessoa.objects.all())
    
    class Meta:
        model = Funcionario
        fields = [
            'idFunc', 'idPessFunc', 'salarioFunc', 'comissaoFunc', 
            'dataAdmissaoFunc', 'idDepaFunc', 'idCargFunc', 'gestor', 'is_gestor',
            'pessoa_nome', 'pessoa_email', 'pessoa_telefone', 
            'departamento_nome', 'cargo_nome', 'gestor_nome'
        ]


class AssociadoSerializer(serializers.ModelSerializer):
    # Campos aninhados para leitura
    pessoa_nome = serializers.CharField(source='idPessAsso.nomePess', read_only=True)
    pessoa_email = serializers.CharField(source='idPessAsso.emailPess', read_only=True)
    pessoa_telefone = serializers.CharField(source='idPessAsso.telefonePess', read_only=True)
    plano_nome = serializers.CharField(source='idPlanAsso.nomePlan', read_only=True)
    consultor_nome = serializers.CharField(source='consultor.idPessFunc.nomePess', read_only=True)
    
    # Veículos do associado
    veiculos = VeiculoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Associado
        fields = [
            'idAsso', 'idPessAsso', 'dataAtivacaoAsso', 'dataPagamentoAsso',
            'idPlanAsso', 'consultor', 'pessoa_nome', 'pessoa_email',
            'pessoa_telefone', 'plano_nome', 'consultor_nome', 'veiculos'
        ]


class MensagemWhatsAppSerializer(serializers.ModelSerializer):
    associado_nome = serializers.CharField(source='associado.idPessAsso.nomePess', read_only=True)
    associado_telefone = serializers.CharField(source='associado.idPessAsso.telefonePess', read_only=True)
    
    class Meta:
        model = MensagemWhatsApp
        fields = [
            'idMensagem', 'associado', 'tipoMensagem', 'conteudo',
            'dataEnvio', 'status', 'associado_nome', 'associado_telefone'
        ]


# Serializers para criação completa (Pessoa + Funcionário/Associado em uma transação)
class FuncionarioCompletoSerializer(serializers.Serializer):
    # Dados da pessoa
    nomePess = serializers.CharField(max_length=255)
    telefonePess = serializers.CharField(max_length=20, required=False)
    documentoPess = serializers.CharField(max_length=30, required=False)
    nascimentoPess = serializers.DateField(required=False)
    emailPess = serializers.EmailField(required=False)
    usuarioPess = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    
    # Dados do funcionário
    salarioFunc = serializers.FloatField(required=False)
    comissaoFunc = serializers.FloatField(required=False)
    dataAdmissaoFunc = serializers.DateField(required=False)
    idDepaFunc = serializers.PrimaryKeyRelatedField(queryset=Departamento.objects.all(), required=False)
    idCargFunc = serializers.PrimaryKeyRelatedField(queryset=Cargo.objects.all(), required=False)
    gestor = serializers.PrimaryKeyRelatedField(queryset=Funcionario.objects.all(), required=False)
    is_gestor = serializers.BooleanField(default=False)
    
    def create(self, validated_data):
        from django.db import transaction
        
        # Separar dados da pessoa e do funcionário
        pessoa_data = {
            'nomePess': validated_data['nomePess'],
            'telefonePess': validated_data.get('telefonePess'),
            'documentoPess': validated_data.get('documentoPess'),
            'nascimentoPess': validated_data.get('nascimentoPess'),
            'emailPess': validated_data.get('emailPess'),
            'usuarioPess': validated_data['usuarioPess'],
            'is_staff': True  # Funcionários são staff
        }
        
        funcionario_data = {
            'salarioFunc': validated_data.get('salarioFunc'),
            'comissaoFunc': validated_data.get('comissaoFunc'),
            'dataAdmissaoFunc': validated_data.get('dataAdmissaoFunc'),
            'idDepaFunc': validated_data.get('idDepaFunc'),
            'idCargFunc': validated_data.get('idCargFunc'),
            'gestor': validated_data.get('gestor'),
            'is_gestor': validated_data.get('is_gestor', False)
        }
        
        # Criar em transação atômica
        with transaction.atomic():
            pessoa = Pessoa.objects.create_user(
                password=validated_data['password'],
                **pessoa_data
            )
            funcionario = Funcionario.objects.create(
                idPessFunc=pessoa,
                **funcionario_data
            )
            
        return funcionario


class AssociadoCompletoSerializer(serializers.Serializer):
    # Dados da pessoa
    nomePess = serializers.CharField(max_length=255)
    telefonePess = serializers.CharField(max_length=20, required=False)
    documentoPess = serializers.CharField(max_length=30, required=False)
    nascimentoPess = serializers.DateField(required=False)
    emailPess = serializers.EmailField(required=False)
    usuarioPess = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    
    # Dados do associado
    dataAtivacaoAsso = serializers.DateField(required=False)
    dataPagamentoAsso = serializers.DateField(required=False)
    idPlanAsso = serializers.PrimaryKeyRelatedField(queryset=Plano.objects.all(), required=False)
    consultor = serializers.PrimaryKeyRelatedField(queryset=Funcionario.objects.all(), required=False)
    
    def create(self, validated_data):
        from django.db import transaction
        
        # Separar dados da pessoa e do associado
        pessoa_data = {
            'nomePess': validated_data['nomePess'],
            'telefonePess': validated_data.get('telefonePess'),
            'documentoPess': validated_data.get('documentoPess'),
            'nascimentoPess': validated_data.get('nascimentoPess'),
            'emailPess': validated_data.get('emailPess'),
            'usuarioPess': validated_data['usuarioPess'],
            'is_staff': False  # Associados não são staff
        }
        
        associado_data = {
            'dataAtivacaoAsso': validated_data.get('dataAtivacaoAsso'),
            'dataPagamentoAsso': validated_data.get('dataPagamentoAsso'),
            'idPlanAsso': validated_data.get('idPlanAsso'),
            'consultor': validated_data.get('consultor')
        }
        
        # Criar em transação atômica
        with transaction.atomic():
            pessoa = Pessoa.objects.create_user(
                password=validated_data['password'],
                **pessoa_data
            )
            associado = Associado.objects.create(
                idPessAsso=pessoa,
                **associado_data
            )
            
        return associado