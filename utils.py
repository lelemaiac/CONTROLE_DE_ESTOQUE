from models import Funcionario, Categoria, Movimentacao, Produto, db_sesion
from sqlalchemy import select


# Inserir dados na tabela
def inserir_funcionario():
    funcionario = Funcionario(nome=(input('Nome completo: ')),
                              telefone=(input('Telefone: ')),
                              cpf=(input('CPF: ')),
                              ano_de_nascimento=(int(input('Ano de nascimento: '))),
                              endereco=(input('Endereço: ')),
                              email=(input('Email: ')),
                                     )
    print(funcionario)
    funcionario.save()


def consultar_funcionario():
    var_funcionario = select(Funcionario)
    var_funcionario = db_sesion.execute(var_funcionario).all()
    print(var_funcionario)


def atualizar_funcionario():
    var_funcionario = select(Funcionario).where(Funcionario.nome == (input('Nome: ')))
    var_funcionario = db_sesion.execute(var_funcionario).scalar()
    print(var_funcionario)
    var_funcionario.nome = str(input('Novo Nome: '))
    var_funcionario.save()


# remove pessoas

def deletar_funcionario():
    funcionario = Funcionario.query.filter_by(nome=str(input('Nome: '))).first()
    print(funcionario)
    funcionario.delete()


def inserir_categoria():
    categoria = Categoria(nome=(input('Nome: ')),
                          )
    print(categoria)
    categoria.save()


def consultar_categoria():
    var_categoria = select(Categoria)
    var_categoria = db_sesion.execute(var_categoria).all()
    print(var_categoria)


def atualizar_categoria():
    var_categoria = select(Categoria).where(Categoria.nome == (input('Nome: ')))
    var_categoria = db_sesion.execute(var_categoria).scalar()
    print(var_categoria)
    var_categoria.nome = str(input('Novo Nome: '))
    var_categoria.save()


# remove pessoas

def deletar_categoria():
    categoria = Categoria.query.filter_by(nome=str(input('Nome: '))).first()
    print(categoria)
    categoria.delete()


def inserir_produto():
    produto = Produto(nome=(input('Nome: ')),
                      codigo=(int(input('Código: : '))),
                      marca=(input('Marca: ')),
                      descricao=(input('Descrição: ')),
                      valor=(float(input('Valor: '))),
                      categoria_id=(int(input('Id da categoria: '))),
                      )
    print(produto)
    produto.save()


def consultar_produto():
    var_produto = select(Produto)
    var_produto = db_sesion.execute(var_produto).all()
    print(var_produto)


def atualizar_produto():
    var_produto = select(Produto).where(Produto.nome == str(input('Nome: ')))
    var_produto = db_sesion.execute(var_produto).scalar()
    print(var_produto)
    var_produto.nome = str(input('Novo Nome: '))
    var_produto.save()


# remove pessoas

def deletar_produto():
    produto = Produto.query.filter_by(nome=str(input('Nome: '))).first()
    print(produto)
    produto.delete()


def inserir_movimentacao():
    movimentacao = Movimentacao(
                                quantidade=(int(input('Quantidade: : '))),
                                status=(input('Status: ')),
                                data=(input('Data: ')),
                                funcionario_id=(int(input('Id do funcionário: '))),
                                produto_id=(int(input('Id do produto: ')))
                                )
    print(movimentacao)
    movimentacao.save()


def consultar_movimentacao():
    var_movimentacao = select(Movimentacao)
    var_movimentacao = db_sesion.execute(var_movimentacao).all()
    print(var_movimentacao)


def atualizar_movimentacao():
    var_movimentacao = select(Movimentacao).where(Movimentacao.status == str(input('Nome: ')))
    var_movimentacao = db_sesion.execute(var_movimentacao).scalar()
    print(var_movimentacao)
    var_movimentacao.nome = str(input('Novo Nome: '))
    var_movimentacao.save()


# remove pessoas

def deletar_movimentacao():
    movimentacao = Movimentacao.query.filter_by(nome=str(input('Nome: '))).first()
    print(movimentacao)
    movimentacao.delete()


if __name__ == '__main__':

    while True:
        print('Menu')
        print('1- Inserir Funcionário')
        print('2- Consultar Funcionário')
        print('3- Atualizar Funcionário')
        print('4- Deletar Funcionário')
        print("")
        print('5- Inserir Categoria')
        print('6- Consultar Categoria')
        print('7- Atualizar Categoria')
        print('8- Deletar Categoria')
        print("")
        print('9- Inserir Produto')
        print('10- Consultar Produto')
        print('11- Atualizar Produto')
        print('12- Deletar Produto')
        print("")
        print('13- Inserir Movimentação')
        print('14- Consultar Movimentação')
        print('15- Atualizar Movimentação')
        print('16- Deletar Movimentação')
        print("")
        print('17- Sair')

        escolha = input('Escolha: ')

        if escolha == '1':
            inserir_funcionario()

        elif escolha == '2':
            consultar_funcionario()

        elif escolha == '3':
            atualizar_funcionario()

        elif escolha == '4':
            deletar_funcionario()
            print("Funcionário deletado")

        elif escolha == '5':
            inserir_categoria()

        elif escolha == '6':
            consultar_categoria()

        elif escolha == '7':
            atualizar_categoria()

        elif escolha == '8':
            deletar_categoria()
            print("Categoria deletada")

        elif escolha == '9':
            inserir_produto()

        elif escolha == '10':
            consultar_produto()

        elif escolha == '11':
            atualizar_produto()

        elif escolha == '12':
            deletar_produto()
            print("Produto deletado")

        elif escolha == '13':
            inserir_movimentacao()

        elif escolha == '14':
            consultar_categoria()

        elif escolha == '15':
            atualizar_movimentacao()

        elif escolha == '16':
            deletar_movimentacao()
            print("Movimentação deletada")

        elif escolha == '17':
            print("Você saiu!!")
            break
