from django.contrib import admin

# Register your models here.
from .models import Clinica, Paciente, Cita, UserProfile
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Filtro lateral que solo muestra las clínicas a las que el usuario tiene acceso
class ClinicaByUserFilter(admin.SimpleListFilter):
    title = 'clinica'
    parameter_name = 'clinica'

    def lookups(self, request, model_admin):
        ids = UserProfile.objects.filter(user=request.user).values_list('clinica', flat=True)
        return [(c.id, c.nombre) for c in Clinica.objects.filter(id__in=ids)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(clinica_id=self.value())
        return queryset

# Admin simplificado para Pacientes
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'clinica')
    list_filter = (ClinicaByUserFilter,)
    search_fields = ('nombre', 'apellido')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Filtrar por clínicas del usuario
        user_clinicas = UserProfile.objects.filter(user=request.user).values_list('clinica', flat=True)
        return qs.filter(clinica__in=user_clinicas)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "clinica" and not request.user.is_superuser:
            user_clinicas = UserProfile.objects.filter(user=request.user).values_list('clinica', flat=True)
            kwargs["queryset"] = Clinica.objects.filter(id__in=user_clinicas)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Admin simplificado para Citas
class CitaAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'clinica', 'fecha_hora', 'estado')
    list_filter = (ClinicaByUserFilter, 'estado')
    search_fields = ('motivo',)
    ordering = ('-fecha_hora',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Filtrar por clínicas del usuario
        user_clinicas = UserProfile.objects.filter(user=request.user).values_list('clinica', flat=True)
        return qs.filter(clinica__in=user_clinicas)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "clinica" and not request.user.is_superuser:
            user_clinicas = UserProfile.objects.filter(user=request.user).values_list('clinica', flat=True)
            kwargs["queryset"] = Clinica.objects.filter(id__in=user_clinicas)
        elif db_field.name == "paciente" and not request.user.is_superuser:
            user_clinicas = UserProfile.objects.filter(user=request.user).values_list('clinica', flat=True)
            kwargs["queryset"] = Paciente.objects.filter(clinica__in=user_clinicas)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # Para usuarios no superusuarios, forzar que la clínica de la cita sea la del paciente
        if not request.user.is_superuser and obj.paciente_id:
            obj.clinica = obj.paciente.clinica
        # Validación de coherencia para todos: paciente y clínica deben coincidir
        if obj.paciente_id and obj.clinica_id and obj.paciente.clinica_id != obj.clinica_id:
            raise ValidationError("La clínica de la cita debe coincidir con la clínica del paciente.")
        super().save_model(request, obj, form, change)

# Admin simplificado para Clinicas
class ClinicaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'direccion')
    search_fields = ('nombre',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Filtrar por clínicas del usuario
        user_clinicas = UserProfile.objects.filter(user=request.user).values_list('clinica', flat=True)
        return qs.filter(id__in=user_clinicas)
    
    def has_add_permission(self, request):
        # Solo superusuarios pueden crear clínicas
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        # Solo superusuarios pueden eliminar clínicas
        return request.user.is_superuser

# Admin simplificado para UserProfile
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'clinica')
    list_filter = ('clinica',)
    raw_id_fields = ('user', 'clinica')

# Registramos los modelos con configuración básica
admin.site.register(Clinica, ClinicaAdmin)
admin.site.register(Paciente, PacienteAdmin)
admin.site.register(Cita, CitaAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
