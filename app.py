from flask import Flask, render_template, url_for, request, redirect, flash
from sqlalchemy import select, func
from models import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SENHA'


@app.route("/")
def index():
    return render_template("base.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/inicio")
def inicio():
    return render_template("inicio.html")

@app.route('/produtos', methods=['GET'])
def produtos():
    sql_produtos = (select(Produto, Categoria)
                    .join(Categoria, Produto.categoria_id == Categoria.id))
    resultado_produtos = db_sesion.execute(sql_produtos).scalars().all()
    print(resultado_produtos)
    return render_template('lista_produtos.html',
                           produtos_banco=resultado_produtos)


@app.route('/novo_produto', methods=["POST", "GET"])
def criar_produto():
    if request.method == "POST":

        if (not request.form['form_nome'] or not request.form['form_marca']
                or not request.form['form_descricao'] or not request.form['form_valor']
                or not request.form['form_codigo'] or not request.form['form_categoria_id']):
            flash("Preencher os campos em branco!!", "error")

        else:


            form_criar = Produto(nome=request.form.get('form_nome'),
                                 marca=request.form.get('form_marca'),
                                 descricao=request.form.get('form_descricao'),
                                 valor=float(request.form.get('form_valor')),
                                 codigo=int(request.form.get('form_codigo')),
                                 categoria_id=int(request.form.get('form_categoria_id')),
                                 )
            form_criar.save()
            db_sesion.close()
            flash("Evento criado!!", "success")

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
        if (not request.form['form_nome'] or not request.form['form_marca'] or
                not request.form['form_descricao'] or not request.form['form_valor'] or
                not request.form['form_codigo'] or not request.form['form_categoria_id']):
            flash("Preencher os campos em branco!!", "error")
        else:
            # Atualiza os campos do produto
            produto_atualizado.nome = request.form.get('form_nome')
            produto_atualizado.marca = request.form.get('form_marca')
            produto_atualizado.descricao = request.form.get('form_descricao')
            produto_atualizado.valor = request.form.get('form_valor')
            produto_atualizado.codigo = request.form.get('form_codigo')
            produto_atualizado.categoria_id = request.form.get('form_categoria_id')

            # Salva as alterações no banco de dados
            produto_atualizado.save()
            db_sesion.commit()
            flash("Modificações salvas!!", "success")

            # Redireciona para a página de produtos
            return redirect(url_for('produtos'))

    # Obtém a lista de categorias para exibir no formulário de edição
    lista_categorias = select(Categoria).select_from(Categoria)
    lista_categoria = db_sesion.execute(lista_categorias).scalars()
    resultado_categoria = [categoria.serialize_user() for categoria in lista_categoria]

    # Renderiza o template de edição de produto com os dados do produto e das categorias
    return render_template('cadastro_de_produto.html', var_produto=produto_atualizado,
                           var_categoria=resultado_categoria)

    print(var_produto)


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

        if not request.form['form_nome'] or not request.form['form_telefone'] or not request.form[
            'form_anoNasci'] or not request.form['form_endereco'] or not request.form['form_cpf'] or not request.form[
            'form_email']:
            flash("Preencher os campos em branco!!", "error")

        else:
            form_criar = Funcionario(nome=request.form.get('form_nome'),
                                     telefone=request.form.get('form_telefone'),
                                     ano_de_nascimento=int(request.form.get('form_anoNasci')),
                                     endereco=request.form.get('form_endereco'),
                                     cpf=request.form.get('form_cpf'),
                                     email=request.form.get('form_email'),
                                     )
            form_criar.save()
            db_sesion.close()
            flash("Evento criado!!", "success")

            return redirect(url_for('funcionarios'))

    return render_template('cadastro_de_funcionario.html')


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


@app.route('/nova_movimentacao', methods=["POST", "GET"])
def criar_movimentacao():
    if request.method == "POST":

        if (not request.form['form_quantidade'] or not request.form['form_data']
                or not request.form['form_status'] or not request.form['form_produto_id']
                or not request.form['form_funcionario_id']):
            flash("Preencher os campos em branco!!", "error")

        else:

            quantidade=int(request.form.get('form_quantidade'))
            produto_id=int(request.form.get('form_produto_id'))
            status=request.form.get('form_status')

            entradas = db_sesion.query(func.sum(Movimentacao.quantidade)).filter_by(produto_id=produto_id,
                                                                                    status="entrada").scalar() or 0

            saidas = db_sesion.query(func.sum(Movimentacao.quantidade)).filter_by(produto_id=produto_id,
                                                                                    status="saida").scalar() or 0

            estoque_atual= entradas - saidas


            if status == "saida" and estoque_atual < quantidade:
                flash('Quantidade insuficiente no estoque!', 'error')

            else:
                form_criar = Movimentacao(quantidade=quantidade,
                                            status=status,
                                            data=request.form.get('form_data'),
                                            produto_id=produto_id,
                                            funcionario_id=int(request.form.get('form_funcionario_id')),
                                          )
                form_criar.save()

                flash('Movimentação criada com sucesso!', 'sucess')
                return redirect(url_for('movimentacoes'))


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


if __name__ == "__main__":
    app.run(debug=
True)



