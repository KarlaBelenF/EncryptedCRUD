// login.js
document.getElementById("btn-login").addEventListener("click", async () => {
    const correoIngresado = document.getElementById("input-correo").value;
    const contraseniaIngresada = document.getElementById("input-password").value;

    // Validación básica
    if (!correoIngresado || !contraseniaIngresada) {
        alert("Por favor, ingrese su correo y contraseña.");
        return;
    }

    try {
        const respuesta = await fetch("http://localhost:8000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                correoElectronico: correoIngresado,
                contrasenia: contraseniaIngresada
            })
        });

        const resultado = await respuesta.json();

        if (respuesta.ok) {
            // Guardamos el rol de forma local en el navegador
            localStorage.setItem("rolActivo", resultado.datos.rol);
            
            // Redirigimos automáticamente a la pantalla de la tabla
            window.location.href = "usuarios.html";
        } else {
            // Mostramos el error devuelto por la API (ej. "Contraseña incorrecta")
            alert("Error: " + resultado.detail);
        }
        
    } catch (error) {
        console.error("Error en la conexión:", error);
        alert("No se pudo conectar con el servidor. Verifique que la API esté encendida.");
    }
});

