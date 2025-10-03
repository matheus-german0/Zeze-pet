# Pagamento Stub (documentação)

Este arquivo descreve o módulo de integração de pagamento simulado.
- createPaymentIntent(invoiceId, amount, method): retorna um objeto com paymentUrl e status 'pending'.
- simulateGatewayCallback(invoiceId): simula callback do gateway, retornando status 'paid'.

Substitua este stub pelo SDK do gateway (PagSeguro, MercadoPago, Stripe) para produção.
