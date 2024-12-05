from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, Boolean
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

#'sqlite:///nome.sqlite3' = nome do meu banco de dados
#configurar banco de dados
#criando conexão
engine = create_engine('sqlite:///controle_estoque.sqlite3')
db_sesion = scoped_session(sessionmaker(bind=engine))

#ela permite que você defina classes Python que representam tabelas de banco de dados
#de forma declarativa, sem a necessidade de configurar manualmente a relação entre as classes e tabelas
Base = declarative_base()
Base.query = db_sesion.query_property()


#class = representação do que tem no banco de dados
#class sempre com letra maiuscula e no singular
#index é para fazer pesquisa
#string é o texto, o que tá dentro do (), significa a quantidade de letras que o texto pode ter

class Funcionario(Base):
    __tablename__ = 'funcionarios'
    id = Column(Integer, primary_key=True)
    nome = Column(String(40), nullable=False, index=True)
    telefone = Column(String(11), nullable=False, index=True, unique=True)
    ano_de_nascimento = Column(Integer, nullable=False, index=True)
    endereco = Column(String(40), nullable=False, index=True)
    cpf = Column(String(11), nullable=False, index=True, unique=True)
    email = Column(String(50), nullable=False, index=True, unique=True)

    def __repr__(self):
        return '<Funcionario: Nome: {} CPF: {}>'.format(self.nome, self.cpf)

    def save(self):
        db_sesion.add(self)
        db_sesion.commit()

    def delete(self):
        db_sesion.delete(self)
        db_sesion.commit()

    def serialize_user(self):
        dados_funcionario = {
            'id': self.id,
            'nome': self.nome,
            'telefone': self.telefone,
            'ano_de_nascimento': self.ano_de_nascimento,
            'endereco': self.endereco,
            'cpf': self.cpf,
            'email': self.email,
        }

        return dados_funcionario


class Categoria(Base):
    __tablename__ = 'categorias'
    id = Column(Integer, primary_key=True)
    nome = Column(String(40), nullable=False, index=True)

    def __repr__(self):
        return '<Categoria: Nome: {}>'.format(self.nome)

    def save(self):
        db_sesion.add(self)
        db_sesion.commit()

    def delete(self):
        db_sesion.delete(self)
        db_sesion.commit()

    def serialize_user(self):
        dados_categoria = {
            'id': self.id,
            'nome': self.nome,
        }

        return dados_categoria


class Produto(Base):
    __tablename__ = 'produtos'
    id = Column(Integer, primary_key=True)
    nome = Column(String(40), nullable=False, index=True)
    marca = Column(String(40), nullable=False, index=True)
    descricao = Column(String(40), nullable=False, index=True)
    quantidade = Column(Integer)
    valor = Column(Float, nullable=False, index=True)
    codigo = Column(Integer, nullable=False, index=True, unique=True)
    categoria_id = Column(Integer, ForeignKey('categorias.id'))
    categorias = relationship('Categoria')

    def __repr__(self):
        return '<Produto: ID: {} Nome: {} Código: {}>'.format(self.id, self.nome, self.codigo)

    def save(self):
        db_sesion.add(self)
        db_sesion.commit()

    def delete(self):
        db_sesion.delete(self)
        db_sesion.commit()

    def serialize_user(self):
        dados_produto = {
            'id': self.id,
            'nome': self.nome,
            'marca': self.marca,
            'descricao': self.descricao,
            'valor': self.valor,
            'codigo': self.codigo,
            'categoria_id': self.categoria_id,
            'categorias': self.categorias,
        }

        return dados_produto


class Movimentacao(Base):
    __tablename__ = 'movimentacao'
    id = Column(Integer, primary_key=True)
    quantidade = Column(Integer, nullable=False, index=True)
    data = Column(String(10), nullable=False, index=True, autoincrement=True)
    status = Column(String(10), nullable=False)

    produto_id = Column(Integer, ForeignKey('produtos.id'))
    produtos = relationship('Produto')

    funcionario_id = Column(Integer, ForeignKey('funcionarios.id'))
    funcionarios = relationship('Funcionario')

    def __repr__(self):
        return '<Movimentacao: Status: {} Produto_id: {} Funcionário: {}>'.format(self.status, self.produto_id, self.funcionario_id)

    def save(self):
        db_sesion.add(self)
        db_sesion.commit()

    def delete(self):
        db_sesion.delete(self)
        db_sesion.commit()

    def serialize_user(self):
        dados_movimentacao = {
            'id': self.id,
            'funcionario_id': self.funcionario_id,
            'funcionarios':self.funcionarios,
            'quantidade': self.quantidade,
            'status': self.status,
            'data': self.data,
            'produto_id': self.produto_id,
            'produtos': self.produtos,
        }

        return dados_movimentacao


def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()