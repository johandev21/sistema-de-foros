from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from functools import wraps
from datetime import datetime
from .models import (
    Usuario,
    Tematica,
    Foro,
    Publicacion,
    Historial,
    Respuesta,
    Palabrotas,
)
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password


# Decoradores
def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("estadoSesion"):
            return redirect("login")
        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("estadoSesion"):
            return redirect("login")
        if request.session.get("tipUsuario") != "Admin":
            return redirect("acceso_denegado")
        return view_func(request, *args, **kwargs)

    return wrapper


# Utilidades
def get_session_data(request):
    usuario_id = request.session.get("idUsuario")
    usuario = Usuario.objects.filter(id=usuario_id).first()
    return {
        "idUsuario": usuario_id,
        "nomUsuario": request.session.get("nomUsuario"),
        "tipUsuario": request.session.get("tipUsuario"),
        "fotoUsuario": (
            usuario.foto.url
            if usuario and usuario.foto
            else default_storage.url("imagenes/default-profile.png")
        ),
    }


def contiene_palabrotas(texto):
    palabras_prohibidas = Palabrotas.objects.values_list("palabra", flat=True)
    for palabra in palabras_prohibidas:
        if palabra.lower() in texto.lower():
            return True
    return False


def registrar_historial(accion, usuario_id):
    Historial.objects.create(accion=accion, fecha=datetime.now(), usuario_id=usuario_id)


def verificar_si_existe(clase, campo, valor):
    return clase.objects.filter(**{campo: valor}).exists()


def obtener_usuario(request):
    usuario_id = request.session.get("idUsuario")
    return get_object_or_404(Usuario, id=usuario_id)


# Views
@login_required
def mostrarIndex(request):
    publicaciones = Publicacion.objects.all().order_by("-fecha")
    datos = get_session_data(request)
    datos["publicaciones"] = publicaciones
    return render(request, "index.html", datos)


def mostrarLogin(request):
    return render(request, "login.html")


def formLogin(request):
    rut = request.POST.get("txtrut")
    pas = request.POST.get("txtpas")

    try:
        usuario = Usuario.objects.get(rut=rut)
    except Usuario.DoesNotExist:
        return render(
            request, "login.html", {"mensaje_error": "Usuario o contraseña incorrectos."}
        )

    if usuario.estado in ["Deshabilitado", "Suspendido"]:
        mensaje_error = (
            "Su cuenta está deshabilitada."
            if usuario.estado == "Deshabilitado"
            else "Su cuenta está suspendida."
        )
        return render(request, "login.html", {"mensaje_error": mensaje_error})

    if check_password(pas, usuario.contrasena):
        usuario.intentos_fallidos = 0
        usuario.save()

        request.session["estadoSesion"] = True
        request.session["idUsuario"] = usuario.id
        request.session["nomUsuario"] = usuario.nombres
        request.session["tipUsuario"] = usuario.tipo_usuario

        registrar_historial("Inicia sesión", usuario.id)
        return redirect("index")
    else:
        usuario.intentos_fallidos += 1
        usuario.save()

        if usuario.tipo_usuario != "Admin" and usuario.intentos_fallidos >= 3:
            usuario.estado = "Deshabilitado"
            usuario.save()
            registrar_historial(
                "Usuario deshabilitado por múltiples intentos fallidos", usuario.id
            )
            mensaje_error = (
                "Su cuenta ha sido deshabilitada por múltiples intentos fallidos."
            )
        elif usuario.tipo_usuario == "Admin":
            mensaje_error = (
                "Contraseña incorrecta. Los administradores no se pueden deshabilitar."
            )
        else:
            intentos_restantes = 3 - usuario.intentos_fallidos
            mensaje_error = (
                f"Contraseña incorrecta. Intentos restantes: {intentos_restantes}"
            )

        if usuario.tipo_usuario != "Admin" and usuario.intentos_fallidos < 3:
             return render(request, "login.html", {"mensaje_error": mensaje_error})
        elif usuario.tipo_usuario == "Admin":
             return render(request, "login.html", {"mensaje_error": mensaje_error})
        else:
             return render(request, "login.html", {"mensaje_error": mensaje_error})

