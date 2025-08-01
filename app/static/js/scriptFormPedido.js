const el = document.getElementById('form-pedido');
var pedido = JSON.parse(el.dataset.pedido || 'null');
var cliente = JSON.parse(el.dataset.cliente || 'null');
var produtos = JSON.parse(el.dataset.produtos || '[]');
var produtosPedido = pedido && pedido.itens ? pedido.itens : [];

function editarPedidoForm() {
    if (!pedido) return;

    $('#pedido-id').val(pedido.id);
    $('#status').val(pedido.status);
    $('#id_cliente').val(pedido.id_cliente);

    if (pedido.data_previsao_entrega) {
        $('#data_previsao_entrega').val(pedido.data_previsao_entrega.split('T')[0]);
    }

    // Se cliente estiver embutido no pedido
    /* if (pedido.cliente) {
        $('#nome').val(pedido.cliente.nome);
        $('#cpf_cnpj').val(pedido.cliente.cpf_cnpj);
        $('#email').val(pedido.cliente.email);
        $('#celular').val(pedido.cliente.celular);
        $('#endereco').val(pedido.cliente.endereco);
        $('#bairro').val(pedido.cliente.bairro);
        $('#cidade').val(pedido.cliente.cidade);
        $('#cep').val(pedido.cliente.cep);
        $('#uf').val(pedido.cliente.uf);
        $('#tipo').val(pedido.cliente.tipo);
    } */

    // Atualiza tabela de produtos
    atualizarTabelaProdutos();
    produtosPedido = produtos;
}

function atualizarTabelaProdutos() {
    var html = '';
    var totalPedido = 0;
    produtosPedido.forEach(function(p, idx) {
        var total = p.preco_unitario * p.quantidade;
        totalPedido += total;
        html += '<tr>';
        html += '<td>'+p.nome+'</td>';
        html += '<td>R$ '+p.preco_unitario.toFixed(2)+'</td>';
        html += '<td>'+p.quantidade+'</td>';
        html += '<td>R$ '+total.toFixed(2)+'</td>';
        html += '<td><button class="btn-outline-danger btn-sm" onclick="removerProduto('+idx+')">Remover</button></td>';
        html += '</tr>';
    });
    valorTotal = totalPedido;
    $('#tabela-produtos tbody').html(html);
    $('#valor-final').text('R$ '+totalPedido.toFixed(2));
    $('#produtos_json').val(JSON.stringify(produtosPedido));
}

function removerProduto(index) {
    produtosPedido.splice(index, 1);
    atualizarTabelaProdutos();
}

$(document).ready(function () {
    atualizarTabelaProdutos();
    // Preenche cliente no formulário (edição)
    // Cliente autocomplete
    $('#cpf_cnpj').on('input', function () {
        var termo = $(this).val();
        if (termo.length < 3) { $('#sugestoes-clientes').hide(); return; }
        $.getJSON("{{ url_for('buscar_clientes') }}", { q: termo }, function (res) {
            var html = '';
            res.forEach(function (c) {
                html += '<div class="sugestao-cliente" data-json="' + encodeURIComponent(JSON.stringify(c)) + '">' +
                        '<strong>' + c.nome + '</strong><br>' +
                        '<small class="text-muted">' + c.cpf_cnpj + '</small>' +
                        '</div>';
            });
            $('#sugestoes-clientes').html(html).show();
        });
    });

    $('#cpf_cnpj').focusout(function () {
        setTimeout(function () { $('#sugestoes-clientes').hide(); }, 200);
    });

    $(document).on('click', '.sugestao-cliente', function () {
        var c = JSON.parse(decodeURIComponent($(this).data('json')));
        $('#id_cliente').val(c.id);
        $('#nome').val(c.nome);
        $('#tipo').val(c.tipo);
        $('#cpf_cnpj').val(c.cpf_cnpj);
        $('#email').val(c.email);
        $('#celular').val(c.celular);
        $('#endereco').val(c.endereco);
        $('#numero').val(c.numero);
        $('#bairro').val(c.bairro);
        $('#cidade').val(c.cidade);
        $('#cep').val(c.cep);
        $('#uf').val(c.uf);
        $('#sugestoes-clientes').hide();
    });

    // Produto autocomplete
    $('#abrir-modal-produto').on('click', function () {
        $('#busca-produto').val('').focus();
        $('#preco-produto').val('');
        $('#quantidade-produto').val(1);
        $('#sugestoes-produtos').hide();
    });

    $('#busca-produto').on('input', function () {
        var termo = $(this).val();
        if (termo.length < 2) { $('#sugestoes-produtos').hide(); return; }
        $.getJSON("{{ url_for('buscar_produtos') }}", { q: termo }, function (res) {
            var html = '';
            res.forEach(function (p) {
                html += '<div class="sugestao-produto" data-json="'+encodeURIComponent(JSON.stringify(p))+'">' + p.nome + ' (R$ ' + p.preco_venda + ')</div>';
            });
            $('#sugestoes-produtos').html(html).show();
        });
    });

    $('#busca-produto').focusout(function () {
        setTimeout(function () { $('#sugestoes-produtos').hide(); }, 200);
    });

    $(document).on('click', '.sugestao-produto', function () {
        var p = JSON.parse(decodeURIComponent($(this).data('json')));
        $('#busca-produto').val(p.nome);
        $('#preco-produto').val(p.preco_venda);
        $('#sugestoes-produtos').hide();
    });

    // Adicionar produto
    $('#adicionar-produto').on('click', function () {
        var nome = $('#busca-produto').val();
        var preco = parseFloat($('#preco-produto').val());
        var qtd = parseInt($('#quantidade-produto').val());

        if (!nome || isNaN(preco) || isNaN(qtd) || qtd < 1) {
            alert('Preencha todos os campos corretamente!');
            return;
        }

        produtosPedido.push({
            nome: nome,
            preco_unitario: preco,
            quantidade: qtd
        });

        atualizarTabelaProdutos();
        $('#modal-produto').modal('hide');
    });
});

editarPedidoForm();
$('#valor_pago').focusout(function () {
    const inputValorPago = $('#valor_pago').val();
    if(inputValorPago > valorTotal){
        $('#valor_pago').val(valorTotal);
    } else if (inputValorPago < 0){
            $('#valor_pago').val(0);
    }
});