from app import app, db
from flask import render_template, url_for, redirect, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import UserForm, LoginForm, LivroForm, AlunoForm, EmprestimoForm
from app.models import Livro, Aluno, Aluguel
from sqlalchemy import or_, func, desc
from datetime import datetime, timedelta

#ROTA PARA A PAGINA PRINCIPAL
@app.route('/', methods=['GET', 'POST'])
def homepage():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = form.login()
        login_user(user, remember=True)
        return redirect(url_for('homepage'))
    
    return render_template('index.html', form=form)

# ROTA PARA CADASTRA UMA CONTA DE FUNCIONARIO
@app.route("/cadastrar", methods=['GET', 'POST'])
def cadastrar():
    form = UserForm()
    if form.validate_on_submit():
        user = form.save()
        login_user(user, remember=True)
        return redirect(url_for('homepage'))
    return render_template('cadastrar.html', form=form)

# ROTA PARA DAR LOGOUT
@app.route('/sair')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))

# ROTA PARA LISTAR E BUSCAR OS LIVROS
@app.route('/livros')
@login_required
def listar_livros():
    query = request.args.get('q')
    
    if query:
        search = f"%{query}%"
        livros = Livro.query.filter(
            or_(
                Livro.titulo.ilike(search),
                Livro.autor.ilike(search),
                Livro.genero.ilike(search)
            )
        ).all()
    else:
        livros = Livro.query.all()
        
    return render_template('livros.html', livros=livros)


# ROTA PARA CADASTRAR UM NOVO LIVRO
@app.route('/livros/cadastrar', methods=['GET', 'POST'])
@login_required 
def cadastrar_livro():
    form = LivroForm()
    if form.validate_on_submit():
        # Cria um novo objeto Livro com os dados do formulário
        novo_livro = Livro(
            titulo=form.titulo.data,
            autor=form.autor.data,
            editora=form.editora.data,
            ano_publicacao=form.ano_publicacao.data,
            genero=form.genero.data,
            exemplares=form.exemplares.data
        )
        db.session.add(novo_livro)
        db.session.commit()
        flash('Livro cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_livros'))
        
    return render_template('cadastrar_editar_livro.html', form=form, title='Cadastrar Novo Livro')