def mostrarSignup(request):
    return render(request, "signup.html")


def formSignup(request):
    rut_usu = request.POST.get("txtrut")
    nom_usu = request.POST.get("txtnom")
    apem_usu = request.POST.get("txtapem")
    apep_usu = request.POST.get("txtapep")
    ema_usu = request.POST.get("txtema")
    nac_usu = request.POST.get("txtnac")
    pas_usu = request.POST.get("txtpas")
    pas2_usu = request.POST.get("txtpas2")

    errores = {}

    if pas_usu != pas2_usu:
        errores["contraseña"] = "Las contraseñas no coinciden."

    if verificar_si_existe(Usuario, "rut", rut_usu):
        errores["rut"] = f"El rut: {rut_usu} ya existe."

    if verificar_si_existe(Usuario, "correo", ema_usu):
        errores["correo"] = f"El correo: {ema_usu} ya existe."

    if errores:
        datos = {
            'errores': errores,
            'data': request.POST
        }
        return render(request, "signup.html", datos)

    try:
        hashed_password = make_password(pas_usu)

        usuario = Usuario.objects.create(
            rut=rut_usu,
            nombres=nom_usu,
            paterno=apep_usu,
            materno=apem_usu,
            correo=ema_usu,
            nacionalidad=nac_usu,
            contrasena=hashed_password,
        )

        registrar_historial("Registro de usuario", usuario.id)

        return redirect("login")

    except Exception as e:
        errores["db_error"] = f"Error al crear el usuario: {str(e)}"
        datos = {
            'errores': errores,
            'data': request.POST
        }
        return render(request, "signup.html", datos)

def logout(request):
    registrar_historial("Cierre sesión", request.session.get("idUsuario"))
    request.session.flush()
    return redirect("login")


@login_required
def mostrarPerfilUsuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    datos = {"usuario": usuario}
    datos.update(get_session_data(request))
    return render(request, "perfil_usuario.html", datos)


@login_required
def mostrarEditarPerfilUsuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    idUsuario = request.session.get("idUsuario")
    tipUsuario = request.session.get("tipUsuario")

    if tipUsuario != "Admin" and idUsuario != usuario.id:
        return redirect("acceso_denegado")

    datos = {"usuario": usuario}
    datos.update(get_session_data(request))
    return render(request, "editar_perfil_usuario.html", datos)


@login_required
def formEditarPerfilUsuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    idUsuario = request.session.get("idUsuario")
    tipUsuario = request.session.get("tipUsuario")

    if tipUsuario != "Admin" and idUsuario != usuario.id:
        return redirect("acceso_denegado")

    errores = {}
    
    form_data = {
        'txtnom': usuario.nombres,
        'txtapem': usuario.materno,
        'txtapep': usuario.paterno,
        'txtnac': usuario.nacionalidad,
    }

    if request.method == "POST":
        form_data = request.POST.copy() 

        nom_usu = request.POST.get("txtnom")
        apem_usu = request.POST.get("txtapem")
        apep_usu = request.POST.get("txtapep")
        nac_usu = request.POST.get("txtnac")
        pas_usu = request.POST.get("txtpas")
        pas2_usu = request.POST.get("txtpas2")
        foto = request.FILES.get("foto")

        if pas_usu or pas2_usu:
            if pas_usu != pas2_usu:
                errores["contraseña"] = "Las contraseñas no coinciden."
            else:
                usuario.contrasena = make_password(pas_usu)
        
        usuario.nombres = nom_usu
        usuario.materno = apem_usu
        usuario.paterno = apep_usu
        usuario.nacionalidad = nac_usu
        
        if foto:
            if usuario.foto:
                usuario.foto.delete(save=False)
            usuario.foto = foto

        if not errores:
            try:
                usuario.save()
                registrar_historial("Edición perfil", idUsuario)
                return redirect("perfil_usuario", id=usuario.id)
            except Exception as e:
                errores["db_error"] = f"Error al actualizar el usuario: {str(e)}"

    datos = {
        "errores": errores,
        "usuario": usuario,
        "data": form_data
    }
    datos.update(get_session_data(request))
    return render(request, "editar_perfil_usuario.html", datos)

