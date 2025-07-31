from datetime import datetime
from flask import Blueprint, request, jsonify
from app.managers.clientes import ClienteManager
from app.managers.pedidos import PedidoManager
from app.models.clientes import Cliente

api_bp = Blueprint("api", __name__)

@api_bp.route("/api/atualizar_status", methods=["POST"])
def atualizar_status():
    data = request.get_json()
    pedido_id = data.get("id")
    novo_status = data.get("novo_status")

    manager = PedidoManager()
    pedido = manager.buscar_por_id(pedido_id)
    if not pedido:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    pedido.status = novo_status
    manager.atualizar_pedido(pedido_id, pedido.to_dict())

    return jsonify({"status": "ok"})



@api_bp.route("/api/pedidos_status/<status>")
def pedidos_por_status(status):
    pedidos = PedidoManager().buscar_todos()
    
    pedidos_filtrados = []

    for p in pedidos:
        if p.status == status:
            cliente = ClienteManager().buscar_por_id(p.id_cliente)
            pedidos_filtrados.append({
                "id": p.id,
                "cliente": cliente.nome if cliente else p.id_cliente,
                "data": p.data_previsao_entrega.strftime("%d/%m/%Y") if p.status not in ['Orçamento', 'Rascunho'] else p.data.strftime("%d/%m/%Y"),
                "total": f"R$ {p.total:.2f}",
                "data_criacao": p.data if p.data else ""
            })
            pedidos_filtrados.sort(
            key=lambda p: p['data_criacao'] if p['data_criacao'] else datetime.min,
            reverse=True)
    return jsonify(pedidos_filtrados[:5])  # LIMITA A 5

from app.managers import pedidos, clientes
@api_bp.route("/api/proximas_entregas")
def api_proximas_entregas():
    pedidos = PedidoManager.buscar_todos()
    clientes_ = ClienteManager.buscar_todos()  # ou como você monta o dicionário de clientes
    entregas_proximas = sorted(
        [p for p in pedidos if p.data_previsao_entrega and p.status != 'Finalizado'],
        key=lambda p: p.data_previsao_entrega
    )[:5]

    return jsonify([
        {
            "id": p.id,
            "cliente": clientes.get(p.id_cliente, p.id_cliente),
            "criado": p.data.strftime('%d/%m/%Y %H:%M') if p.data else '',
            "entrega": p.data_previsao_entrega.strftime('%d/%m/%Y') if p.data_previsao_entrega else '',
            "status": p.status,
            "status_class": {
                'Rascunho': 'secondary',
                'Design': 'primary',
                'Produção': 'info',
                'Finalizado': 'success',
                'Orçamento': 'dark',
                'Atrasado': 'danger'
            }.get(p.status, 'dark'),
            "total": f"R$ {p.total:.2f}"
        }
        for p in entregas_proximas
    ])