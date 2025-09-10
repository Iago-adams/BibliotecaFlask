from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo
from app import bcrypt, db
from app.models import User

class UserForm(FlaskForm):
    nome = StringField('Nome', validathors=[DataRequired()])
    sobrenome = StringField('Sobrenome', validators=[DataRequired()])
    cadastro = StringField('Número de cadastro', validators=[DataRequired])
    senha = PasswordField('Senha', validathors=[DataRequired()])
    confirmacao = PasswordField('Senha', validators=[DataRequired(), EqualTo('senha')])
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
                raise Exception("Senha incorreta!")
        else:
            raise Exception("Usuário não encontrado!")