from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- Manager para o Modelo Pessoa (agora seu USER MODEL) ---
class PessoaManager(BaseUserManager):
    def create_user(self, usuarioPess, password=None, **extra_fields):
        if not usuarioPess:
            raise ValueError('O campo de usuário (usuarioPess) deve ser definido')
        user = self.model(usuarioPess=usuarioPess, **extra_fields)
        user.set_password(password) # Criptografa a senha
        user.save(using=self._db)
        return user

    def create_superuser(self, usuarioPess, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(usuarioPess, password, **extra_fields)

# --- Modelo Pessoa (Seu AUTH_USER_MODEL) ---
class Pessoa(AbstractBaseUser, PermissionsMixin):
    # Usando seu idPess SERIAL PRIMARY KEY do SQL
    idPess = models.AutoField(primary_key=True)
    nomePess = models.CharField(max_length=255)
    telefonePess = models.CharField(max_length=20, blank=True, null=True)
    documentoPess = models.CharField(max_length=30, unique=True, blank=True, null=True)
    nascimentoPess = models.DateField(null=True, blank=True)
    emailPess = models.EmailField(unique=True, blank=True, null=True) # Ainda pode ser único
    # senhaPess TEXT NOT NULL - O Django gerencia isso com o AbstractBaseUser, não defina aqui.
    usuarioPess = models.CharField(max_length=150, unique=True) # CAMPO DE LOGIN

    # Campos de permissão para AbstractBaseUser
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False) # Adicionado para corresponder ao DDL
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True) # Adicionado para corresponder ao DDL

    objects = PessoaManager()

    USERNAME_FIELD = 'usuarioPess' # AGORA O CAMPO DE LOGIN É 'usuarioPess'
    REQUIRED_FIELDS = ['nomePess', 'emailPess'] # Campos obrigatórios para createsuperuser (além do USERNAME_FIELD e password)

    # Relacionamento OneToOne com Endereco
    idEndePess = models.OneToOneField('Endereco', on_delete=models.SET_NULL, null=True, blank=True, db_column='idEndePess')

    def __str__(self):
        return self.usuarioPess

    class Meta:
        db_table = 'Pessoa' # Garante que o Django use o nome de tabela exato
        verbose_name_plural = "Pessoas"


class Endereco(models.Model):
    idEnde = models.AutoField(primary_key=True)
    cepEnde = models.CharField(max_length=10, blank=True, null=True) # Ajustado para CharField
    logadouroEnde = models.TextField()
    numeroEnde = models.CharField(max_length=10, blank=True, null=True) # Ajustado para CharField
    complementoEnde = models.TextField(blank=True, null=True)
    bairroEnde = models.TextField()
    cidadeEnde = models.TextField()

    def __str__(self):
        return f"{self.logadouroEnde}, {self.numeroEnde} - {self.cidadeEnde}"

    class Meta:
        db_table = 'Endereco'


class Departamento(models.Model):
    idDepa = models.AutoField(primary_key=True)
    nomeDepa = models.TextField(unique=True)

    def __str__(self):
        return self.nomeDepa

    class Meta:
        db_table = 'Departamento'


class Cargo(models.Model):
    idCarg = models.AutoField(primary_key=True)
    nomeCarg = models.TextField(unique=True)

    def __str__(self):
        return self.nomeCarg

    class Meta:
        db_table = 'Cargo'


class Plano(models.Model):
    idPlan = models.AutoField(primary_key=True)
    nomePlan = models.TextField(unique=True)

    def __str__(self):
        return self.nomePlan

    class Meta:
        db_table = 'Plano'


class Veiculo(models.Model):
    idVeic = models.AutoField(primary_key=True)
    nomeVeic = models.CharField(max_length=100)
    anoVeic = models.SmallIntegerField(null=True, blank=True)
    placaVeic = models.CharField(max_length=10, unique=True)
    # associado = models.ForeignKey('Associado', on_delete=models.CASCADE, related_name='veiculos') # Adicionar depois de definir Associado

    def __str__(self):
        return f"{self.placaVeic} ({self.nomeVeic})"

    class Meta:
        db_table = 'Veiculo'


class Funcionario(models.Model):
    idFunc = models.AutoField(primary_key=True)
    # Relacionamento de 1-para-1 com Pessoa (mas com sua própria PK)
    idPessFunc = models.OneToOneField(Pessoa, on_delete=models.CASCADE, db_column='idPessFunc')
    salarioFunc = models.FloatField(null=True, blank=True) # REAL no SQL
    comissaoFunc = models.FloatField(null=True, blank=True) # REAL no SQL
    dataAdmissaoFunc = models.DateField(null=True, blank=True)
    idDepaFunc = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True, db_column='idDepaFunc')
    idCargFunc = models.ForeignKey(Cargo, on_delete=models.SET_NULL, null=True, blank=True, db_column='idCargFunc')

    def __str__(self):
        return f"Funcionário: {self.idPessFunc.nomePess}" # Acesso via relacionamento

    class Meta:
        db_table = 'Funcionario'

# Sinal para criar Funcionario/Associado quando uma Pessoa é criada, se necessário
# @receiver(post_save, sender=Pessoa)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created and instance.is_staff: # Exemplo: se for staff, cria Funcionario
#         Funcionario.objects.create(idPessFunc=instance)
#     # if created and not instance.is_staff: # Exemplo: se não for staff, cria Associado
#     #     Associado.objects.create(idPessAsso=instance)


class Associado(models.Model):
    idAsso = models.AutoField(primary_key=True)
    idPessAsso = models.OneToOneField(Pessoa, on_delete=models.CASCADE, db_column='idPessAsso')
    dataAtivacaoAsso = models.DateField(null=True, blank=True)
    dataPagamentoAsso = models.DateField(null=True, blank=True)
    idPlanAsso = models.ForeignKey(Plano, on_delete=models.SET_NULL, null=True, blank=True, db_column='idPlanAsso')
    idVeicAsso = models.ForeignKey(Veiculo, on_delete=models.SET_NULL, null=True, blank=True, db_column='idVeicAsso') # Associa Veiculo ao Associado

    def __str__(self):
        return f"Associado: {self.idPessAsso.nomePess}"

    class Meta:
        db_table = 'Associado'

# Agora podemos adicionar o ForeignKey de Veiculo para Associado, já que Associado está definido.
# Se Veiculo for criado antes de Associado, pode dar erro de referência circular.
# Para evitar isso, pode-se usar uma string 'Associado' no ForeignKey, ou definir Veiculo depois.
# Ou usar o sinal post_save para criar veiculos se for o caso.
# Vou adicionar no modelo Veiculo uma linha de relacionamento comentado acima.
# Se precisar, descomente e faça um `makemigrations` e `migrate` novamente.