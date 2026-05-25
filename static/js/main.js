// Confirmar eliminación
function confirmarEliminar(url, nombre) {
    if (confirm(`¿Estás seguro que querés eliminar "${nombre}"?`)) {
        window.location.href = url;
    }
}

// Auto cerrar alertas después de 4 segundos
document.addEventListener("DOMContentLoaded", function () {
    setTimeout(function () {
        const alertas = document.querySelectorAll(".alert");
        alertas.forEach(function (alerta) {
            const bsAlerta = bootstrap.Alert.getOrCreateInstance(alerta);
            bsAlerta.close();
        });
    }, 4000);
});

// Mostrar nombre del archivo seleccionado
document.querySelectorAll(".form-control[type=file]").forEach(function (input) {
    input.addEventListener("change", function () {
        const nombre = this.files[0]?.name || "Ningún archivo seleccionado";
        const label = this.nextElementSibling;
        if (label) label.textContent = nombre;
    });
});