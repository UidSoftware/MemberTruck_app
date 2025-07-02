from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Pessoa, Endereco, Departamento, Cargo, Plano, Veiculo, Funcionario, Associado

# Custom serializer para login usando 'usuarioPess'
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'usuarioPess' # <--- ISSO DIZ AO JWT PARA USAR O CAMPO 'usuarioPess' COMO USERNAME

class PessoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pessoa
        # Excluir 'password' para não expor em listagens/detalhes
        exclude = ('password', 'is_superuser', 'last_login', 'date_joined', 'groups', 'user_permissions')
        read_only_fields = ('idPess',) # O ID é gerado automaticamente
        # No caso de criação de pessoa, você pode querer um serializer separado ou ajustar este
        # para lidar com a senha de forma segura (write_only).
        # Para criação de usuário:
        # extra_kwargs = {'password': {'write_only': True}}
        # def create(self, validated_data):
        #     user = Pessoa.objects.create_user(**validated_data)
        #     return user

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
    class Meta:
        model = Veiculo
        fields = '__all__'

class FuncionarioSerializer(serializers.ModelSerializer):
    # Serializa os dados da Pessoa vinculada
    pessoa_data = PessoaSerializer(source='idPessFunc', read_only=True)

    class Meta:
        model = Funcionario
        fields = '__all__' # Incluirá todos os campos de Funcionario e o relacionamento idPessFunc
        read_only_fields = ('idFunc',) # O ID é gerado automaticamente

class AssociadoSerializer(serializers.ModelSerializer):
    # Serializa os dados da Pessoa vinculada
    pessoa_data = PessoaSerializer(source='idPessAsso', read_only=True)
    veiculo_data = VeiculoSerializer(source='idVeicAsso', read_only=True) # Dados do veículo

    class Meta:
        model = Associado
        fields = '__all__'
        read_only_fields = ('idAsso',)