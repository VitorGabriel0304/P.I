// Script básico para interações do sistema
document.addEventListener('DOMContentLoaded', function () {
  // Função para fechar automaticamente as mensagens de alerta (flash) após 5 segundos
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach((alert) => {
    setTimeout(() => {
      // Usa a biblioteca do Bootstrap para fechar o alerta de forma suave
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000); // 5000 milissegundos = 5 segundos
  });
});