@admin_required
def mostrarGestionarUsuarios(request):
    search_query = request.GET.get('q', '')
    page_number = request.GET.get('page')

    usuarios_list = Usuario.objects.all().order_by('-id')

    if search_query:
        usuarios_list = usuarios_list.filter(
            Q(nombres__icontains=search_query) |
            Q(correo__icontains=search_query)
        )

    paginator = Paginator(usuarios_list, 5)
    page_obj = paginator.get_page(page_number)

    datos = {
        "page_obj": page_obj,
        "search_query": search_query
    }
    datos.update(get_session_data(request))
    return render(request, "gestionar_usuarios.html", datos)

from django.contrib import messages


@admin_required
def deshabilitar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    if usuario.tipo_usuario == "Admin":
        messages.error(request, "No puedes deshabilitar a un administrador.")
        return redirect("gestionar_usuarios")

    usuario.estado = "Deshabilitado"
    usuario.save()
    registrar_historial("Deshabilitación de usuario", request.session.get("idUsuario"))

    messages.success(request, f"El usuario {usuario.nombres} ha sido deshabilitado.")
    return redirect("gestionar_usuarios")


@admin_required
def habilitar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    if usuario.estado == "Activo":
        messages.error(request, "El usuario ya está habilitado.")
        return redirect("gestionar_usuarios")

    usuario.estado = "Activo"
    usuario.save()
    registrar_historial("Habilitación de usuario", request.session.get("idUsuario"))

    messages.success(request, f"El usuario {usuario.nombres} ha sido habilitado.")
    return redirect("gestionar_usuarios")


@admin_required
def mostrarCrearTematica(request):
    datos = get_session_data(request)
    return render(request, "crear_tematica.html", datos)


@admin_required
def formCrearTematica(request):
    nom_tematica = request.POST.get("txtnomtem")
    des_tematica = request.POST.get("txtdestem")

    errores = {}

    if not nom_tematica.strip() or not des_tematica.strip():
        errores["texto"] = "El nombre y la descripción no pueden estar vacíos."
        datos = {"errores": errores}
        datos.update(get_session_data(request))
        return render(request, "crear_tematica.html", datos)

    if verificar_si_existe(Tematica, "nombre", nom_tematica):
        errores["nombre"] = f"La temática: {nom_tematica} ya existe."

    if errores:
        datos = {"errores": errores}
        datos.update(get_session_data(request))
        return render(request, "crear_tematica.html", datos)

    try:
        tematica = Tematica.objects.create(
            nombre=nom_tematica, descripcion=des_tematica
        )
        registrar_historial("Creación de temática", request.session.get("idUsuario"))
        return redirect("administrar_tematicas")

    except Exception as e:
        errores["db_error"] = f"Error al crear la temática: {str(e)}"
        datos = {"errores": errores}
        datos.update(get_session_data(request))
        return render(request, "crear_tematica.html", datos)


@admin_required
def mostrarEditarTematica(request, id):
    tematica = get_object_or_404(Tematica, id=id)
    datos = {"tematica": tematica}
    datos.update(get_session_data(request))
    return render(request, "editar_tematica.html", datos)


