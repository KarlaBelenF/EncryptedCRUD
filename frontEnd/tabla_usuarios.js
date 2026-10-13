document.addEventListener("DOMContentLoaded", () => {
    cargarUsuarios();
    configurarBotonSalir();
});

let usuarioEditandoId = null;
let estatusUsuarioEditando = true;

function obtenerRolSolicitante() {
    return (localStorage.getItem("rolActivo") || "empleado").toLowerCase();
}

// Función para el botón de Salir
function configurarBotonSalir() {
    const btnSalir = document.getElementById("btn-salir");
    if (btnSalir) {
        btnSalir.addEventListener("click", (e) => {
            e.preventDefault();
            localStorage.removeItem("rolActivo");
            window.location.href = "inicio_sesion.html";
        });
    }
}

async function cargarUsuarios() {
    try {
        const rolUsuario = localStorage.getItem("rolActivo") || "empleado";
        const respuesta = await fetch(`http://localhost:8000/usuarios?rol_solicitante=${rolUsuario}`);
        
        if (!respuesta.ok) {
            throw new Error("Error en la respuesta del servidor");
        }

        const json = await respuesta.json();
        
        if (json.status === "success") {
            renderizarTabla(json.data);
        } else {
            alert("Error al obtener los datos del servidor.");
        }
    } catch (error) {
        console.error("Hubo un problema con la petición Fetch:", error);
        alert("No se pudo conectar con la base de datos. Verifica que el servidor de FastAPI esté corriendo.");
    }
}

function renderizarTabla(usuarios) {
    const tbody = document.getElementById('tabla-usuarios-body');
    tbody.innerHTML = '';
    const esAdministrador = obtenerRolSolicitante() === "administrador";
    
    usuarios.forEach(usuario => {
        const tr = document.createElement('tr');
        
        const apellidos = `${usuario.apellidoPaterno} ${usuario.apellidoMaterno}`;
        const estadoTexto = usuario.estatus ? 'Activo' : 'Inactivo';

        tr.innerHTML = `
            <td>${usuario.id}</td>
            <td>${usuario.nombre}</td>
            <td>${apellidos}</td>
            <td>${usuario.correoElectronico}</td>
            <td>${usuario.rol}</td>
            <td>${estadoTexto}</td>
            <td>${usuario.telefono}</td>
            <td>${usuario.direccion}</td>
            <td>${usuario.fechaNacimiento}</td>
            <td>${usuario.rfc}</td>
            <td>${usuario.cvv}</td>
            <td>${usuario.numeroCuenta}</td>
            <td>${usuario.nip}</td>
            <td class="celda-acciones">
                ${esAdministrador ? `<button class="btn-icono btn-editar" title="Editar" onclick="editarUsuario(${usuario.id})">✏️</button>` : ""}
                <button class="btn-icono btn-eliminar" title="Eliminar" onclick="eliminarUsuario(${usuario.id})">
                    🗑️
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}
window.editarUsuario = async function(id) {
    if (obtenerRolSolicitante() !== "administrador") {
        alert("Solo los administradores pueden editar usuarios.");
        return;
    }

    try {
        const respuesta = await fetch(
            `http://localhost:8000/usuarios/${id}?rol_solicitante=administrador`
        );
        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(resultado.detail || "No se pudieron cargar los datos del usuario.");
        }

        const usuario = resultado.data;
        usuarioEditandoId = id;
        estatusUsuarioEditando = usuario.estatus;
        document.getElementById("crear-nombre").value = usuario.nombre;
        document.getElementById("crear-paterno").value = usuario.apellidoPaterno;
        document.getElementById("crear-materno").value = usuario.apellidoMaterno;
        document.getElementById("crear-rol").value = usuario.rol;
        document.getElementById("crear-correo").value = usuario.correoElectronico;
        document.getElementById("crear-password").value = "";
        document.getElementById("crear-password").required = false;
        document.getElementById("crear-password").placeholder = "Dejar vacío para conservar la actual";
        document.getElementById("crear-telefono").value = usuario.telefono;
        document.getElementById("crear-fecha").value = usuario.fechaNacimiento;
        document.getElementById("crear-direccion").value = usuario.direccion;
        document.getElementById("crear-rfc").value = usuario.rfc;
        document.getElementById("crear-cuenta").value = usuario.numeroCuenta;
        document.getElementById("crear-cvv").value = usuario.cvv;
        document.getElementById("crear-nip").value = usuario.nip;
        document.getElementById("titulo-modal-usuario").textContent = "Editar Usuario";
        document.getElementById("btn-guardar").textContent = "Guardar Cambios";
        document.getElementById("modal-nuevo-usuario").className = "modal-visible";
    } catch (error) {
        console.error("Error al cargar usuario para editar:", error);
        alert(error.message || "No se pudo conectar con el servidor para cargar el usuario.");
    }
};

