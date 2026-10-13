document.addEventListener("DOMContentLoaded", () => {
    cargarUsuarios();
    configurarBotonSalir();
});

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
            <td>N/A</td> 
            <td>N/A</td>
            <td>${usuario.cvv}</td>
            <td>${usuario.numeroCuenta}</td>
            <td>${usuario.nip}</td>
            <td class="celda-acciones">
                <button class="btn-icono btn-editar" title="Editar" onclick="editarUsuario(${usuario.id})">
                    ✏️
                </button>
                <button class="btn-icono btn-eliminar" title="Eliminar" onclick="eliminarUsuario(${usuario.id})">
                    🗑️
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}
window.editarUsuario = function(id) {
    console.log("Abrir modal o ventana para editar al usuario con ID:", id);
};

window.eliminarUsuario = function(id) {
    if(confirm("¿Estás seguro de que deseas eliminar este usuario del sistema?")) {
        console.log("Eliminando usuario con ID:", id);
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
        modal.className = "modal-visible";
    });

    const cerrarModal = () => {
        modal.className = "modal-oculto";
        formCrear.reset();
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
        const rolSolicitante = localStorage.getItem("rolActivo") || "empleado";
        const nuevoUsuario = {
            nombre: document.getElementById("crear-nombre").value,
            apellidoPaterno: document.getElementById("crear-paterno").value,
            apellidoMaterno: document.getElementById("crear-materno").value,
            rol: document.getElementById("crear-rol").value,
            correoElectronico: document.getElementById("crear-correo").value,
            telefono: document.getElementById("crear-telefono").value,
            fechaNacimiento: document.getElementById("crear-fecha").value,
            direccion: document.getElementById("crear-direccion").value,
            rfc: document.getElementById("crear-rfc").value,
            contrasenia: document.getElementById("crear-password").value,
            numeroCuenta: document.getElementById("crear-cuenta").value,
            cvv: document.getElementById("crear-cvv").value,
            nip: document.getElementById("crear-nip").value
        };

        try {
            const respuesta = await fetch(`http://localhost:8000/usuarios/crear?rol_solicitante=${rolSolicitante}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(nuevoUsuario)
            });

            const resultado = await respuesta.json();

            if (respuesta.ok) {
                alert("Éxito: " + resultado.mensaje);
                cerrarModal();
                cargarUsuarios();
            } else {
                alert("Error: "+resultado.detail);
            }
        } catch (error) {
            console.error("Error al crear usuario:", error);
            alert("No se pudo conectar con el servidor para crear el usuario.");
        }
    });
});