@admin_required
def formEditarTematica(request, id):
    nom_tematica = request.POST.get("txtnomtem")
    des_tematica = request.POST.get("txtdestem")

    errores = {}

    if not nom_tematica.strip() or not des_tematica.strip():
        errores["texto"] = "El nombre y la descripción no pueden estar vacíos."
        datos = {"errores": errores}
        datos.update(get_session_data(request))
        return render(request, "editar_tematica.html", datos)

    if Tematica.objects.filter(nombre=nom_tematica).exclude(id=id).exists():
        errores["nombre"] = f"La temática: {nom_tematica} ya existe."

    tematica = get_object_or_404(Tematica, id=id)

    if errores:
        datos = {"errores": errores, "tematica": tematica}
        datos.update(get_session_data(request))
        return render(request, "editar_tematica.html", datos)

    try:
        tematica.nombre = nom_tematica
        tematica.descripcion = des_tematica
        tematica.save()

        registrar_historial("Edición de temática", request.session.get("idUsuario"))
        return redirect("administrar_tematicas")

    except Exception as e:
        errores["db_error"] = f"Error al editar la temática: {str(e)}"
        datos = {"errores": errores, "tematica": tematica}
        datos.update(get_session_data(request))
        return render(request, "editar_tematica.html", datos)


@admin_required
def eliminarTematica(request, id):
    tematica = get_object_or_404(Tematica, id=id)
    try:
        tematica.delete()
        registrar_historial("Eliminación temática", request.session.get("idUsuario"))
    except Exception as e:
        pass
    return redirect("administrar_tematicas")


@admin_required
def mostrarAdministrarTematicas(request):
    search_query = request.GET.get('q', '')
    page_number = request.GET.get('page')

    tematicas_list = Tematica.objects.all().order_by('-id')

    if search_query:
        tematicas_list = tematicas_list.filter(
            Q(nombre__icontains=search_query)
        )

    paginator = Paginator(tematicas_list, 5) 
    
    page_obj = paginator.get_page(page_number)

    datos = {
        'page_obj': page_obj,
        'search_query': search_query
    }
    datos.update(get_session_data(request))
    return render(request, "administrar_tematicas.html", datos)

@login_required
def mostrarForo(request, foro_id):
    foro = get_object_or_404(Foro, id=foro_id)
    publicaciones = Publicacion.objects.filter(foro=foro)
    datos = {"foro": foro, "publicaciones": publicaciones}
    datos.update(get_session_data(request))
    return render(request, "ver_foro.html", datos)


@admin_required
def mostrarCrearForo(request):
    tematicas = Tematica.objects.all()
    datos = {"tematicas": tematicas}
    datos.update(get_session_data(request))
    return render(request, "crear_foro.html", datos)


@admin_required
def formCrearForo(request):
    nom_foro = request.POST.get("txtnomfor")
    des_foro = request.POST.get("txtdesfor")
    tema_id = request.POST.get("cbotem")
    imagen = request.FILES.get("imagen")

    errores = {}

    if not nom_foro.strip() or not des_foro.strip():
        errores["texto"] = "El nombre y la descripción no pueden estar vacíos."

    if verificar_si_existe(Foro, "nombre", nom_foro):
        errores["nombre"] = f"El foro: {nom_foro} ya existe, intente con otro nombre."

    if contiene_palabrotas(nom_foro) or contiene_palabrotas(des_foro):
        errores["prohibidas"] = (
            "El nombre o la descripción contienen palabras no permitidas."
        )

    if errores:
        tematicas = Tematica.objects.all()
        datos = {
            "errores": errores,
            "tematicas": tematicas,
            "data": {
                "txtnomfor": nom_foro,
                "txtdesfor": des_foro,
                "cbotem": tema_id,
            },
        }
        datos.update(get_session_data(request))
        return render(request, "crear_foro.html", datos)

    try:
        tematica = get_object_or_404(Tematica, id=tema_id)
        foro = Foro(nombre=nom_foro, descripcion=des_foro, tematica=tematica)
        if imagen:
            foro.imagen = imagen
        foro.save()

        registrar_historial("Creación de foro", request.session.get("idUsuario"))
        return redirect("administrar_foros")

    except Exception as e:
        errores["db_error"] = f"Error al crear el foro: {str(e)}"
        tematicas = Tematica.objects.all()
        datos = {
            "errores": errores,
            "tematicas": tematicas,
            "data": {
                "txtnomfor": nom_foro,
                "txtdesfor": des_foro,
                "cbotem": tema_id,
            },
        }
        datos.update(get_session_data(request))
        return render(request, "crear_foro.html", datos)


