import mercadopago
import datetime

PLANOS = {PLANOS = {
    "7_dias": {"valor": 11.90, "dias": 7},
    "15_dias": {"valor": 19.90, "dias": 15},
    "30_dias": {"valor": 29.90, "dias": 30},
    # aliases para compatibilidade com main.py
    "7d": {"valor": 11.90, "dias": 7},
    "15d": {"valor": 19.90, "dias": 15},
    "30d": {"valor": 29.90, "dias": 30},
    "7": {"valor": 11.90, "dias": 7},
    "15": {"valor": 19.90, "dias": 15},
    "30": {"valor": 29.90, "dias": 30},
},
}

def gerar_pix_mp(token, telegram_id, plano_key):
    print(f"--- GERANDO PIX PARA {telegram_id} PLANO {plano_key} ---")
    try:
        sdk = mercadopago.SDK(token)
        
        plano = PLANOS.get(plano_key)
        if not plano:
            plano = PLANOS["7_dias"]

        email_pagador = f"cliente.{telegram_id}@gmail.com"

        payment_data = {
            "transaction_amount": float(plano["valor"]),
            "description": f"VIP {plano['dias']} dias - ID {telegram_id}",
            "payment_method_id": "pix",
            "payer": {
                "email": email_pagador,
                "first_name": "Cliente",
                "last_name": "VIP",
                "identification": {
                    "type": "CPF",
                    "number": "52998224725"
                }
            },
            "external_reference": str(telegram_id)
        }

        print(f"Enviando para MP: {payment_data}")
        result = sdk.payment().create(payment_data)
        pagamento = result.get("response", {})
        
        print(f"RESPOSTA COMPLETA DO MP: {pagamento}")

        if "id" not in pagamento:
            print(f"ERRO DO MERCADO PAGO: {pagamento}")
            return None

        transaction_data = pagamento.get("point_of_interaction", {}).get("transaction_data", {})
        
        return {
            "id": pagamento["id"],
            "qr_code": transaction_data.get("qr_code"),
            "qr_code_base64": transaction_data.get("qr_code_base64"),
            "ticket_url": transaction_data.get("ticket_url"),
            "valor": plano["valor"],
            "status": pagamento.get("status")
        }

    except Exception as e:
        print(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return None
