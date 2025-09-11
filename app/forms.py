from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange, ValidationError
from app import bcrypt, db
from app.models import User, Aluno, Livro
from flask import flash

class UserForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    sobrenome = StringField('Sobrenome', validators=[DataRequired()])
    cadastro = StringField('Número de cadastro', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    confirmacao = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('senha')])
    btnSubmit = SubmitField('Enviar')
    
    def save(self):
        senha_hash = bcrypt.generate_password_hash(self.senha.data.encode('utf-8'))
        user = User(
            nome = self.nome.data,
            sobrenome = self.sobrenome.data,
            cadastro = self.cadastro.data,
            senha = senha_hash
        )
        
        db.session.add(user)
        db.session.commit()
        return user

class LoginForm(FlaskForm):
    cadastro = StringField('Número de cadastro', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    btnSubmit = SubmitField('Enviar')
    
    def login(self):
        user = User.query.filter_by(cadastro=self.cadastro.data).first()
        if user:
            if bcrypt.check_password_hash(user.senha, self.senha.data.encode('utf-8')):
                return user
            else:
                flash("Senha incorreta!", "danger")
                return None
        else:
            flash("Usuário não encontrado!", "danger")
            return None
        
class LivroForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), Length(min=2, max=100)])
    autor = StringField('Autor', validators=[DataRequired(), Length(min=2, max=100)])
    editora = StringField('Editora', validators=[DataRequired(), Length(min=2, max=100)])
    ano_publicacao = IntegerField('Ano de Publicação', validators=[DataRequired(), NumberRange(min=1000, max=2025, message='Insira um ano válido.')])
    genero = StringField('Gênero', validators=[DataRequired(), Length(min=2, max=50)])
    exemplares = IntegerField('Nº de Exemplares Disponíveis', validators=[DataRequired(), NumberRange(min=0, message='O número de exemplares não pode ser negativo.')])
    btnSubmit = SubmitField('Salvar')
    
class AlunoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=2, max=100)])
    sobrenome = StringField('Sobrenome', validators=[DataRequired(), Length(min=2, max=100)])
    cpf = StringField('CPF', validators=[DataRequired(), Length(min=11, max=14, message='CPF deve ter entre 11 e 14 caracteres.')])
    btnSubmit = SubmitField('Salvar')
    
    def validate_cpf(self, cpf):
        aluno = Aluno.query.filter_by(cpf=cpf.data).first()
        if aluno:
            raise ValidationError('Este CPF já está cadastrado. Por favor, utilize outro.')
        
class EmprestimoForm(FlaskForm):
    aluno = SelectField('Aluno', coerce=int, validators=[DataRequired()])
    livro = SelectField('Livro', coerce=int, validators=[DataRequired()])
    btnSubmit = SubmitField('Registrar Empréstimo')