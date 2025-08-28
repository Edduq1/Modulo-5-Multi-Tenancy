from django.db import models

# Create your models here.
from django.contrib.auth.models import User

# Este modelo representa las clínicas (inquilinos)
class Clinica(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'clinica'

# Este modelo representa a los pacientes y los conecta al modelo de usuario
class Paciente(models.Model):
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, db_column='clinica_id')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        db_table = 'paciente'

# Este modelo representa las citas
class Cita(models.Model):
    # Opciones de estado de la cita
    ESTADOS_CITA = [
        ('P', 'Pendiente'),
        ('A', 'Atendida'),
        ('C', 'Cancelada'),
    ]

    fecha_hora = models.DateTimeField()
    motivo = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=1, choices=ESTADOS_CITA, default='P')
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, db_column='paciente_id')
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, db_column='clinica_id')

    def __str__(self):
        return f"Cita de {self.paciente} el {self.fecha_hora}"
        
    class Meta:
        db_table = 'cita'

# Este modelo es para vincular a los usuarios con las clínicas
class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, db_column='clinica_id')

    def __str__(self):
        return f"{self.user.username} - {self.clinica.nombre}"

    class Meta:
        managed = False
        db_table = 'user_profile'
        unique_together = (('user', 'clinica'),)
