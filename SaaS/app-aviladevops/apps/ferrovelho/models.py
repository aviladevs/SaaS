from django.db import models

# Modelos básicos para o app ferrovelho
class Material(models.Model):
    nome = models.CharField(max_length=100)
    preco_kg = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __str__(self):
        return self.nome