@admin_required
def mostrarEditarForo(request, id):
    foro = get_object_or_404(Foro, id=id)
    tematicas = Tematica.objects.all()
    datos = {"foro": foro, "tematicas": tematicas}
    datos.update(get_session_data(request))
    return render(request, "editar_foro.html", datos)


@admin_required
def formEditarForo(request, id):
    nom_foro = request.POST.get("txtnomfor")
    des_foro = request.POST.get("txtdesfor")
    tema_id = request.POST.get("cbotem")
    imagen = request.FILES.get("imagen")

    errores = {}

    if not nom_foro.strip() or not des_foro.strip():
        errores["texto"] = "El nombre y la descripción no pueden estar vacíos."
        tematicas = Tematica.objects.all()
        datos = {"errores": errores, "tematicas": tematicas}
        datos.update(get_session_data(request))
        return render(request, "editar_foro.html", datos)

    if Foro.objects.filter(nombre=nom_foro).exclude(id=id).exists():
        errores["nombre"] = f"El foro: {nom_foro} ya existe, intente con otro nombre."

    if contiene_palabrotas(nom_foro) or contiene_palabrotas(des_foro):
        errores["prohibidas"] = (
            "El nombre o la descripción contienen palabras no permitidas."
        )
        tematicas = Tematica.objects.all()
        datos = {"errores": errores, "tematicas": tematicas}
        datos.update(get_session_data(request))
        return render(request, "editar_foro.html", datos)

    foro = get_object_or_404(Foro, id=id)
    tematica = get_object_or_404(Tematica, id=tema_id)

    if errores:
        tematicas = Tematica.objects.all()
        datos = {"errores": errores, "foro": foro, "tematicas": tematicas}
        datos.update(get_session_data(request))
        return render(request, "editar_foro.html", datos)

    try:
        foro.nombre = nom_foro
        foro.descripcion = des_foro
        foro.tematica = tematica
        if imagen:
            foro.imagen = imagen
        foro.save()

        registrar_historial("Edición foro", request.session.get("idUsuario"))
        return redirect("administrar_foros")

    except Exception as e:
        errores["db_error"] = f"Error al editar el foro: {str(e)}"
        tematicas = Tematica.objects.all()
        datos = {"errores": errores, "foro": foro, "tematicas": tematicas}
        datos.update(get_session_data(request))
        return


@admin_required
def mostrarAdministrarForos(request):
    search_query = request.GET.get("q", "")
    page_number = request.GET.get("page")

    foros_list = Foro.objects.all().order_by("-id")

    if search_query:
        foros_list = foros_list.filter(
            Q(nombre__icontains=search_query)
            | Q(tematica__nombre__icontains=search_query)
        )

    paginator = Paginator(foros_list, 5)

    page_obj = paginator.get_page(page_number)

    datos = {"page_obj": page_obj, "search_query": search_query}
    datos.update(get_session_data(request))
    return render(request, "administrar_foros.html", datos)


@admin_required
def eliminarForo(request, id):
    foro = get_object_or_404(Foro, id=id)
    try:
        foro.delete()
        registrar_historial("Eliminación foro", request.session.get("idUsuario"))
    except Exception as e:
        errores = {"db_error": f"Error al eliminar el foro: {str(e)}"}
        return redirect("administrar_foros")

    return redirect("administrar_foros")


