const API_URL = "http://localhost:8000";

// MODIFICACIÓN: Siempre que cargue o abra la página de cero, el sistema se iniciará en el Login
document.addEventListener("DOMContentLoaded", () => {
    cerrarSesion(); // Forzamos el cierre de sesión visual y de memoria al iniciar
});

// Función Profesional para autenticar con el Backend
async function autenticarUsuario() {
    const usuario = document.getElementById("login-usuario").value.trim();
    const contrasena = document.getElementById("login-password").value.trim();

    if (!usuario || !contrasena) {
        alert("⚠️ Por favor, complete todos los campos.");
        return;
    }

    try {
        const respuesta = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario: usuario, contrasena: contrasena })
        });

        const resultado = await respuesta.json();

        if (resultado.status === "success") {
            // Eliminamos el localStorage permanente para que no recuerde credenciales viejas
            mostrarPanelSistema();
        } else {
            alert("❌ " + resultado.mensaje);
        }
    } catch (error) {
        alert("🔌 Error del sistema: No hay conexión con el servidor para validar el acceso.");
    }
}

function mostrarPanelSistema() {
    document.getElementById("seccion-login").classList.add("ocultar-seccion");
    document.getElementById("panel-sistema").classList.remove("ocultar-seccion");
    document.getElementById("btn-nav-logout").classList.remove("ocultar-seccion");
    actualizarContadorCupos();
}

function cerrarSesion() {
    // Limpieza total inmediata
    document.getElementById("panel-sistema").classList.add("ocultar-seccion");
    document.getElementById("btn-nav-logout").classList.add("ocultar-seccion");
    document.getElementById("seccion-login").classList.remove("ocultar-seccion");
    
    // Validamos que los campos existan antes de limpiarlos para evitar errores en consola
    const userField = document.getElementById("login-usuario");
    const passField = document.getElementById("login-password");
    if(userField) userField.value = "";
    if(passField) passField.value = "";
}

// ... El resto de tus funciones (actualizarContadorCupos y registrarOperacion) se quedan exactamente igual abajo.



// --- MÓDULOS DE CUPOS ANTERIORES ---
async function actualizarContadorCupos() {
    try {
        const respuesta = await fetch(`${API_URL}/cupos`);
        const datos = await respuesta.json();
        document.getElementById("contador-cupos").textContent = datos.cupos_libres;
    } catch (error) {
        console.error("Error obteniendo cupos:", error);
    }
}

async function registrarOperacion(tipo) {
    const inputId = tipo === 'ingreso' ? 'doc-entrada' : 'doc-salida';
    const documento = document.getElementById(inputId).value.trim();

    if (!documento) {
        alert("⚠️ Por favor, digite un número de documento.");
        return;
    }

    try {
        const respuesta = await fetch(`${API_URL}/${tipo}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ documento: documento })
        });

        const resultado = await respuesta.json();

        if (resultado.status === "success") {
            alert("✅ " + resultado.mensaje);
            document.getElementById(inputId).value = "";
            actualizarContadorCupos();
        } else {
            alert("❌ " + resultado.mensaje);
        }
    } catch (error) {
        alert("🔌 Error de conexión con el servidor.");
    }
}