# ROTA PARA EDITAR UM LIVRO EXISTENTE
@app.route('/livros/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_livro(id):
    # Busca o livro pelo ID ou retorna erro 404 se não encontrar
    livro = Livro.query.get_or_404(id)
    form = LivroForm()
    
    if form.validate_on_submit():
        # Atualiza os dados do livro com as informações do formulário
        livro.titulo = form.titulo.data
        livro.autor = form.autor.data
        livro.editora = form.editora.data
        livro.ano_publicacao = form.ano_publicacao.data
        livro.genero = form.genero.data
        livro.exemplares = form.exemplares.data
        db.session.commit()
        flash('Livro atualizado com sucesso!', 'success')
        return redirect(url_for('listar_livros'))
    
    elif request.method == 'GET':
        # Se for a primeira vez que a página é carregada (GET),
        # preenche o formulário com os dados atuais do livro
        form.titulo.data = livro.titulo
        form.autor.data = livro.autor
        form.editora.data = livro.editora
        form.ano_publicacao.data = livro.ano_publicacao
        form.genero.data = livro.genero
        form.exemplares.data = livro.exemplares

    return render_template('cadastrar_editar_livro.html', form=form, title=f'Editar Livro: {livro.titulo}')


# ROTA PARA EXCLUIR UM LIVRO
@app.route('/livros/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_livro(id):
    livro = Livro.query.get_or_404(id)
    db.session.delete(livro)
    db.session.commit()
    flash('Livro excluído com sucesso.', 'info')
    return redirect(url_for('listar_livros'))

@app.route('/alunos')
@login_required
def listar_alunos():
    query = request.args.get('q')
    if query:
        search = f"%{query}%"
        alunos = Aluno.query.filter(
            or_(
                Aluno.nome.ilike(search),
                Aluno.sobrenome.ilike(search),
                Aluno.cpf.ilike(search)
            )
        ).all()
    else:
        alunos = Aluno.query.all()
    return render_template('alunos.html', alunos=alunos)

# ROTA PARA CADASTRAR UM NOVO ALUNO
@app.route('/alunos/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar_aluno():
    form = AlunoForm()
    if form.validate_on_submit():
        novo_aluno = Aluno(
            nome=form.nome.data,
            sobrenome=form.sobrenome.data,
            cpf=form.cpf.data
        )
        db.session.add(novo_aluno)
        db.session.commit()
        flash('Aluno cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_alunos'))
    return render_template('cadastrar_editar_aluno.html', form=form, title='Cadastrar Novo Aluno')

# ROTA PARA EDITAR UM ALUNO EXISTENTE
@app.route('/alunos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_aluno(id):
    aluno = Aluno.query.get_or_404(id)
    form = AlunoForm()

    # Validação customizada para edição: ignora o CPF do próprio aluno
    if form.validate_on_submit():
        aluno_existente = Aluno.query.filter(Aluno.cpf == form.cpf.data, Aluno.id != id).first()
        if aluno_existente:
            flash('Este CPF já pertence a outro aluno.', 'danger')
        else:
            aluno.nome = form.nome.data
            aluno.sobrenome = form.sobrenome.data
            aluno.cpf = form.cpf.data
            db.session.commit()
            flash('Dados do aluno atualizados com sucesso!', 'success')
            return redirect(url_for('listar_alunos'))
            
    elif request.method == 'GET':
        form.nome.data = aluno.nome
        form.sobrenome.data = aluno.sobrenome
        form.cpf.data = aluno.cpf
        
    return render_template('cadastrar_editar_aluno.html', form=form, title=f'Editar Aluno: {aluno.nome}')

# ROTA PARA EXCLUIR UM ALUNO
@app.route('/alunos/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_aluno(id):
    aluno = Aluno.query.get_or_404(id)
    # VERIFICAÇÃO IMPORTANTE: Não deixa excluir aluno com livros emprestados
    if aluno.livrosEmprestados:
        flash('Não é possível excluir este aluno, pois ele possui livros emprestados.', 'danger')
        return redirect(url_for('listar_alunos'))
        
    db.session.delete(aluno)
    db.session.commit()
    flash('Aluno excluído com sucesso.', 'info')
    return redirect(url_for('listar_alunos'))

@app.route('/emprestimos')
@login_required
def listar_emprestimos():
    # Buscamos apenas os aluguéis que ainda não foram devolvidos
    emprestimos_ativos = Aluguel.query.filter_by(emprestimo_ativo=True).all()
    return render_template('emprestimos.html', emprestimos=emprestimos_ativos)

@app.route('/emprestimos/novo', methods=['GET', 'POST'])
@login_required
def novo_emprestimo():
    form = EmprestimoForm()
    
    # Esta é a parte mais importante: popular os menus dropdown
    # Buscamos apenas livros com exemplares disponíveis
    form.livro.choices = [(livro.id, livro.titulo) for livro in Livro.query.filter(Livro.exemplares > 0).all()]
    form.aluno.choices = [(aluno.id, f"{aluno.nome} {aluno.sobrenome}") for aluno in Aluno.query.all()]

    if form.validate_on_submit():
        livro_id = form.livro.data
        aluno_id = form.aluno.data
        data_aluguel = datetime.now()

        livro = Livro.query.get(livro_id)
        
        # Lógica de negócio: diminuir o número de exemplares
        livro.exemplares -= 1

        novo_aluguel = Aluguel(
            id_livro=livro_id,
            id_aluno=aluno_id,
            data_aluguel=data_aluguel,
            # A data de devolução fica nula até o livro ser devolvido
            data_devolucao=data_aluguel+timedelta(weeks=1)
        )
        
        db.session.add(novo_aluguel)
        db.session.commit()
        flash('Empréstimo registrado com sucesso!', 'success')
        return redirect(url_for('listar_emprestimos'))

    return render_template('novo_emprestimo.html', form=form, title='Registrar Novo Empréstimo')

@app.route('/emprestimos/devolver/<int:id>', methods=['POST'])
@login_required
def devolver_livro(id):
    aluguel = Aluguel.query.get_or_404(id)
    
    # Lógica de negócio: aumentar o número de exemplares
    aluguel.livro.exemplares += 1
    aluguel.emprestimo_ativo = False
    aluguel.data_devolucao = datetime.now()
    db.session.commit()
    flash('Livro devolvido com sucesso!', 'info')
    return redirect(url_for('listar_emprestimos'))

@app.route('/historico', methods=['GET'])
@login_required
def ver_livros():
    emprestimos = Aluguel.query.all()
    return render_template('historico.html', emprestimos=emprestimos)