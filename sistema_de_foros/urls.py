from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from foros import views

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),

    # ---------- Login/Signup/Logout ----------    
    path('', views.mostrarIndex, name='index'),
    path('login/', views.mostrarLogin, name='login'),
    path('form_login/', views.formLogin, name='form_login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.mostrarSignup, name='signup'),
    path('form_signup/', views.formSignup, name='form_signup'),
    
    # ---------- Manejo de Usuarios ----------    
    path('perfil_usuario/<int:id>/', views.mostrarPerfilUsuario, name='perfil_usuario'),
    path('editar_usuario/<int:id>', views.mostrarEditarPerfilUsuario, name='editar_usuario'),
    path('form_editar_usuario/<int:id>', views.formEditarPerfilUsuario, name='form_editar_usuario'),
    path('gestionar_usuarios/', views.mostrarGestionarUsuarios, name='gestionar_usuarios'),
    path('deshabilitar_usuario/<int:id>/', views.deshabilitar_usuario, name='deshabilitar_usuario'),
    path('habilitar_usuario/<int:id>/', views.habilitar_usuario, name='habilitar_usuario'),

    
    # ---------- Manejo de Tematicas ----------    
    path('administrar_tematicas/', views.mostrarAdministrarTematicas, name='administrar_tematicas'),
    path('crear_tematica/', views.mostrarCrearTematica, name='crear_tematica'),
    path('form_crear_tematica/', views.formCrearTematica, name='form_crear_tematica'),
    path('editar_tematica/<int:id>', views.mostrarEditarTematica, name='editar_tematica'),
    path('form_editar_tematica/<int:id>', views.formEditarTematica, name='form_editar_tematica'),
    path('eliminar_tematica/<int:id>', views.eliminarTematica, name='eliminar_tematica'),
    
    # ---------- Manejo de Foros ----------    
    path('foro/<int:foro_id>', views.mostrarForo, name='foro'),
    path('crear_foro/', views.mostrarCrearForo, name='crear_foro'),
    path('form_crear_foro/', views.formCrearForo, name='form_crear_foro'),
    path('editar_foro/<int:id>', views.mostrarEditarForo, name='editar_foro'),
    path('form_editar_foro/<int:id>', views.formEditarForo, name='form_editar_foro'),
    path('administrar_foros/', views.mostrarAdministrarForos, name='administrar_foros'),
    path('eliminar_foro/<int:id>', views.eliminarForo, name='eliminar_foro'),
    path('explorar_foros/', views.explorarForos, name='explorar_foros'),
    
    # ---------- Manejo de Publicaciones ----------    
    path('foro/<int:foro_id>/crear_publicacion', views.mostrarCrearPublicacion, name='crear_publicacion'),
    path('foro/<int:foro_id>/form_crear_publicacion', views.formCrearPublicacion, name='form_crear_publicacion'),
    path('foro/<int:foro_id>/editar_publicacion/<int:publicacion_id>', views.mostrarEditarPublicacion, name='editar_publicacion'),
    path('foro/<int:foro_id>/form_editar_publicacion/<int:publicacion_id>', views.formEditarPublicacion, name='form_editar_publicacion'),
    path('foro/<int:foro_id>/publicacion/<int:publicacion_id>', views.mostrarPublicacion, name='mostrar_publicacion'),
    path('foro/<int:foro_id>/eliminar_publicacion/<int:publicacion_id>', views.eliminarPublicacion, name='eliminar_publicacion'),
    
    
    # ---------- Manejo de Respuestas ----------    
    path('foro/<int:foro_id>/publicacion/<int:publicacion_id>/form_crear_respuesta', views.formCrearRespuesta, name='form_crear_respuesta'),
    path('foro/<int:foro_id>/publicacion/<int:publicacion_id>/editar_respuesta/<int:respuesta_id>/', views.mostrarEditarRespuesta, name='editar_respuesta'),
    path('foro/<int:foro_id>/publicacion/<int:publicacion_id>/form_editar_respuesta/<int:respuesta_id>/', views.formEditarRespuesta, name='form_editar_respuesta'),
    path('foro/<int:foro_id>/publicacion/<int:publicacion_id>/eliminar_respuesta/<int:respuesta_id>/', views.eliminarRespuesta, name='eliminar_respuesta'),
    
    # ---------- Manejo de Historial de Acciones ----------    
    path('historial_acciones/', views.mostrarHistorialAcciones, name='historial_acciones'),
    
    # ---------- Manejo de Acceso Denegado ----------    
    path('acceso_denegado/', views.accesoDenegado, name='acceso_denegado'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)