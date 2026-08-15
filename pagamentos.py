import os
import mercadopago

sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN"))

def gerar_pix(valor, telegram_id, descricao="VIP"):
    payment_data = {
        "transaction_amount": float(valor),
        "description": descricao,
        "payment_method_id": "pix",
        "payer": {"email": "cliente@email.com"},
        "external_reference": str(telegram_id)
    }
    result = sdk.payment().create(payment_data)
    payment = result["response"]
    
    return {
        "id": payment["id"],
        "qr_code": payment["point_of_interaction"]["transaction_data"]["qr_code"],
        "qr_code_base64": payment["point_of_interaction"]["transaction_data"]["qr_code_base64"]
    }
