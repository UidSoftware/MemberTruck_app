from django.contrib import admin


# membertruck_app.admin.py
from django.contrib import admin
from .models import Pessoa, Endereco, Departamento, Cargo, Plano, Veiculo, Funcionario, Associado

admin.site.register(Pessoa)
admin.site.register(Endereco)
admin.site.register(Departamento)
admin.site.register(Cargo)
admin.site.register(Plano)
admin.site.register(Veiculo)
admin.site.register(Funcionario)
admin.site.register(Associado)