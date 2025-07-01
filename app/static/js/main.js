document.addEventListener('DOMContentLoaded', function () {
    // Lógica para el botón de menú del sidebar en el layout del dashboard
    const menuToggle = document.getElementById('menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', function (e) {
            e.preventDefault();
            const wrapper = document.getElementById('wrapper');
            if(wrapper) {
                wrapper.classList.toggle('toggled');
            }
        });
    }

    // Lógica para inicializar y mostrar automáticamente los toasts (notificaciones flash)
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.map(function (toastEl) {
        const toast = new bootstrap.Toast(toastEl, {
            delay: 5000 // El toast se ocultará después de 5 segundos
        });
        toast.show();
        return toast;
    });
});