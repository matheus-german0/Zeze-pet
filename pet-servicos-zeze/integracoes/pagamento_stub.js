// pagamento_stub.js
// Simula criação de pagamento e notificação do gateway

function createPaymentIntent(invoiceId, amount, method){
  // retorna objeto que imitaria a resposta de um gateway
  return {
    invoiceId,
    amount: Number(amount).toFixed(2),
    method,
    status: 'pending',
    paymentUrl: 'https://sandbox.pagamento/fakepay/' + invoiceId
  };
}

function simulateGatewayCallback(invoiceId){
  // Simula uma confirmação de pagamento em 2s (apenas para demo front-end)
  return { invoiceId, status: 'paid', paid_at: new Date().toISOString(), reference: 'SIM-'+invoiceId };
}

module.exports = { createPaymentIntent, simulateGatewayCallback };
