import sqlalchemy.exc
from flask import Flask, render_template, url_for, request, redirect, flash, Response
from sqlalchemy import select, func, desc, asc
from models import *
import plotly.express as px
import plotly.io as pio
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SENHA'

@app.route("/")
def index():
    return render_template("base.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route('/cadastros')
def cadastros():
    return render_template("cadastros.html")


@app.route('/tabelas')
def tabelas():
    return render_template("tabelas.html")


@app.route('/graficos')
def graficos():
    graph_funcionario = grafico_funcionario()
    graph_produto = grafico_produto()
    return render_template("graficos.html",
                        grafico_func=graph_funcionario, grafico_prod=graph_produto)


@app.route("/inicio")
def inicio():
    return render_template("inicio.html")


@app.route('/grafico_produto')
def grafico_produto():
    valor_produtos = db_sesion.execute(
        select((Produto.quantidade * Produto.valor).label('valor_total'), Produto.nome)
        .order_by(desc('valor_total'))
        .limit(5)
    ).fetchall()

    for nome_produto in valor_produtos:
        print(nome_produto)
    print("Quantidade, valor, produto:", valor_produtos)

    # Dados dos produtos
    produtos = [
        {"nome": valor_produtos[0][1], "valor": valor_produtos[0][0]},
        {"nome": valor_produtos[1][1], "valor": valor_produtos[1][0]},
        {"nome": valor_produtos[2][1], "valor": valor_produtos[2][0]},
        {"nome": valor_produtos[3][1], "valor": valor_produtos[3][0]},
        {"nome": valor_produtos[4][1], "valor": valor_produtos[4][0]}

    ]

    print("Valor chave 1:", valor_produtos[0][0])
    print("Valor chave 0:", valor_produtos[0][1])
    print('prod', produtos)

    # Convertendo os dados para um DataFrame
    df = pd.DataFrame(produtos)

    # Criando um gráfico com Plotly Express
    fig = px.bar(
        df,
        x="nome",
        y="valor",
        title="Valor por produto no estoque",
        labels={"valor": "Valores", "nome": "Produto"},
        color="nome"
    )
    fig.layout.update().legend.visible = False

    # Convertendo o gráfico para HTML
    graph_html = fig.to_html(full_html=False)

    # Renderizando o template com o gráfico
    return graph_html


@app.route('/produtos', methods=['GET'])
def produtos():
    sql_produtos = (select(Produto, Categoria)
                    .join(Categoria, Produto.categoria_id == Categoria.id)
                    )
    resultado_produtos = db_sesion.execute(sql_produtos).scalars()
    print('listadeprodutos:', resultado_produtos)
    return render_template('lista_produtos.html',
                           produtos_banco=resultado_produtos)


@app.route('/grafico_funcionario')
def grafico_funcionario():
    valor_funcionario = db_sesion.execute(
        select(
            Funcionario.nome,
            func.count(Movimentacao.id).label('movimentacao_total')
        )
        .join(Movimentacao, Funcionario.id == Movimentacao.funcionario_id)
        .group_by(Funcionario.id)
        .order_by(desc('movimentacao_total'))
        .limit(5)
    ).fetchall()

    for nome_funcionario in valor_funcionario:
        print(nome_funcionario)

    # Dados dos funcionarios
    funcionarios = [
        {"nome": valor_funcionario[0][0], "movimentacao": valor_funcionario[0][1]},
        {"nome": valor_funcionario[1][0], "movimentacao": valor_funcionario[1][1]},
        {"nome": valor_funcionario[2][0], "movimentacao": valor_funcionario[2][1]},
        {"nome": valor_funcionario[3][0], "movimentacao": valor_funcionario[3][1]}

    ]

    print("Valor chave 1:", valor_funcionario[0][0])
    print("Valor chave 0:", valor_funcionario[0][1])
    print('func', funcionarios)

    # Convertendo os dados para um DataFrame
    df = pd.DataFrame(funcionarios)

    # Criando um gráfico com Plotly Express
    fig = px.bar(
        df,
        x="nome",
        y="movimentacao",
        title="Total de movimentações por funcionário",
        labels={"movimentacao": "Movimentações", "nome": "Funcionário"},
        color="nome",

    )
    fig.layout.update().legend.visible = False

    # Convertendo o gráfico para HTML
    graph_html = fig.to_html(full_html=False)

    return graph_html


@app.route('/novo_produto', methods=["POST", "GET"])
def criar_produto():
    if request.method == "POST":
        print("teste_1")
        if (not request.form['form_nome'] or not request.form['form_marca']
                or not request.form['form_descricao'] or not request.form['form_valor']
                or not request.form['form_codigo'] or not request.form['form_categoria_id']):
            flash("Preencher os campos em branco!!", "error")
            print("teste_2")
        else:
            try:
                form_criar = Produto(nome=request.form.get('form_nome'),
                                     marca=request.form.get('form_marca'),
                                     descricao=request.form.get('form_descricao'),
                                     valor=float(request.form.get('form_valor')),
                                     codigo=int(request.form.get('form_codigo').strip()),
                                     categoria_id=int(request.form.get('form_categoria_id')),
                                     quantidade=0
                                     )
                form_criar.save()
                db_sesion.close()
                flash("Evento criado!!", "success")
                print("teste_4")

            except sqlalchemy.exc.IntegrityError:
                flash("O código deste produto já está cadastrado!!", "error")

            return redirect(url_for('produtos'))

    lista_categorias = select(Categoria).select_from(Categoria)
    lista_categoria = db_sesion.execute(lista_categorias).scalars()
    resultado_categoria = []

    for categorias in lista_categoria:
        resultado_categoria.append(categorias.serialize_user())

    return render_template('cadastro_de_produto.html', var_categoria=resultado_categoria)


@app.route('/editar_produto/<int:id>', methods=["POST", "GET"])
def editar_produto(id):
    # Obtém o produto pelo ID
    produto_atualizado = db_sesion.execute(select(Produto).where(Produto.id == id)).scalar()

    if not produto_atualizado:
        flash("Produto não encontrado!", "error")
        return redirect(url_for('produtos'))

    if request.method == "POST":
        # Verifica se todos os campos necessários foram preenchidos
        if (not request.form['form_nome'] and not request.form['form_marca'] and
                not request.form['form_descricao'] and not request.form['form_valor'] and
                not request.form['form_codigo'] and not request.form['form_categoria_id']):
            flash("Preencher os campos em branco!!", "error")
        else:
            try:
                # Atualiza os campos do produto
                produto_atualizado.nome = request.form.get('form_nome')
                produto_atualizado.marca = request.form.get('form_marca')
                produto_atualizado.descricao = request.form.get('form_descricao')
                produto_atualizado.valor = request.form.get('form_valor')
                produto_atualizado.codigo = request.form.get('form_codigo').strip()
                produto_atualizado.categoria_id = request.form.get('form_categoria_id')

                # Salva as alterações no banco de dados
                produto_atualizado.save()
                db_sesion.commit()
                flash("Modificações salvas!!", "success")

            except sqlalchemy.exc.IntegrityError:
                flash("O código deste produto já está cadastrado!!", "error")

            # Redireciona para a página de produtos
            return redirect(url_for('criar_produto'))

    # Obtém a lista de categorias para exibir no formulário de edição
    categoria_cad = select(Categoria).filter_by(id=produto_atualizado.categoria_id)
    categoria_cad = db_sesion.execute(categoria_cad).scalar()
    lista_categorias = select(Categoria).select_from(Categoria)
    lista_categoria = db_sesion.execute(lista_categorias).scalars()
    resultado_categoria = [categoria.serialize_user() for categoria in lista_categoria]

    # Renderiza o template de edição de produto com os dados do produto e das categorias
    return render_template('editar_produto.html', var_produto=produto_atualizado,
                           var_categoria=resultado_categoria, cat_atual=categoria_cad)


@app.route('/funcionarios', methods=['GET'])
def funcionarios():
    sql_funcionarios = select(Funcionario)
    resultado_funcionarios = db_sesion.execute(sql_funcionarios).scalars()
    lista_funcionarios = []
    for x in resultado_funcionarios:
        lista_funcionarios.append(x.serialize_user())
        print(lista_funcionarios[-1])
    return render_template("lista_funcionarios.html",
                           funcionarios_banco=lista_funcionarios)


@app.route('/novo_funcionario', methods=["POST", "GET"])
def criar_funcionario():
    if request.method == "POST":
        print("Teste 1")

        if (not request.form['form_nome'] or not request.form['form_telefone'] or not request.form['form_anoNasci']
                or not request.form['form_endereco'] or not request.form['form_cpf'] or not request.form['form_email']):
            flash("Preencher os campos em branco!!", "error")

        else:
            print("Teste 2")
            cpf = request.form.get('form_cpf').strip()
            cpf_existe = db_sesion.execute(select(Funcionario).where(Funcionario.cpf == cpf)).scalar()
            print(cpf_existe)

            print("Teste 3")
            telefone = request.form.get('form_telefone').strip()
            telefone_existe = db_sesion.execute(select(Funcionario).where(Funcionario.telefone == telefone)).scalar()

            print("teste 4")
            email = request.form.get('form_email').strip()
            email_existe = db_sesion.execute(select(Funcionario).where(Funcionario.email == email)).scalar()

            if cpf_existe:
                flash("Este CPF já está cadastrado!!", "error")
                print("teste5")

            elif telefone_existe:
                print('test2')
                flash("Este telefone já está cadastrado!!", "error")

            elif email_existe:
                flash("Este email já está cadastrado!!", "error")

            else:
                print("teste else")
                form_criar = Funcionario(nome=request.form.get('form_nome'),
                                         telefone=telefone,
                                         ano_de_nascimento=int(request.form.get('form_anoNasci')),
                                         endereco=request.form.get('form_endereco'),
                                         cpf=cpf,
                                         email=email,
                                         )

                form_criar.save()
                db_sesion.close()
                flash("Evento criado!!", "success")

                return redirect(url_for('funcionarios'))

    return render_template('cadastro_de_funcionario.html')


@app.route('/editar_funcionario/<int:id>', methods=["POST", "GET"])
def editar_funcionario(id):
    # Obtém o funcionario pelo ID
    funcionario_atualizado = db_sesion.execute(select(Funcionario).where(Funcionario.id == id)).scalar()

    if request.method == "POST":
        # Verifica se todos os campos necessários foram preenchidos
        print('test1')
        if (not request.form['form_nome'] and not request.form['form_telefone'] and
                not request.form['form_anoNasci'] and not request.form['form_endereco'] and
                not request.form['form_cpf'] and not request.form['form_email']):
            flash("Preencher os campos em branco!!", "error")
            print('test2')

        else:
            print("teste 3")
            cpf = request.form.get('form_cpf').strip()
            # Se o CPF do funcionario atualizado é diferente do CPF que já está no banco, entra nesse if
            if funcionario_atualizado.cpf != cpf:
                print("teste 4")
                cpf_existe = db_sesion.execute(select(Funcionario).where(Funcionario.cpf == cpf)).scalar()
                if cpf_existe:
                    print("teste 5")
                    flash("Este CPF já está cadastrado!!", "error")
                    return redirect(url_for('criar_funcionario'))

            telefone = request.form.get('form_telefone').strip()
            # Se o telefone atualizado é diferente do telefone já cadastrado do banco de dados, entra nesse if
            if funcionario_atualizado.telefone != telefone:
                print("teste 7")
                telefone_existe = db_sesion.execute(
                    select(Funcionario).where(Funcionario.telefone == telefone)).scalar()
                if telefone_existe:
                    print('test 8')
                    flash("Este telefone já está cadastrado!!", "error")
                    return redirect(url_for('criar_funcionario'))

            email = request.form.get('form_email').strip()
            # Se o email atualizado é diferente do email já cadastrado no banco de dados, entra nesse if
            if funcionario_atualizado.email != email:
                email_existe = db_sesion.execute(select(Funcionario).where(Funcionario.email == email)).scalar()
                if email_existe:
                    print("teste9")
                    flash("Este email já está cadastrado!!", "error")
                    return redirect(url_for('criar_funcionario'))

            # Atualiza os campos do produto
            funcionario_atualizado.nome = request.form.get('form_nome')
            funcionario_atualizado.telefone = request.form.get('form_telefone').strip()
            funcionario_atualizado.ano_de_nascimento = request.form.get('form_anoNasci')
            funcionario_atualizado.endereco = request.form.get('form_endereco')
            funcionario_atualizado.cpf = request.form.get('form_cpf').strip()
            funcionario_atualizado.email = request.form.get('form_email').strip()

            # Salva as alterações no banco de dados
            funcionario_atualizado.save()
            # db_sesion.commit()
            flash("Modificações salvas!!", "success")

            # Redireciona para a página de produtos
            return redirect(url_for('funcionarios'))

    # Renderiza o template de edição de produto com os dados do produto e das categorias
    return render_template('editar_funcionario.html', var_funcionario=funcionario_atualizado)


@app.route('/movimentacoes', methods=['GET'])
def movimentacoes():
    sql_movimentacao = (select(Movimentacao, Produto, Funcionario)
                        .join(Produto, Movimentacao.produto_id == Produto.id)
                        .join(Funcionario, Movimentacao.funcionario_id == Funcionario.id)
                        )

    resultado_movimentacao = db_sesion.execute(sql_movimentacao).scalars().all()
    print(resultado_movimentacao)
    return render_template('lista_movimentacao.html',
                           movimentacao_banco=resultado_movimentacao)


@app.route('/entra_sai', methods=['GET'])
def entra_sai(Movimentacao, estoque_banco, estoque_atual, movimentacoes):
    estoque_banco.quantidade = estoque_atual
    estoque_banco.save()
    form_criar = Movimentacao(quantidade=int(request.form.get('form_quantidade')),
                              status=request.form.get('form_status'),
                              data=request.form.get('form_data'),
                              produto_id=int(request.form.get('form_produto_id')),
                              funcionario_id=int(request.form.get('form_funcionario_id')),
                              )
    form_criar.save()
    flash('Movimentação criada com sucesso!', 'sucess')
    return redirect(url_for('movimentacoes'))


@app.route('/nova_movimentacao', methods=["POST", "GET"])
def criar_movimentacao():
    if request.method == "POST":
        print('teste_1')
        if (not request.form['form_quantidade'] and not request.form['form_data']
                and not request.form['form_status'] and not request.form['form_produto_id']
                and not request.form['form_funcionario_id']):
            flash("Preencher os campos em branco!!", "error")

        else:
            print('teste_2')
            quantidade = int(request.form.get('form_quantidade'))
            produto_id = int(request.form.get('form_produto_id'))
            status = request.form.get('form_status')
            print('resultado:: ', quantidade, produto_id, status)

            estoque_banco = select(Produto).filter_by(id=produto_id)
            estoque_banco = db_sesion.execute(estoque_banco).scalar()
            print('Produtos:', estoque_banco.nome, estoque_banco.quantidade)
            if status == 'Saida':
                if estoque_banco.quantidade >= quantidade:
                    print('teste_4')
                    estoque_atual = estoque_banco.quantidade - quantidade
                    entra_sai(Movimentacao, estoque_banco, estoque_atual, movimentacoes)

                else:
                    flash('Quantidade insuficiente no estoque!', 'error')
                    print('nao pode')
            else:
                print('tipooooo::', estoque_banco.quantidade)
                estoque_atual = estoque_banco.quantidade + quantidade
                entra_sai(Movimentacao, estoque_banco, estoque_atual, movimentacoes)

    lista_produto = select(Produto).select_from(Produto)
    lista_produto = db_sesion.execute(lista_produto).scalars()
    resultado_produto = []

    for produto in lista_produto:
        resultado_produto.append(produto.serialize_user())

    lista_funcionario = select(Funcionario).select_from(Funcionario)
    lista_funcionario = db_sesion.execute(lista_funcionario).scalars()
    resultado_funcionario = []

    for funcionarios in lista_funcionario:
        resultado_funcionario.append(funcionarios.serialize_user())

    return render_template("cadastro_de_movimentacao.html",
                           var_produto=resultado_produto, var_funcionario=resultado_funcionario)


@app.route('/editar_movimentacao/<int:id>', methods=["POST", "GET"])
def editar_movimentacao(id):
    # Obtém o produto pelo ID
    movimentacao_atualizado = db_sesion.execute(select(Movimentacao).where(Movimentacao.id == id)).scalar()

    if not movimentacao_atualizado:
        flash("Movimentação não encontrada!", "error")
        return redirect(url_for('movimentacoes'))

    if request.method == "POST":
        # Verifica se todos os campos necessários foram preenchidos
        if (not request.form['form_quantidade'] and not request.form['form_data'] and
                not request.form['form_status'] and not request.form['form_produto_id'] and
                not request.form['form_funcionario_id']):
            flash("Preencher os campos em branco!!", "error")
        else:
            # Atualiza os campos da movimentação
            movimentacao_atualizado.quantidade = request.form.get('form_quantidade')
            movimentacao_atualizado.data = request.form.get('form_data')
            movimentacao_atualizado.status = request.form.get('form_status')
            movimentacao_atualizado.produto_id = request.form.get('form_produto_id')
            movimentacao_atualizado.funcionario_id = request.form.get('form_funcionario_id')

            # Salva as alterações no banco de dados
            movimentacao_atualizado.save()
            db_sesion.commit()
            flash("Modificações salvas!!", "success")

            # Redireciona para a página de movimentações
            return redirect(url_for('movimentacoes'))

    # Obtém a lista de produtos para exibir no formulário de edição
    produto_cad = select(Produto).filter_by(id=movimentacao_atualizado.produto_id)
    produto_cad = db_sesion.execute(produto_cad).scalar()
    lista_produtos = select(Produto).select_from(Produto)
    lista_produto = db_sesion.execute(lista_produtos).scalars()
    resultado_produto = [produto.serialize_user() for produto in lista_produto]

    # Obtém a lista de funcionários para exibir no formulário de edição
    funcionario_cad = select(Funcionario).filter_by(id=movimentacao_atualizado.funcionario_id)
    funcionario_cad = db_sesion.execute(funcionario_cad).scalar()
    lista_funcionarios = select(Funcionario).select_from(Funcionario)
    lista_funcionario = db_sesion.execute(lista_funcionarios).scalars()
    resultado_funcionario = [funcionario.serialize_user() for funcionario in lista_funcionario]

    # Renderiza o template de edição de movimentação com os dados do produto e dos funcionários
    return render_template('editar_movimentacao.html', var_movimentacao=movimentacao_atualizado,
                           var_produto=resultado_produto, produto_atual=produto_cad,
                           var_funcionario=resultado_funcionario,
                           funcionario_atual=funcionario_cad)


@app.route('/categorias', methods=['GET'])
def categorias():
    sql_categorias = select(Categoria)
    resultado_categorias = db_sesion.execute(sql_categorias).scalars()
    lista_categorias = []
    for x in resultado_categorias:
        lista_categorias.append(x.serialize_user())
        print(lista_categorias[-1])
    return render_template("lista_categoria.html",
                           categorias_banco=lista_categorias)


@app.route('/nova_categoria', methods=["POST", "GET"])
def criar_categoria():
    if request.method == "POST":

        if not request.form['form_nome']:
            flash("Preencher o campo em branco!!", "error")

        else:
            form_criar = Categoria(nome=request.form.get('form_nome'),
                                   )
            form_criar.save()
            db_sesion.close()
            flash("Evento criado!!", "success")

            return redirect(url_for('categorias'))

    return render_template('cadastro_de_categoria.html')


@app.route('/editar_categoria/<int:id>', methods=["POST", "GET"])
def editar_categoria(id):
    # Obtém a categoria pelo ID
    categoria_atualizada = db_sesion.execute(select(Categoria).where(Categoria.id == id)).scalar()

    if not categoria_atualizada:
        flash("Categoria não encontrada!", "error")
        return redirect(url_for('categorias'))

    if request.method == "POST":
        # Verifica se todos os campos necessários foram preenchidos
        if (not request.form['form_nome']):
            flash("Preencher o campo em branco!!", "error")
        else:
            # Atualiza os campos do produto
            categoria_atualizada.nome = request.form.get('form_nome')

            # Salva as alterações no banco de dados
            categoria_atualizada.save()
            db_sesion.commit()
            flash("Modificações salvas!!", "success")

            # Redireciona para a página de produtos
            return redirect(url_for('categorias'))
    return render_template('editar_categoria.html', var_categoria=categoria_atualizada)


if __name__ == "__main__":
    app.run(debug=True)