@login_required
def explorarForos(request):
    all_tematicas = Tematica.objects.all().order_by('nombre')
    
    popular_tematicas = Tematica.objects.all()[:3] 

    search_query = request.GET.get('q', '')
    tematica_id = request.GET.get('tematica', '')
    page_number = request.GET.get('page')

    foros_list = Foro.objects.select_related('tematica').all().order_by('-id')

    if tematica_id:
        foros_list = foros_list.filter(tematica_id=tematica_id)

    if search_query:
        foros_list = foros_list.filter(
            Q(nombre__icontains=search_query) |
            Q(descripcion__icontains=search_query)
        )

    paginator = Paginator(foros_list, 9) 
    page_obj = paginator.get_page(page_number)

    current_tematica_id_int = None
    try:
        current_tematica_id_int = int(tematica_id)
    except (ValueError, TypeError):
        pass

    datos = {
        'page_obj': page_obj,
        'all_tematicas': all_tematicas,
        'popular_tematicas': popular_tematicas,
        'search_query': search_query,
        'current_tematica_id': tematica_id,
        'current_tematica_id_int': current_tematica_id_int,
    }
    datos.update(get_session_data(request))
    return render(request, "explorar_foros.html", datos)

@login_required
def mostrarCrearPublicacion(request, foro_id):
    foro = get_object_or_404(Foro, id=foro_id)
    datos = {"foro": foro}
    datos.update(get_session_data(request))
    return render(request, "crear_publicacion.html", datos)


@login_required
def formCrearPublicacion(request, foro_id):
    titulo = request.POST.get("txtpubtit")
    comentario = request.POST.get("txtpubcom")

    usuario = obtener_usuario(request)
    foro = get_object_or_404(Foro, id=foro_id)

    errores = {}

    if not titulo.strip() or not comentario.strip():
        errores["texto"] = "El título y el comentario no pueden estar vacíos."

    if contiene_palabrotas(titulo) or contiene_palabrotas(comentario):
        errores["prohibidas"] = "La publicación contiene palabras no permitidas."

    if errores:
        datos = {
            "errores": errores,
            "foro": foro,
            "data": {
                "txtpubtit": titulo,
                "txtpubcom": comentario,
            },
        }
        datos.update(get_session_data(request))
        return render(request, "crear_publicacion.html", datos)

    try:
        Publicacion.objects.create(
            usuario=usuario, foro=foro, titulo=titulo, texto=comentario
        )
        registrar_historial("Creación publicación", usuario.id)
        return redirect("foro", foro_id=foro.id)
    except Exception as e:
        errores = {"db_error": f"Error al crear la publicación: {str(e)}"}
        datos = {
            "errores": errores,
            "foro": foro,
            "data": {
                "txtpubtit": titulo,
                "txtpubcom": comentario,
            },
        }
        datos.update(get_session_data(request))
        return render(request, "crear_publicacion.html", datos)


@login_required
def mostrarEditarPublicacion(request, foro_id, publicacion_id):
    foro = get_object_or_404(Foro, id=foro_id)
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    datos = {"foro": foro, "publicacion": publicacion}
    datos.update(get_session_data(request))
    return render(request, "editar_publicacion.html", datos)


@login_required
def formEditarPublicacion(request, foro_id, publicacion_id):
    foro = get_object_or_404(Foro, id=foro_id)
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    titulo = request.POST.get("txtpubtit")
    comentario = request.POST.get("txtpubcom")

    errores = {}

    if not titulo.strip() or not comentario.strip():
        errores["texto"] = "El título y el comentario no pueden estar vacíos."
        datos = {"errores": errores, "foro": foro, "publicacion": publicacion}
        datos.update(get_session_data(request))
        return render(request, "editar_publicacion.html", datos)

    # Verificación de palabras prohibidas
    if contiene_palabrotas(titulo) or contiene_palabrotas(comentario):
        errores["prohibidas"] = "La publicación contiene palabras no permitidas."
        datos = {"errores": errores, "foro": foro, "publicacion": publicacion}
        datos.update(get_session_data(request))
        return render(request, "editar_publicacion.html", datos)

    publicacion.titulo = titulo
    publicacion.texto = comentario

    try:
        publicacion.save()
        registrar_historial("Edición de publicación", request.session.get("idUsuario"))
        return redirect("foro", foro_id=foro.id)
    except Exception as e:
        errores["db_error"] = f"Error al editar la publicación: {str(e)}"
        datos = {"errores": errores, "foro": foro, "publicacion": publicacion}
        datos.update(get_session_data(request))
        return render(request, "editar_publicacion.html", datos)


