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

    # Serializer aninhado para o relacionamento OneToOne com Pessoa
    idPessFunc = PessoaSerializer(read_only=True) # Para leitura, mostra os detalhes da Pessoa
    # Para escrita, você provavelmente precisará de um campo Writable Nested ou lidar com isso na view/serializer
    # Ou, se você só passa o ID da Pessoa no POST/PUT, usaria:
    # idPessFunc_id = serializers.PrimaryKeyRelatedField(queryset=Pessoa.objects.all(), source='idPessFunc', write_only=True)

    # Para os relacionamentos ForeignKey (Departamento e Cargo), podemos usar:
    # 1. PrimaryKeyRelatedField (envia/recebe o ID) - MAIS COMUM PARA ESCRITA
    idDepaFunc = serializers.PrimaryKeyRelatedField(queryset=Departamento.objects.all(), source='idDepaFunc_id') # Adicionado _id
    idCargFunc = serializers.PrimaryKeyRelatedField(queryset=Cargo.objects.all(), source='idCargFunc_id') # Adicionado _id

    # 2. StringRelatedField (envia/recebe o __str__ do objeto, read-only) - BOM PARA LEITURA
    # idDepaFunc_nome = serializers.StringRelatedField(source='idDepaFunc.nomeDepa', read_only=True)
    # idCargFunc_nome = serializers.StringRelatedField(source='idCargFunc.nomeCarg', read_only=True)

    # --- NOVOS CAMPOS ---
    # Para o campo 'gestor' (auto-referência ForeignKey)
    # Ao criar/atualizar um consultor, você enviará o ID do gestor.
    # Ao listar, ele mostrará o ID do gestor.
    # Se quiser mais detalhes do gestor ao LISTAR, pode usar um Serializer aninhado ou StringRelatedField.
    gestor = serializers.PrimaryKeyRelatedField(queryset=Funcionario.objects.all(), allow_null=True)

    # Para o campo booleano 'is_gestor'
    is_gestor = serializers.BooleanField(required=False) # 'required=False' porque tem default=False no modelo


    class Meta:
        model = Funcionario
        fields = [
            'idFunc',
            'idPessFunc',
            # 'idPessFunc_id', # Se usar o campo write_only para idPessFunc
            'salarioFunc',
            'comissaoFunc',
            'dataAdmissaoFunc',
            'idDepaFunc',
            # 'idDepaFunc_nome', # Se usar
            'idCargFunc',
            # 'idCargFunc_nome', # Se usar
            'gestor', # Inclua o novo campo gestor
            'is_gestor' # Inclua o novo campo is_gestor
        ]
        read_only_fields = ('idFunc',) # O ID é gerado automaticamente

class AssociadoSerializer(serializers.ModelSerializer):
    # Serializa os dados da Pessoa vinculada
    pessoa_data = PessoaSerializer(source='idPessAsso', read_only=True)
    veiculo_data = VeiculoSerializer(source='idVeicAsso', read_only=True) # Dados do veículo

    class Meta:
        model = Associado
        fields = '__all__'
        read_only_fields = ('idAsso',)