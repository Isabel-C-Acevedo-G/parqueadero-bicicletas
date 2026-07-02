const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
    cerrarSesion();
});

function limpiarCampos(ids) {
    ids.forEach(id => {
        const elemento = document.getElementById(id);
        if (elemento) elemento.value = "";
    });
}

function limpiarFormularioLogin() {
    limpiarCampos(["login-usuario", "login-password"]);
}

function limpiarFormularioRegistro() {
    limpiarCampos([
        "registro-documento",
        "registro-nombres",
        "registro-apellidos",
        "registro-correo",
        "registro-telefono",
        "registro-password"
    ]);
}

function limpiarFormularioMovimientos() {
    limpiarCampos(["doc-movimiento", "espacio-movimiento"]);
}

function limpiarFormularioIncidente() {
    limpiarCampos(["incidente-bici", "incidente-descripcion"]);
}

// Autenticación Profesional Multi-Rol (Login)
async function autenticarUsuario() {
    const usuario = document.getElementById("login-usuario").value.trim();
    const contrasena = document.getElementById("login-password").value.trim();

    if (!usuario || !contrasena) {
        alert("⚠️ Por favor, complete todos los campos de acceso.");
        return;
    }

    try {
        const respuesta = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario: usuario, contrasena: contrasena })
        });

        let resultado = null;
        try {
            resultado = await respuesta.json();
        } catch (parseError) {
            console.error('Error parseando JSON de login:', parseError);
        }

        const mensaje = resultado?.mensaje || resultado?.detail || respuesta.statusText || "Error de servidor desconocido.";

        if (respuesta.ok && resultado?.status === "success") {
            limpiarFormularioLogin();
            mostrarPanelSistema(resultado.rol);
        } else {
            console.error('Login falló:', respuesta.status, resultado);
            alert("❌ " + mensaje);
        }
    } catch (error) {
        console.error('Error de red en login:', error);
        alert("🔌 Error del sistema: No hay conexión con el servidor relacional SQL. Verifique Docker Desktop.");
    }
}

function mostrarPanelSistema(rol) {
    document.getElementById("seccion-login").classList.add("ocultar-seccion");
    document.getElementById("panel-sistema").classList.remove("ocultar-seccion");
    document.getElementById("btn-nav-logout").classList.remove("ocultar-seccion");
    
    const saludo = document.getElementById("saludo-rol");
    const bloqueGestion = document.getElementById("bloque-gestion-operario");
    
    if (rol === "Administrador" || rol === "Operario") {
        saludo.innerHTML = "Panel Central <span class='texto-resaltado'>Administrativo</span>";
        bloqueGestion.classList.remove("ocultar-seccion");
    } else {
        saludo.innerHTML = "Portal del <span class='texto-resaltado'>Ciclista</span>";
        bloqueGestion.classList.add("ocultar-seccion");
    }
    
    actualizarContadorCupos();
}

function cerrarSesion() {
    document.getElementById("panel-sistema").classList.add("ocultar-seccion");
    document.getElementById("seccion-ubicaciones").classList.add("ocultar-seccion");
    document.getElementById("seccion-planes").classList.add("ocultar-seccion");
    document.getElementById("seccion-registro").classList.add("ocultar-seccion");
    document.getElementById("btn-nav-logout").classList.add("ocultar-seccion");
    document.getElementById("seccion-login").classList.remove("ocultar-seccion");
    
    const userField = document.getElementById("login-usuario");
    const passField = document.getElementById("login-password");
    if(userField) userField.value = "";
    if(passField) passField.value = "";
}

