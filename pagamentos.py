import mercadopago
import datetime

PLANOS = {
    "7_dias": {"valor": 11.90, "dias": 7},
    "15_dias": {"valor": 19.90, "dias": 15},
    "30_dias": {"valor": 29.90, "dias": 30},
    # Alias - seu main.py usa 7d, 15d, 30d
    "7d": {"valor": 11.90, "dias": 7},
    "15d": {"valor": 19.90, "dias": 15},
    "30d": {"valor": 29.90, "dias": 30},
    "7": {"valor": 11.90, "dias": 7},
    "15": {"valor": 19.90, "dias": 15},
    "30": {"valor": 29.90, "dias": 30},
}

def gerar_pix_mp(token, telegram_id, plano_key):
    print(f"--- GERANDO PIX PARA {telegram_id} PLANO {plano_key} ---")
    try:
        sdk = mercadopago.SDK(token)
        
        # Converte 30d -> 30_dias se precisar
        mapeamento = {"7d": "7_dias", "15d": "15_dias", "30d": "30_dias", "7": "7_dias", "15": "15_dias", "30": "30_dias"}
        chave_real = mapeamento.get(plano_key, plano_key)
        
        plano = PLANOS.get(chave_real)
        if not plano:
            print(f"Plano {plano_key} nao encontrado, usando 7_dias")
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
        
        print(f"PIX GERADO COM SUCESSO! ID: {pagamento['id']}")

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
