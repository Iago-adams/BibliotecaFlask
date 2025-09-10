from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    cadastro = db.Column(db.String, nullable=True, unique=True)
    nome = db.Column(db.String, nullable=True)
    sobrenome = db.Column(db.String, nullable=True)
    senha = db.Column(db.String, nullable=True)

class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    autor = db.Column(db.String)
    editora = db.Column(db.String)
    publicacao = db.Column(db.DateTime)
    genero = db.Column(db.String)
    numeroDisponiveis = db.Column(db.Integer)
    alunosAlugados = db.relationship('Aluguel', backref='livro', lazy=True)
    
class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    cpf = db.Column(db.String, unique=True)
    livrosEmprestados = db.relationship('Aluguel', backref='aluno', lazy=True)
    
class Aluguel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_livro = db.Column(db.Integer, db.ForeignKey('livro.id'))
    id_aluno = db.Column(db.Integer, db.ForeignKey('aluno.id'))
    data_aluguel = db.Column(db.DateTime, default=datetime.now)
    data_devolucao = db.Column(db.Date, nullable=True)