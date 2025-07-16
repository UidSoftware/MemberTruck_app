from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Pessoa, Endereco, Departamento, Cargo, Plano, Veiculo, Funcionario, Associado

# Custom serializer para login usando 'usuarioPess'
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'usuarioPess' # ISSO DIZ AO JWT PARA USAR O CAMPO 'usuarioPess' COMO USERNAME

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
    # Se você quiser que o Associado seja aninhado ao criar/atualizar um Veiculo,
    # precisaria de um AssociadoSerializer aqui e métodos create/update no VeiculoSerializer.
    # Por enquanto, assumimos que idAssoVeic é um PrimaryKeyRelatedField para escrita.
    associado = serializers.PrimaryKeyRelatedField(queryset=Associado.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Veiculo
        fields = '__all__'

class PessoaSerializer(serializers.ModelSerializer):
    # Campo de senha para criação/atualização (write_only para não ser lido)
    password = serializers.CharField(write_only=True)
    
    # Se você quiser que o Endereco seja aninhado para criação/atualização de Pessoa,
    # descomente a linha abaixo e adicione a lógica no create/update.
    # Por agora, assumimos que idEndePess é um PrimaryKeyRelatedField ou que o Endereco é criado separadamente.
    # idEndePess = EnderecoSerializer(required=False, allow_null=True)


    class Meta:
        model = Pessoa
        fields = [
            'idPess', 'nomePess', 'telefonePess', 'documentoPess', 'nascimentoPess',
            'emailPess', 'usuarioPess', 'password', 'is_staff', 'is_active',
            'is_superuser', 'date_joined', 'last_login', 'idEndePess' # Inclua idEndePess
        ]
        read_only_fields = ['idPess', 'date_joined', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_superuser': {'read_only': True},
            'is_staff': {'read_only': True},
            'is_active': {'read_only': True},
        }

    def create(self, validated_data):
        # O password é passado para o create_user do manager, que o remove de validated_data
        # e o usa para set_password.
        # Se Endereco for aninhado, você precisaria extraí-lo aqui antes de Pessoa.objects.create_user
        # endereco_data = validated_data.pop('idEndePess', None)
        user = Pessoa.objects.create_user(**validated_data)
        # if endereco_data:
        #     endereco_instance = Endereco.objects.create(**endereco_data)
        #     user.idEndePess = endereco_instance
        #     user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        # endereco_data = validated_data.pop('idEndePess', None) # Se Endereco for aninhado

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        
        instance.save()
        
        # if endereco_data and instance.idEndePess: # Se Endereco for aninhado e já existir
        #     endereco_serializer = EnderecoSerializer()
        #     endereco_serializer.update(instance.idEndePess, endereco_data)
        # elif endereco_data and not instance.idEndePess: # Se Endereco for aninhado e não existir
        #     endereco_instance = Endereco.objects.create(**endereco_data)
        #     instance.idEndePess = endereco_instance
        #     instance.save()
        return instance


class FuncionarioSerializer(serializers.ModelSerializer):
    # Usamos o PessoaSerializer diretamente para o campo idPessFunc
    # Isso permite que os dados da Pessoa sejam aninhados e criados/atualizados
    idPessFunc = PessoaSerializer() # Removido read_only=True para permitir escrita

    # Para os relacionamentos ForeignKey (Departamento e Cargo), usamos PrimaryKeyRelatedField
    # sem o argumento 'source' se o nome do campo no serializer é o mesmo do modelo.
    idDepaFunc = serializers.PrimaryKeyRelatedField(queryset=Departamento.objects.all())
    idCargFunc = serializers.PrimaryKeyRelatedField(queryset=Cargo.objects.all())

    # Campo 'gestor' (auto-referência ForeignKey)
    gestor = serializers.PrimaryKeyRelatedField(queryset=Funcionario.objects.all(), allow_null=True, required=False) # required=False para permitir que seja nulo

    # Campo booleano 'is_gestor'
    is_gestor = serializers.BooleanField(required=False)

    class Meta:
        model = Funcionario
        fields = [
            'idFunc', 'idPessFunc', 'salarioFunc', 'comissaoFunc',
            'dataAdmissaoFunc', 'idDepaFunc', 'idCargFunc',
            'gestor', 'is_gestor'
        ]
        read_only_fields = ('idFunc',) # idFunc é auto-gerado

    def create(self, validated_data):
        # Extrai os dados da Pessoa aninhados
        pessoa_data = validated_data.pop('idPessFunc')

        # Cria a instância de Pessoa usando o PessoaSerializer
        # O PessoaSerializer.create já lida com o password e o salvamento
        pessoa_instance = PessoaSerializer().create(pessoa_data)

        # Cria a instância de Funcionario, vinculando à Pessoa recém-criada
        funcionario = Funcionario.objects.create(idPessFunc=pessoa_instance, **validated_data)
        return funcionario

    def update(self, instance, validated_data):
        # Extrai os dados da Pessoa aninhados, se existirem
        pessoa_data = validated_data.pop('idPessFunc', {})

        # Atualiza a instância de Pessoa vinculada
        pessoa_instance = instance.idPessFunc
        pessoa_serializer = PessoaSerializer()
        pessoa_serializer.update(pessoa_instance, pessoa_data)

        # Atualiza os outros campos da instância de Funcionario
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class AssociadoSerializer(serializers.ModelSerializer):
    # Usamos o PessoaSerializer diretamente para o campo idPessAsso
    idPessAsso = PessoaSerializer()

    # Para o relacionamento ForeignKey com Veiculo
    # idVeicAsso = serializers.PrimaryKeyRelatedField(queryset=Veiculo.objects.all(), allow_null=True, required=False)
    # Ou, se você quiser aninhar dados do Veiculo para criação/atualização do Associado:
    idVeicAsso = VeiculoSerializer(required=False, allow_null=True) # Assumindo que Veiculo pode ser criado/atualizado junto

    class Meta:
        model = Associado
        fields = '__all__'
        read_only_fields = ('idAsso',)

    def create(self, validated_data):
        pessoa_data = validated_data.pop('idPessAsso')
        veiculo_data = validated_data.pop('idVeicAsso', None)

        pessoa_instance = PessoaSerializer().create(pessoa_data)
        
        associado = Associado.objects.create(idPessAsso=pessoa_instance, **validated_data)

        if veiculo_data:
            # Se Veiculo for aninhado e você quiser criá-lo aqui
            # Certifique-se de que o VeiculoSerializer lida com a FK 'associado'
            # ou atribua o associado_id aqui
            veiculo_data['associado'] = associado.idAsso # Vincula o veículo ao associado recém-criado
            VeiculoSerializer().create(veiculo_data)
        
        return associado

    def update(self, instance, validated_data):
        pessoa_data = validated_data.pop('idPessAsso', {})
        veiculo_data = validated_data.pop('idVeicAsso', None)

        # Atualiza Pessoa
        pessoa_serializer = PessoaSerializer()
        pessoa_serializer.update(instance.idPessAsso, pessoa_data)

        # Atualiza ou cria Veiculo
        if veiculo_data:
            if instance.idVeicAsso: # Se já tem um veículo, atualiza
                veiculo_serializer = VeiculoSerializer()
                veiculo_serializer.update(instance.idVeicAsso, veiculo_data)
            else: # Se não tem, cria um novo e associa
                veiculo_data['associado'] = instance.idAsso # Vincula o veículo ao associado
                VeiculoSerializer().create(veiculo_data)
        
        # Atualiza os outros campos do Associado
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
