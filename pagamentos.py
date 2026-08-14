import mercadopago

# SEUS PLANOS ATUALIZADOS
PLANOS = {
    "7d": {"dias": 7, "preco": 11.90, "nome": "Plano 7 dias"},
    "15d": {"dias": 15, "preco": 14.90, "nome": "Plano 15 dias"},
    "30d": {"dias": 30, "preco": 19.90, "nome": "Plano VIP 30 dias"}
}

def gerar_pix_mp(access_token, telegram_id, plano_key, webhook_url=None):
    sdk = mercadopago.SDK(access_token)
    plano = PLANOS[plano_key]

    payment_data = {
        "transaction_amount": plano["preco"],
        "description": plano["nome"],
        "payment_method_id": "pix",
        "payer": {
            "email": f"user_{telegram_id}@vipbot.local",
            "first_name": f"User {telegram_id}"
        },
        "external_reference": f"{telegram_id}_{plano_key}",
    }
    if webhook_url:
        payment_data["notification_url"] = webhook_url

    result = sdk.payment().create(payment_data)
    payment = result["response"]
    
    # MP pode demorar pra gerar o QR
    txn_data = payment.get("point_of_interaction", {}).get("transaction_data", {})
    
    return {
        "id": payment["id"],
        "qr_code": txn_data.get("qr_code"),
        "qr_base64": txn_data.get("qr_code_base64"),
        "status": payment.get("status")
    }