@login_required
def mostrarPublicacion(request, foro_id, publicacion_id):
    foro = get_object_or_404(Foro, id=foro_id)
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    respuestas = Respuesta.objects.filter(publicacion=publicacion).order_by("fecha")
    datos = {"foro": foro, "publicacion": publicacion, "respuestas": respuestas}
    datos.update(get_session_data(request))
    return render(request, "publicacion.html", datos)


@login_required
def eliminarPublicacion(request, foro_id, publicacion_id):
    publicacion = get_object_or_404(Publicacion, id=publicacion_id, foro_id=foro_id)
    try:
        publicacion.delete()
        registrar_historial("Eliminación publicación", request.session.get("idUsuario"))
    except Exception as e:
        errores = {"db_error": f"Error al eliminar la publicación: {str(e)}"}
        foro = get_object_or_404(Foro, id=foro_id)
        publicaciones = Publicacion.objects.filter(foro=foro)
        datos = {"errores": errores, "foro": foro, "publicaciones": publicaciones}
        datos.update(get_session_data(request))
        return render(request, "ver_foro.html", datos)
    return redirect("foro", foro_id=foro_id)


@login_required
def formCrearRespuesta(request, foro_id, publicacion_id):
    texto_respuesta = request.POST.get("txtrespuesta")
    usuario = obtener_usuario(request)
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    foro = get_object_or_404(Foro, id=foro_id)

    if not texto_respuesta.strip():
        errores = {"texto": "La respuesta no puede estar vacía."}
        respuestas = Respuesta.objects.filter(publicacion=publicacion).order_by("fecha")
        datos = {
            "errores": errores,
            "foro": foro,
            "publicacion": publicacion,
            "respuestas": respuestas,
            "texto_respuesta": texto_respuesta,
        }
        datos.update(get_session_data(request))
        return render(request, "publicacion.html", datos)

    if contiene_palabrotas(texto_respuesta):
        errores = {"prohibidas": "La respuesta contiene palabras no permitidas."}
        respuestas = Respuesta.objects.filter(publicacion=publicacion).order_by("fecha")
        datos = {
            "errores": errores,
            "foro": foro,
            "publicacion": publicacion,
            "respuestas": respuestas,
            "texto_respuesta": texto_respuesta,
        }
        datos.update(get_session_data(request))
        return render(request, "publicacion.html", datos)

    try:
        Respuesta.objects.create(
            usuario=usuario, publicacion=publicacion, texto=texto_respuesta
        )
        registrar_historial("Creación de respuesta", usuario.id)
        return redirect(
            "mostrar_publicacion", foro_id=foro.id, publicacion_id=publicacion.id
        )
    except Exception as e:
        errores = {"db_error": f"Error al crear la respuesta: {str(e)}"}
        respuestas = Respuesta.objects.filter(publicacion=publicacion).order_by("fecha")
        datos = {
            "errores": errores,
            "foro": foro,
            "publicacion": publicacion,
            "respuestas": respuestas,
            "texto_respuesta": texto_respuesta,
        }
        datos.update(get_session_data(request))
        return render(request, "publicacion.html", datos)


@login_required
def mostrarEditarRespuesta(request, foro_id, publicacion_id, respuesta_id):
    respuesta = get_object_or_404(
        Respuesta, id=respuesta_id, publicacion_id=publicacion_id
    )
    
    publicacion = respuesta.publicacion
    foro = publicacion.foro
    
    usuario = obtener_usuario(request)

    if usuario.id != respuesta.usuario.id and usuario.tipo_usuario != "Admin":
        return HttpResponseForbidden("No tienes permiso para editar esta respuesta.")

    datos = {
        "respuesta": respuesta,
        "publicacion": publicacion,
        "foro": foro,
    }
    datos.update(get_session_data(request))
    
    return render(request, "editar_respuesta.html", datos)