function mostrarRegistro(event) {
    if (event) event.preventDefault();
    document.getElementById("seccion-login").classList.add("ocultar-seccion");
    document.getElementById("seccion-ubicaciones").classList.add("ocultar-seccion");
    document.getElementById("seccion-planes").classList.add("ocultar-seccion");
    document.getElementById("panel-sistema").classList.add("ocultar-seccion");
    const registro = document.getElementById("seccion-registro");
    registro.classList.remove("ocultar-seccion");
    registro.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function mostrarLogin(event) {
    if (event) event.preventDefault();
    document.getElementById("seccion-registro").classList.add("ocultar-seccion");
    document.getElementById("seccion-ubicaciones").classList.add("ocultar-seccion");
    document.getElementById("seccion-planes").classList.add("ocultar-seccion");
    document.getElementById("panel-sistema").classList.add("ocultar-seccion");
    const inicio = document.getElementById("seccion-login");
    inicio.classList.remove("ocultar-seccion");
    inicio.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function registrarUsuario() {
    const documento = document.getElementById("registro-documento").value.trim();
    const nombres = document.getElementById("registro-nombres").value.trim();
    const apellidos = document.getElementById("registro-apellidos").value.trim();
    const correo = document.getElementById("registro-correo").value.trim();
    const telefono = document.getElementById("registro-telefono").value.trim();
    const contrasena = document.getElementById("registro-password").value.trim();
    const rol = document.getElementById("registro-rol").value;

    if (!documento || !nombres || !apellidos || !correo || !contrasena) {
        alert("⚠️ Por favor, complete todos los campos de registro.");
        return;
    }

    try {
        const respuesta = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ documento, nombres, apellidos, correo, telefono, contrasena, rol })
        });

        const resultado = await respuesta.json();
        const mensaje = resultado?.mensaje || resultado?.detail || respuesta.statusText || "Error desconocido al registrar usuario.";

        if (respuesta.ok && resultado?.status === "success") {
            alert("✅ " + mensaje);
            limpiarFormularioRegistro();
            mostrarLogin();
        } else {
            alert("❌ " + mensaje);
        }
    } catch (error) {
        console.error('Error de red en registro:', error);
        alert("🔌 Error del sistema: No se pudo conectar con el backend.");
    }
}

async function actualizarContadorCupos() {
    try {
        const respuesta = await fetch(`${API_URL}/cupos`);
        const datos = await respuesta.json();
        document.getElementById("contador-cupos").textContent = datos.cupos_libres;
    } catch (error) {
        console.error("Error obteniendo cupos:", error);
    }
}

async function procesarMovimiento(tipo) {
    const documento = document.getElementById("doc-movimiento").value.trim();
    const espacio = document.getElementById("espacio-movimiento").value.trim();

    if (!documento) {
        alert("⚠️ Por favor, ingrese el documento del ciclista.");
        return;
    }

    try {
        const respuesta = await fetch(`${API_URL}/${tipo}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ documento: documento, espacio: espacio })
        });
        const resultado = await respuesta.json();
        alert(resultado.status === "success" ? "✅ " + resultado.mensaje : "❌ " + resultado.mensaje);
        if (resultado.status === "success") {
            limpiarFormularioMovimientos();
        }
        actualizarContadorCupos();
    } catch (error) {
        alert("❌ Error de red al procesar el movimiento en la base de datos SQL.");
    }
}

async function registrarIncidente() {
    const bicicleta = document.getElementById("incidente-bici").value.trim();
    const descripcion = document.getElementById("incidente-descripcion").value.trim();

    if (!bicicleta || !descripcion) {
        alert("⚠️ Por favor, rellene los campos del incidente.");
        return;
    }

    try {
        const respuesta = await fetch(`${API_URL}/incidente`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ bicicleta: bicicleta, descripcion: descripcion })
        });
        const resultado = await respuesta.json();
        const mensaje = resultado.mensaje || resultado.detail || "Error desconocido al guardar el incidente.";
        alert(respuesta.ok ? "✅ " + mensaje : "❌ " + mensaje);
        if (respuesta.ok) {
            limpiarFormularioIncidente();
        }
    } catch (error) {
        alert("❌ Error de red al guardar el incidente.");
    }
}

function mostrarInicio() {
    document.getElementById("seccion-login").classList.remove("ocultar-seccion");
    document.getElementById("seccion-registro").classList.add("ocultar-seccion");
    document.getElementById("seccion-ubicaciones").classList.add("ocultar-seccion");
    document.getElementById("seccion-planes").classList.add("ocultar-seccion");
    document.getElementById("panel-sistema").classList.add("ocultar-seccion");
}

function mostrarUbicaciones() {
    document.getElementById("seccion-login").classList.add("ocultar-seccion");
    document.getElementById("seccion-registro").classList.add("ocultar-seccion");
    document.getElementById("seccion-ubicaciones").classList.remove("ocultar-seccion");
    document.getElementById("seccion-planes").classList.add("ocultar-seccion");
    document.getElementById("panel-sistema").classList.add("ocultar-seccion");
}

function mostrarPlanes() {
    document.getElementById("seccion-login").classList.add("ocultar-seccion");
    document.getElementById("seccion-registro").classList.add("ocultar-seccion");
    document.getElementById("seccion-ubicaciones").classList.add("ocultar-seccion");
    document.getElementById("seccion-planes").classList.remove("ocultar-seccion");
    document.getElementById("panel-sistema").classList.add("ocultar-seccion");
}
