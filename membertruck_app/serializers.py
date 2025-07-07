from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Pessoa, Endereco, Departamento, Cargo, Plano, Veiculo, Funcionario, Associado

# Custom serializer para login usando 'usuarioPess'
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'usuarioPess' # <--- ISSO DIZ AO JWT PARA USAR O CAMPO 'usuarioPess' COMO USERNAME

class PessoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pessoa
        fields = '__all__' # Inclui todos os campos do modelo
        extra_kwargs = {
            'password': {'write_only': True}, # Permite escrever, mas não ler (não aparece no GET)
            'is_superuser': {'read_only': True}, # Apenas leitura
            'is_staff': {'read_only': True}, # Apenas leitura
            'is_active': {'read_only': True}, # Apenas leitura
            'date_joined': {'read_only': True}, # Apenas leitura
            'last_login': {'read_only': True}, # Apenas leitura
            # 'groups': {'read_only': True}, # Se você quiser esconder grupos e permissões também
            # 'user_permissions': {'read_only': True},
        }

    # Ele garante que o serializer saiba como criar o objeto Pessoa corretamente.
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Pessoa.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    

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