import mercadopago
import datetime

PLANOS = {
    "7_dias": {"valor": 11.90, "preco": 11.90, "dias": 7, "nome": "VIP 7 Dias"},
    "15_dias": {"valor": 14.90, "preco": 14.90, "dias": 15, "nome": "VIP 15 Dias"},
    "30_dias": {"valor": 19.90, "preco": 19.90, "dias": 30, "nome": "VIP 30 Dias"},
    "7d": {"valor": 11.90, "preco": 11.90, "dias": 7, "nome": "VIP 7 Dias"},
    "15d": {"valor": 14.90, "preco": 14.90, "dias": 15, "nome": "VIP 15 Dias"},
    "30d": {"valor": 19.90, "preco": 19.90, "dias": 30, "nome": "VIP 30 Dias"},
}

def gerar_pix_mp(token, telegram_id, plano_key):
    try:
        sdk = mercadopago.SDK(token)
        mapa = {"7d": "7_dias", "15d": "15_dias", "30d": "30_dias"}
        chave = mapa.get(plano_key, plano_key)
        plano = PLANOS.get(chave, PLANOS["7_dias"])
        payment_data = {
            "transaction_amount": float(plano["valor"]),
            "description": f"{plano['nome']} - ID {telegram_id}",
            "payment_method_id": "pix",
            "payer": {
                "email": f"cliente.{telegram_id}@gmail.com",
                "first_name": "Cliente",
                "last_name": "VIP",
                "identification": {"type": "CPF", "number": "52998224725"}
            },
            "external_reference": str(telegram_id)
        }
        result = sdk.payment().create(payment_data)
        pagamento = result.get("response", {})
        if "id" not in pagamento:
            print(f"ERRO MP: {pagamento}")
            return None
        trans = pagamento.get("point_of_interaction", {}).get("transaction_data", {})
        return {
            "id": pagamento["id"],
            "qr_code": trans.get("qr_code"),
            "qr_code_base64": trans.get("qr_code_base64"),
            "ticket_url": trans.get("ticket_url"),
            "valor": plano["valor"],
            "preco": plano["valor"],
            "nome": plano["nome"],
            "dias": plano["dias"],
            "status": pagamento.get("status")
        }
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        return None
