function login() {
    const correo = document.getElementById("correo").value;
    const password = document.getElementById("password").value;
    const errorElement = document.getElementById("error-message");
    errorElement.innerText = ""; // Limpiar error previo

    // Validación simple de cliente
    if (!correo || !password) {
        errorElement.innerText = "Por favor, introduce correo y contraseña.";
        return;
    }

    fetch("/auth/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ correo, password })
    })
    .then(response => {
        if (!response.ok) {
            // Si la respuesta no es 2xx, intenta parsear el error
            return response.json().then(errData => {
                // Lanza un error para ser capturado por el .catch
                throw new Error(errData.error || "Error en el servidor");
            }).catch(() => {
                // Si el JSON falla o no hay 'error', lanza error genérico
                throw new Error("Credenciales incorrectas o error de red.");
            });
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
        
        if (data.token) {
            // Guardar el token y el rol en localStorage
            localStorage.setItem("token", data.token);
            localStorage.setItem("rol", data.rol);
            if (data.rol === "administrador") {
                window.location.href = "/administrador";
            } else if (data.rol === "profesor") {
                window.location.href = "/dashboard";
            } else if (data.rol === "conserje") {
                window.location.href = "/conserjes";
            } else {
                console.log("Rol desconocido:", data.rol);
                errorElement.innerText = "Rol de usuario no reconocido.";
            }
        } else {
            // Si la respuesta es 200 OK pero no hay token
            errorElement.innerText = data.error || "Error desconocido al iniciar sesión.";
        }
    })
    .catch(error => {
        // Captura errores de red o los lanzados desde el primer .then
        console.error("Error en login:", error);
        errorElement.innerText = error.message;
    });
}

/* --- Lógica de Carga de Páginas Protegidas --- */
function cargarDashboard() {
    console.log("Cargando Dashboard. Token:", localStorage.getItem("token"));
    fetch("/dashboard", {
        method: "GET",
        headers: { "Authorization": "Bearer " + localStorage.getItem("token") }
    })
    .then(response => {
        if (response.status === 401 || response.status === 403) {
            localStorage.clear(); // Limpiar token inválido
            window.location.href = "/";  // Si no está autorizado, vuelve al login
        } else if (response.ok) {
            return response.text();
        } else {
            throw new Error("No se pudo cargar el dashboard.");
        }
    })
    .then(html => {
        if (html) {
            document.documentElement.innerHTML = html;
        }
    })
    .catch(err => {
        console.error(err);
        window.location.href = "/"; // Fallback al login
    });
}

function cargarConserjes() {
    console.log("Cargando Conserjes. Token:", localStorage.getItem("token"));
    fetch("/conserjes", {
        method: "GET",
        headers: { "Authorization": "Bearer " + localStorage.getItem("token") }
    })
    .then(response => {
        if (response.status === 401 || response.status === 403) {
            localStorage.clear();
            window.location.href = "/";
        } else if (response.ok) {
            return response.text();
        } else {
            throw new Error("No se pudo cargar la página de conserjes.");
        }
    })
    .then(html => {
        if (html) {
            document.documentElement.innerHTML = html;
        }
    })
    .catch(err => {
        console.error(err);
        window.location.href = "/"; // Fallback al login
    });
}

/* --- Enrutador Simple de Lado Cliente --- */
// Este código decide qué mostrar al cargar la página.
(function() {
    const path = window.location.pathname;
    
    if (path === "/") {
        // Si es la raíz, muestra el formulario de login
        document.querySelector('.login-container').style.display = 'block';
    } else if (path === "/dashboard") {
        // Si es dashboard, carga su contenido
        cargarDashboard();
    } else if (path === "/conserjes") {
        // Si es conserjes, carga su contenido
        cargarConserjes();
    }
    // NOTA: La ruta "/administrador" no se maneja aquí porque el
    // script de login redirige directamente. Si un admin recarga
    // /administrador, necesitarías una lógica similar a esta.
})();