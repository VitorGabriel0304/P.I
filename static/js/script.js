// Script básico para interações do sistema
document.addEventListener('DOMContentLoaded', function () {
  // Exemplo: Auto-fechar alertas após 5 segundos
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });
});
