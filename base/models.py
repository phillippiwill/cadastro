from django.db import models # type: ignore
from multi_email_field.fields import MultiEmailField


class Estado(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Municipio(models.Model):
    nome = models.CharField(max_length=100)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nome} - {self.estado.nome}"

class Interesse(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Partido(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    
class Cargo(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome    


class Contato(models.Model):
    nome = models.CharField(max_length=100)
    cargo = models.ForeignKey(Cargo, on_delete=models.SET_NULL, null=True)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True)
    municipio = models.ForeignKey(Municipio, on_delete=models.SET_NULL, null=True)
    observacoes = models.TextField(blank=True, null=True)  # Campo para observações
    foto = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)  # Campo para upload de fotos
    interesses = models.ManyToManyField('Interesse', blank=True)
    entidade = models.CharField(max_length=100, blank=True)  
    partido = models.ForeignKey(Partido, on_delete=models.SET_NULL, null=True, blank=True) 

    def __str__(self):
        return f"{self.nome} - {self.cargo}"
    
class Email(models.Model):
    contact = models.ForeignKey(Contato, related_name='emails', on_delete=models.CASCADE)
    email = models.EmailField()

    def __str__(self):
        return self.email

class Telephone(models.Model):
    contact = models.ForeignKey(Contato, related_name='telephones', on_delete=models.CASCADE)
    telephone = models.CharField(max_length=15)  # Adjust the max_length as needed

    def __str__(self):
        return self.telephone
