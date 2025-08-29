# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Clinica, Paciente, Cita, UserProfile
from datetime import datetime
import json

class MultiTenantCitasTestCase(TestCase):
    def setUp(self):
        """Configurar datos de prueba"""
        # Crear clínicas
        self.clinica_a = Clinica.objects.create(nombre='Clínica Nova', direccion='Miraflores')
        self.clinica_b = Clinica.objects.create(nombre='Bienestar Integral', direccion='Surco')
        
        # Crear usuarios
        self.admin_user = User.objects.create_user(
            username='admin', password='admin123', is_superuser=True, is_staff=True
        )
        self.user_clinica_a = User.objects.create_user(
            username='usuario_clinica_a', password='pass123', is_staff=True
        )
        self.user_clinica_b = User.objects.create_user(
            username='usuario_clinica_b', password='pass123', is_staff=True
        )
        self.user_paciente = User.objects.create_user(
            username='paciente_a', password='pass123'
        )
        
        # Crear perfiles de usuario (relación con clínicas)
        UserProfile.objects.create(user=self.admin_user, clinica=self.clinica_a)
        UserProfile.objects.create(user=self.admin_user, clinica=self.clinica_b)
        UserProfile.objects.create(user=self.user_clinica_a, clinica=self.clinica_a)
        UserProfile.objects.create(user=self.user_clinica_b, clinica=self.clinica_b)
        
        # Crear pacientes
        self.paciente_a = Paciente.objects.create(
            id=1, user=self.user_paciente, nombre='Ana', apellido='Pérez',
            fecha_nacimiento='1990-05-15', clinica=self.clinica_a
        )
        self.paciente_b = Paciente.objects.create(
            id=2, nombre='Juan', apellido='Gómez',
            fecha_nacimiento='1985-11-20', clinica=self.clinica_b
        )
        
        # Crear citas
        self.cita_a = Cita.objects.create(
            fecha_hora='2025-08-28 10:00:00', motivo='Consulta general',
            paciente=self.paciente_a, clinica=self.clinica_a
        )
        self.cita_b = Cita.objects.create(
            fecha_hora='2025-08-28 11:30:00', motivo='Revisión anual',
            paciente=self.paciente_b, clinica=self.clinica_b
        )
        
        self.client = Client()
    
    def test_clinic_isolation_get_citas(self):
        """Prueba que cada clínica solo vea sus propias citas (GET)"""
        # Usuario de Clínica A
        self.client.login(username='usuario_clinica_a', password='pass123')
        response = self.client.get('/api/citas/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Solo debe ver la cita de su clínica
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['citas'][0]['clinica']['id'], self.clinica_a.id)
        
        # Usuario de Clínica B
        self.client.login(username='usuario_clinica_b', password='pass123')
        response = self.client.get('/api/citas/')
        data = json.loads(response.content)
        
        # Solo debe ver la cita de su clínica
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['citas'][0]['clinica']['id'], self.clinica_b.id)
    
    def test_automatic_tenant_assignment_post_cita(self):
        """Prueba que las citas nuevas se asignen automáticamente al tenant del usuario (POST)"""
        self.client.login(username='usuario_clinica_a', password='pass123')
        
        cita_data = {
            'paciente_id': self.paciente_a.id,
            'clinica_id': self.clinica_a.id,
            'fecha_hora': '2025-08-29 14:00:00',
            'motivo': 'Nueva consulta'
        }
        
        response = self.client.post('/api/citas/create/', 
                                  json.dumps(cita_data), 
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Verificar que la cita se creó en la clínica correcta
        nueva_cita = Cita.objects.get(id=data['cita_id'])
        self.assertEqual(nueva_cita.clinica.id, self.clinica_a.id)
    
    def test_prevent_cross_tenant_access(self):
        """Prueba que no se pueda acceder a citas de otros tenants"""
        self.client.login(username='usuario_clinica_a', password='pass123')
        
        # Intentar acceder a una cita de la Clínica B
        response = self.client.get(f'/api/citas/{self.cita_b.id}/')
        self.assertEqual(response.status_code, 404)  # No debe encontrarla
        
        # Intentar actualizar una cita de la Clínica B
        update_data = {'estado': 'A'}
        response = self.client.put(f'/api/citas/{self.cita_b.id}/update/',
                                 json.dumps(update_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 404)  # No debe encontrarla
    
    def test_update_cita_tenant_isolation(self):
        """Prueba actualización de citas con aislamiento de tenant (PUT)"""
        self.client.login(username='usuario_clinica_a', password='pass123')
        
        # Actualizar cita propia
        update_data = {'estado': 'A', 'motivo': 'Consulta actualizada'}
        response = self.client.put(f'/api/citas/{self.cita_a.id}/update/',
                                 json.dumps(update_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Verificar que se actualizó
        cita_actualizada = Cita.objects.get(id=self.cita_a.id)
        self.assertEqual(cita_actualizada.estado, 'A')
        self.assertEqual(cita_actualizada.motivo, 'Consulta actualizada')
    
    def test_delete_cita_tenant_isolation(self):
        """Prueba eliminación de citas con aislamiento de tenant (DELETE)"""
        self.client.login(username='usuario_clinica_a', password='pass123')
        
        # Eliminar cita propia
        response = self.client.delete(f'/api/citas/{self.cita_a.id}/delete/')
        self.assertEqual(response.status_code, 200)
        
        # Verificar que se eliminó
        self.assertFalse(Cita.objects.filter(id=self.cita_a.id).exists())
        
        # Verificar que la cita de la otra clínica sigue existiendo
        self.assertTrue(Cita.objects.filter(id=self.cita_b.id).exists())
    
    def test_admin_can_see_all_citas(self):
        """Prueba que el admin pueda ver todas las citas"""
        self.client.login(username='admin', password='admin123')
        
        response = self.client.get('/api/citas/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # El admin debe ver todas las citas
        self.assertEqual(data['total'], 2)
    
    def test_pacientes_tenant_isolation(self):
        """Prueba aislamiento de pacientes por tenant"""
        self.client.login(username='usuario_clinica_a', password='pass123')
        
        response = self.client.get('/api/pacientes/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Solo debe ver pacientes de su clínica
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['pacientes'][0]['clinica']['id'], self.clinica_a.id)
    
    def test_clinicas_user_access(self):
        """Prueba que los usuarios solo vean sus clínicas asignadas"""
        self.client.login(username='usuario_clinica_a', password='pass123')
        
        response = self.client.get('/api/clinicas/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Solo debe ver su clínica
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['clinicas'][0]['id'], self.clinica_a.id)
    
    def test_prevent_unauthorized_clinic_access(self):
        """Prueba que no se pueda acceder a clínicas no autorizadas"""
        self.client.login(username='usuario_clinica_a', password='pass123')
        
        # Intentar acceder a los detalles de la Clínica B
        response = self.client.get(f'/api/clinicas/{self.clinica_b.id}/')
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_cita_creation_validation(self):
        """Prueba validación en creación de citas"""
        self.client.login(username='usuario_clinica_a', password='pass123')
        
        # Intentar crear cita con paciente de otra clínica
        cita_data = {
            'paciente_id': self.paciente_b.id,  # Paciente de Clínica B
            'clinica_id': self.clinica_a.id,
            'fecha_hora': '2025-08-29 14:00:00',
            'motivo': 'Consulta no autorizada'
        }
        
        response = self.client.post('/api/citas/create/',
                                  json.dumps(cita_data),
                                  content_type='application/json')
        
        # Debe fallar porque el paciente no pertenece a la clínica del usuario
        self.assertEqual(response.status_code, 404)

class TenantIsolationSummaryTest(TestCase):
    """Pruebas de resumen para verificar el entregable principal"""
    
    def setUp(self):
        # Configuración similar al test anterior
        self.clinica_a = Clinica.objects.create(nombre='Clínica Nova', direccion='Miraflores')
        self.clinica_b = Clinica.objects.create(nombre='Bienestar Integral', direccion='Surco')
        
        self.user_a = User.objects.create_user(username='user_a', password='pass123', is_staff=True)
        self.user_b = User.objects.create_user(username='user_b', password='pass123', is_staff=True)
        
        UserProfile.objects.create(user=self.user_a, clinica=self.clinica_a)
        UserProfile.objects.create(user=self.user_b, clinica=self.clinica_b)
        
        self.paciente_a = Paciente.objects.create(
            id=1, nombre='Ana', apellido='Pérez', clinica=self.clinica_a
        )
        self.paciente_b = Paciente.objects.create(
            id=2, nombre='Juan', apellido='Gómez', clinica=self.clinica_b
        )
        
        self.client = Client()
    
    def test_entregable_citas_no_se_mezclan(self):
        """👉 ENTREGABLE: Verificar que las citas de Clínica A no se mezclan con las de Clínica B"""
        
        # Crear citas para ambas clínicas
        self.client.login(username='user_a', password='pass123')
        cita_a_data = {
            'paciente_id': self.paciente_a.id,
            'clinica_id': self.clinica_a.id,
            'fecha_hora': '2025-08-29 10:00:00',
            'motivo': 'Cita Clínica A'
        }
        response_a = self.client.post('/api/citas/create/',
                                    json.dumps(cita_a_data),
                                    content_type='application/json')
        self.assertEqual(response_a.status_code, 201)
        
        self.client.login(username='user_b', password='pass123')
        cita_b_data = {
            'paciente_id': self.paciente_b.id,
            'clinica_id': self.clinica_b.id,
            'fecha_hora': '2025-08-29 11:00:00',
            'motivo': 'Cita Clínica B'
        }
        response_b = self.client.post('/api/citas/create/',
                                    json.dumps(cita_b_data),
                                    content_type='application/json')
        self.assertEqual(response_b.status_code, 201)
        
        # Verificar aislamiento: Usuario A solo ve citas de Clínica A
        self.client.login(username='user_a', password='pass123')
        response = self.client.get('/api/citas/')
        data_a = json.loads(response.content)
        
        self.assertEqual(data_a['total'], 1)
        self.assertEqual(data_a['citas'][0]['clinica']['nombre'], 'Clínica Nova')
        self.assertIn('Cita Clínica A', data_a['citas'][0]['motivo'])
        
        # Verificar aislamiento: Usuario B solo ve citas de Clínica B
        self.client.login(username='user_b', password='pass123')
        response = self.client.get('/api/citas/')
        data_b = json.loads(response.content)
        
        self.assertEqual(data_b['total'], 1)
        self.assertEqual(data_b['citas'][0]['clinica']['nombre'], 'Bienestar Integral')
        self.assertIn('Cita Clínica B', data_b['citas'][0]['motivo'])
        
        print("✅ ENTREGABLE CUMPLIDO: Las citas de Clínica A NO se mezclan con las de Clínica B")
        print(f"   - Usuario Clínica A ve {data_a['total']} cita(s) de su clínica")
        print(f"   - Usuario Clínica B ve {data_b['total']} cita(s) de su clínica")
        print("   - Aislamiento de tenants funcionando correctamente")