@login_required
def formEditarRespuesta(request, foro_id, publicacion_id, respuesta_id):
    respuesta = get_object_or_404(
        Respuesta, id=respuesta_id, publicacion_id=publicacion_id
    )
    usuario = obtener_usuario(request)

    if usuario.id != respuesta.usuario.id and usuario.tipo_usuario != "Admin":
        return HttpResponseForbidden("No tienes permiso para editar esta respuesta.")

    texto_respuesta = request.POST.get("txtrespuesta")

    errores = {}

    if not texto_respuesta.strip():
        errores = {"texto": "La respuesta no puede estar vacía."}
        datos = {
            "errores": errores,
            "respuesta": respuesta,
            "foro_id": foro_id,
            "publicacion_id": publicacion_id,
        }
        datos.update(get_session_data(request))
        return render(request, "editar_respuesta.html", datos)

    if contiene_palabrotas(texto_respuesta):
        errores["prohibidas"] = "La respuesta contiene palabras no permitidas."
        datos = {
            "errores": errores,
            "respuesta": respuesta,
            "foro_id": foro_id,
            "publicacion_id": publicacion_id,
        }
        datos.update(get_session_data(request))
        return render(request, "editar_respuesta.html", datos)

    try:
        respuesta.texto = texto_respuesta
        respuesta.save()
        registrar_historial("Edición de respuesta", usuario.id)
        return redirect(
            "mostrar_publicacion", foro_id=foro_id, publicacion_id=publicacion_id
        )
    except Exception as e:
        errores = {"db_error": f"Error al editar la respuesta: {str(e)}"}
        datos = {
            "errores": errores,
            "respuesta": respuesta,
            "foro_id": foro_id,
            "publicacion_id": publicacion_id,
        }
        datos.update(get_session_data(request))
        return render(request, "editar_respuesta.html", datos)


@login_required
def eliminarRespuesta(request, foro_id, publicacion_id, respuesta_id):
    respuesta = get_object_or_404(
        Respuesta, id=respuesta_id, publicacion_id=publicacion_id
    )
    usuario = obtener_usuario(request)

    if usuario.id != respuesta.usuario.id and usuario.tipo_usuario != "Admin":
        return HttpResponseForbidden("No tienes permiso para eliminar esta respuesta.")

    try:
        respuesta.delete()
        registrar_historial("Eliminación de respuesta", usuario.id)
        return redirect(
            "mostrar_publicacion", foro_id=foro_id, publicacion_id=publicacion_id
        )
    except Exception as e:
        errores = {"db_error": f"Error al eliminar la respuesta: {str(e)}"}
        respuestas = Respuesta.objects.filter(publicacion_id=publicacion_id).order_by(
            "fecha"
        )
        publicacion = get_object_or_404(Publicacion, id=publicacion_id)
        datos = {
            "errores": errores,
            "foro_id": foro_id,
            "publicacion": publicacion,
            "respuestas": respuestas,
        }
        datos.update(get_session_data(request))
        return render(request, "publicacion.html", datos)


@admin_required
def mostrarHistorialAcciones(request):
    search_query = request.GET.get('q', '')
    page_number = request.GET.get('page')

    historial_list = Historial.objects.select_related('usuario').all().order_by('-id')

    if search_query:
        historial_list = historial_list.filter(
            Q(usuario__nombres__icontains=search_query) |
            Q(accion__icontains=search_query)
        )

    paginator = Paginator(historial_list, 5) 
    page_obj = paginator.get_page(page_number)

    datos = {
        "page_obj": page_obj,
        "search_query": search_query
    }
    datos.update(get_session_data(request))
    return render(request, "historial_acciones.html", datos)


def accesoDenegado(request):
    return render(
        request,
        "acceso_denegado.html",
        {"mensaje": "No tienes permiso para acceder a esta página."},
    )