window.eliminarUsuario = async function(id) {
    if (!confirm("¿Estás seguro de que deseas eliminar este usuario del sistema?")) {
        return;
    }

    try {
        const rolSolicitante = obtenerRolSolicitante();
        const respuesta = await fetch(
            `http://localhost:8000/usuarios/${id}?rol_solicitante=${encodeURIComponent(rolSolicitante)}`,
            { method: "DELETE" }
        );
        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(resultado.detail || "No se pudo eliminar el usuario.");
        }

        alert(resultado.mensaje);
        await cargarUsuarios();
    } catch (error) {
        console.error("Error al eliminar usuario:", error);
        alert(error.message || "No se pudo conectar con el servidor para eliminar el usuario.");
    }
};


// ==========================================
// CREACIÓN DE USUARIO
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("modal-nuevo-usuario");
    const btnAbrirModal = document.getElementById("btn-abrir-modal");
    const btnCerrarModal = document.getElementById("btn-cerrar-modal");
    const btnCancelarModal = document.getElementById("btn-cancelar-modal");
    const formCrear = document.getElementById("form-crear-usuario");

    // Función para abrir el modal
    btnAbrirModal.addEventListener("click", () => {
        cerrarModal();
        modal.className = "modal-visible";
    });

    const cerrarModal = () => {
        modal.className = "modal-oculto";
        formCrear.reset();
        usuarioEditandoId = null;
        estatusUsuarioEditando = true;
        document.getElementById("crear-password").required = true;
        document.getElementById("crear-password").placeholder = "";
        document.getElementById("titulo-modal-usuario").textContent = "Crear Nuevo Usuario";
        document.getElementById("btn-guardar").textContent = "Guardar Usuario";
    };
    btnCerrarModal.addEventListener("click", cerrarModal);
    btnCancelarModal.addEventListener("click", cerrarModal);

    window.addEventListener("click", (e) => {
        if (e.target === modal) {
            cerrarModal();
        }
    });

    formCrear.addEventListener("submit", async (e) => {
        e.preventDefault();
        const rolSolicitante = obtenerRolSolicitante();
        const datosUsuario = {
            nombre: document.getElementById("crear-nombre").value,
            apellidoPaterno: document.getElementById("crear-paterno").value,
            apellidoMaterno: document.getElementById("crear-materno").value,
            rol: document.getElementById("crear-rol").value,
            correoElectronico: document.getElementById("crear-correo").value,
            telefono: document.getElementById("crear-telefono").value,
            fechaNacimiento: document.getElementById("crear-fecha").value,
            direccion: document.getElementById("crear-direccion").value,
            rfc: document.getElementById("crear-rfc").value,
            contrasenia: document.getElementById("crear-password").value || null,
            numeroCuenta: document.getElementById("crear-cuenta").value,
            cvv: document.getElementById("crear-cvv").value,
            nip: document.getElementById("crear-nip").value
        };

        if (usuarioEditandoId !== null) {
            datosUsuario.estatus = estatusUsuarioEditando;
        }

        try {
            const esEdicion = usuarioEditandoId !== null;
            const ruta = esEdicion
                ? `http://localhost:8000/usuarios/${usuarioEditandoId}?rol_solicitante=${rolSolicitante}`
                : `http://localhost:8000/usuarios/crear?rol_solicitante=${rolSolicitante}`;
            const respuesta = await fetch(ruta, {
                method: esEdicion ? "PUT" : "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(datosUsuario)
            });

            const resultado = await respuesta.json();

            if (!respuesta.ok) {
                throw new Error(resultado.detail || "No se pudo guardar el usuario.");
            }

            alert(resultado.mensaje);
            cerrarModal();
            await cargarUsuarios();
        } catch (error) {
            console.error("Error al guardar usuario:", error);
            alert(error.message || "No se pudo conectar con el servidor para guardar el usuario.");
        }
    });
});