from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

# --- Manager para o Modelo Pessoa (agora seu USER MODEL) ---
class PessoaManager(BaseUserManager):
    def create_user(self, usuarioPess, password=None, **extra_fields):
        if not usuarioPess:
            raise ValueError('O campo de usuário (usuarioPess) deve ser definido')
        user = self.model(usuarioPess=usuarioPess, **extra_fields)
        user.set_password(password)  # Criptografa a senha
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
    idPess = models.AutoField(primary_key=True)
    nomePess = models.CharField(max_length=255)
    telefonePess = models.CharField(max_length=20, blank=True, null=True)
    documentoPess = models.CharField(max_length=30, unique=True, blank=True, null=True)
    nascimentoPess = models.DateField(null=True, blank=True)
    emailPess = models.EmailField(unique=True, blank=True, null=True)
    usuarioPess = models.CharField(max_length=150, unique=True)  # CAMPO DE LOGIN

    # Campos de permissão para AbstractBaseUser
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    # Relacionamento com Endereco
    idEndePess = models.OneToOneField(
        'Endereco', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        db_column='idEndePess'
    )

    objects = PessoaManager()

    USERNAME_FIELD = 'usuarioPess'
    REQUIRED_FIELDS = ['nomePess', 'emailPess']

    def __str__(self):
        return self.usuarioPess

    class Meta:
        db_table = 'Pessoa'
        verbose_name_plural = "Pessoas"


class Endereco(models.Model):
    idEnde = models.AutoField(primary_key=True)
    cepEnde = models.CharField(max_length=10, blank=True, null=True)
    logadouroEnde = models.TextField()
    numeroEnde = models.CharField(max_length=10, blank=True, null=True)
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


class Funcionario(models.Model):
    idFunc = models.AutoField(primary_key=True)
    idPessFunc = models.OneToOneField(
        Pessoa, 
        on_delete=models.CASCADE, 
        db_column='idPessFunc'
    )
    salarioFunc = models.FloatField(null=True, blank=True)
    comissaoFunc = models.FloatField(null=True, blank=True)
    dataAdmissaoFunc = models.DateField(null=True, blank=True)
    idDepaFunc = models.ForeignKey(
        Departamento, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        db_column='idDepaFunc'
    )
    idCargFunc = models.ForeignKey(
        Cargo, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        db_column='idCargFunc'
    )

    # Relacionamento gestor-consultor
    gestor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultores'
    )
    
    # Identificar se é gestor
    is_gestor = models.BooleanField(default=False)

    def __str__(self):
        return f"Funcionário: {self.idPessFunc.nomePess}"

    class Meta:
        db_table = 'Funcionario'


class Associado(models.Model):
    idAsso = models.AutoField(primary_key=True)
    idPessAsso = models.OneToOneField(
        Pessoa, 
        on_delete=models.CASCADE, 
        db_column='idPessAsso'
    )
    dataAtivacaoAsso = models.DateField(null=True, blank=True)
    dataPagamentoAsso = models.DateField(null=True, blank=True)
    idPlanAsso = models.ForeignKey(
        Plano, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        db_column='idPlanAsso'
    )
    
    # Relacionamento com consultor (quem indicou)
    consultor = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='associados_indicados',
        limit_choices_to={'is_gestor': False}  # Apenas consultores, não gestores
    )

    def __str__(self):
        return f"Associado: {self.idPessAsso.nomePess}"

    class Meta:
        db_table = 'Associado'


# CORREÇÃO: Veiculo pertence a Associado (1 para muitos)
class Veiculo(models.Model):
    idVeic = models.AutoField(primary_key=True)
    nomeVeic = models.CharField(max_length=100)
    anoVeic = models.SmallIntegerField(null=True, blank=True)
    placaVeic = models.CharField(max_length=10, unique=True)
    
    # Um veículo pertence a um associado, um associado pode ter vários veículos
    associado = models.ForeignKey(
        Associado,
        on_delete=models.CASCADE,
        related_name='veiculos'  # associado.veiculos.all()
    )

    def __str__(self):
        return f"{self.placaVeic} ({self.nomeVeic})"

    class Meta:
        db_table = 'Veiculo'


# Modelo para histórico de mensagens WhatsApp (adicional)
class MensagemWhatsApp(models.Model):
    TIPO_CHOICES = [
        ('cobranca', 'Cobrança'),
        ('comemorativa', 'Comemorativa'),
        ('promocional', 'Promocional'),
    ]
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('enviada', 'Enviada'),
        ('erro', 'Erro'),
    ]
    
    idMensagem = models.AutoField(primary_key=True)
    associado = models.ForeignKey(
        Associado,
        on_delete=models.CASCADE,
        related_name='mensagens'
    )
    tipoMensagem = models.CharField(max_length=20, choices=TIPO_CHOICES)
    conteudo = models.TextField()
    dataEnvio = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    
    def __str__(self):
        return f"Mensagem {self.tipoMensagem} para {self.associado.idPessAsso.nomePess}"
    
    class Meta:
        db_table = 'MensagemWhatsApp'
        verbose_name = "Mensagem WhatsApp"
        verbose_name_plural = "Mensagens WhatsApp"