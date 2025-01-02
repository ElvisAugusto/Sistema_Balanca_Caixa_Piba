from datetime import datetime
from application import db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateTimeField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, ValidationError


# Formulário de login
class LoginForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(),
                                              Email()])  # Campo de email com validação de presença e formato de email
    senha = PasswordField('Senha:', validators=[DataRequired()])  # Campo de senha com validação de presença
    entrar = SubmitField('Entrar')  # Botão de submissão para login


# Formulário de cadastro
class CadastroForm(FlaskForm):
    nome = StringField('Nome:', validators=[DataRequired()])  # Campo de nome com validação de presença
    email = StringField('Email:', validators=[DataRequired(),
                                              Email()])  # Campo de email com validação de presença e formato de email
    senha = PasswordField('Senha:', validators=[DataRequired()])  # Campo de senha com validação de presença
    cadastrar = SubmitField('Cadastrar')  # Botão de submissão para cadastro


# Formulário de menu
class Menu(FlaskForm):
    botaoBalanca = SubmitField('Balança')  # Botão para acessar a funcionalidade de Balança
    botaoCaixa = SubmitField('Caixa')  # Botão para acessar a funcionalidade de Caixa
    botaoRelatorio = SubmitField('Relatório')  # Botão para acessar a funcionalidade de Relatório
    botaoLogout = SubmitField('Logout')  # Botão para fazer logout do sistema


# Formulário para adicionar valores
class AddValueForm(FlaskForm):
    id_comanda = IntegerField('ID da comanda:', validators=[
        DataRequired()])  # Campo de entrada para o ID da comanda com validação de presença
    nome_comanda = StringField('Nome da comanda:', validators=[
        DataRequired()])  # Campo de entrada para o nome da comanda com validação de presença
    valor_refeicao = StringField('Valor refeição:', validators=[
        DataRequired()])  # Campo de entrada para o valor da refeição com validação de presença
    tipo_bebida = SelectField('Bebida:', choices=[('Água - R$ 2,50'), ('Refri.de Limão - R$ 5,00'), ('Refri.de Lata - R$ 4,00'), ('Caçulinha - R$ 2,50'), ('Suco - R$ 3,00')],
                              validators=[
                                  DataRequired()])  # Campo de seleção para o tipo de bebida com opções pré-definidas e validação de presença
    quantidade_bebida = IntegerField('Quantidade:', validators=[
        DataRequired()])  # Campo de entrada para a quantidade de bebida com validação de presença
    adicionar = SubmitField('Adicionar')  # Botão de submissão para adicionar valores
    confirmar = SubmitField('Confirmar')  # Botão de submissão para confirmar a adição de valores
    limpar = SubmitField('Limpar')  # Botão de submissão para limpar os campos do formulário
    voltar_menu = SubmitField('Voltar menu')  # Botão de submissão para voltar ao menu principal


# Formulário para operações de caixa
class CaixaForm(FlaskForm):
    id_refeicao = StringField('ID da comanda:', validators=[
        DataRequired()])  # Campo de entrada para o ID da comanda com validação de presença
    nome_comanda = StringField('Buscar por nome:', validators=[
        DataRequired()])  # Campo de entrada para buscar por nome com validação de presença
    buscar = SubmitField('Buscar')  # Botão de submissão para buscar a comanda pelo ID ou nome
    voltar_menu = SubmitField('Voltar menu')  # Botão de submissão para voltar ao menu principal
    cancelar = SubmitField('Cancelar')  # Botão de submissão para cancelar a operação
    realizar_pagamento = SubmitField('Realizar Pagamento')  # Botão de submissão para realizar o pagamento
    forma_pagamento = SelectField('Forma de Pagamento: ', choices=[('Cartão'), ('Dinheiro'), ('Pix')],
                                  validators=[DataRequired()])  # Campo de seleção para escolher a forma de pagamento


# Formulário para geração de relatórios
class RelatorioForm(FlaskForm):
    data_inicial = DateTimeField('Data Inicial:', validators=[DataRequired()], format='%Y-%m-%dT%H:%M',
                                 default=datetime.now)  # Campo de data inicial com validação de presença e formato específico
    data_final = DateTimeField('Data Final:', validators=[DataRequired()], format='%Y-%m-%dT%H:%M',
                               default=datetime.now)  # Campo de data final com validação de presença e formato específico
    gerar_relatorio = SubmitField('Gerar Relatório')  # Botão de submissão para gerar relatório
    voltar_menu = SubmitField('Voltar Menu')  # Botão de submissão para voltar ao menu

    # Validação personalizada para garantir que a data final não seja menor que a data inicial
    def validate_data_final(form, field):
        if field.data < form.data_inicial.data:
            raise ValidationError('A data final não pode ser menor que a data inicial.')


# Modelo para usuários
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Chave primária autoincrementada
    nome = db.Column(db.String(50), nullable=False)  # Campo de nome, não pode ser nulo
    email = db.Column(db.String(50), unique=True, nullable=False)  # Campo de email, deve ser único e não pode ser nulo
    senha = db.Column(db.String(50), nullable=False)  # Campo de senha, não pode ser nulo
    permissao = db.Column(db.String(15), nullable=False)

    # Método para representação em string do objeto
    def __repr__(self):
        return f'<Usuario {self.nome}>'


# Modelo para registros da balança
class Balanca(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Chave primária autoincrementada
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'),
                           nullable=False)  # Chave estrangeira referenciando o ID do usuário
    nome_comanda = db.Column(db.String(100), nullable=False)  # Campo para o nome da comanda, não pode ser nulo
    numero_refeicoes = db.Column(db.Integer, nullable=False)  # Campo para o número de refeições, não pode ser nulo
    total_refeicoes = db.Column(db.Float, nullable=False)  # Campo para o total de refeições, não pode ser nulo
    forma_pagamento = db.Column(db.String(50), nullable=True)  # Campo para a forma de pagamento, pode ser nulo
    data = db.Column(db.DateTime, nullable=False,
                     default=datetime.now)  # Campo para a data, não pode ser nulo, valor padrão é a data e hora atual

    # Método para representação em string do objeto
    def __repr__(self):
        return f'<Balanca {self.id}>'


class Bebida(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Chave primária
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'),
                           nullable=False)  # Chave estrangeira referenciando o ID do usuário
    nome_comanda = db.Column(db.String(100), nullable=False)  # Campo para o nome da comanda, não pode ser nulo
    numero_bebidas = db.Column(db.Integer, nullable=False)  # Campo para o número de refeições, não pode ser nulo
    tipo_bebida = db.Column(db.String(15), nullable=False)  # Campo para o tipo de bebida, não pode ser nulo
    total_bebidas = db.Column(db.Float, nullable=False)  # Campo para o total de refeições, não pode ser nulo
    forma_pagamento = db.Column(db.String(15), nullable=True)  # Campo para a forma de pagamento, pode ser nulo
    data = db.Column(db.DateTime, nullable=False,
                     default=datetime.now)  # Campo para a data, não pode ser nulo, valor padrão é a data e hora atual

    # Método para representação em string do objeto
    def __repr__(self):
        return f'<Bebidas {self.id}>'
