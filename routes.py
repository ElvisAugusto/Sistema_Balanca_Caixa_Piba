from flask import render_template, request, redirect, url_for, flash, session, jsonify
from functions import *
from application import application, db
from models import *
from flask_bcrypt import check_password_hash, generate_password_hash
from sqlalchemy import text
import time

# Lista global para armazenar os valores da refeição
refeicao = {}
bebida = {}
contador = 1
id_existente = 0
nome_existente = "Insira o nome"
max_numero_refeicoes = 0
registro_balanca = None
registro_bebidas = None

# Função para verificar a autenticação do usuário
def verificar_autenticacao():
    if 'usuario_logado' not in session:
        return redirect(url_for('index'))

@application.route('/')
def index():
    # Chama a função de logout para garantir que não haja sessão ativa
    logout()
    return redirect(url_for('login'))
@application.route('/logout')
def logout():
    session.clear()  # Limpa todos os dados da sessão
    return redirect(url_for('index'))  # Redireciona para a página de login

@application.after_request
def add_header(response):
    # Limpar cache nas respostas do Flask
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@application.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Instancia o formulário de login
    if form.validate_on_submit():  # Verifica se o formulário foi submetido e validado
        email = form.email.data
        usuario = Usuario.query.filter_by(email=email).first()  # Busca o usuário pelo e-mail
        if usuario and check_password_hash(usuario.senha,
                                           form.senha.data):  # Verifica se o usuário existe e se a senha está correta
            session['usuario_logado'] = usuario.id  # Armazena o ID do usuário na sessão
            return redirect(url_for('menu'))  # Redireciona para a página menu em caso de sucesso
        else:
            flash('Falha no login! Verifique suas credenciais.', 'error')
            return redirect(url_for('login'))  # Redireciona de volta para a página de login em caso de falha

    return render_template('login.html', form=form)

@application.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    form = CadastroForm()  # Instancia o formulário de cadastro

    if form.validate_on_submit():  # Verifica se o formulário foi submetido e validado
        nome = form.nome.data  # Obtém o nome do formulário
        email = form.email.data  # Obtém o email do formulário
        senha = generate_password_hash(form.senha.data).decode('utf-8')  # Gera o hash da senha e decodifica para string
        permissao = 'Usuario'  # Define a permissão padrão do usuário como 'Usuario'

        # Verifica se o email já está em uso no banco de dados
        usuario_existente = Usuario.query.filter_by(email=email).first()

        if usuario_existente:
            flash('Este email já está em uso.', 'error')  # Exibe mensagem de erro se o email já estiver em uso
            return redirect(url_for('cadastrar'))  # Redireciona para a página de cadastro
        else:
            # Cria uma nova instância do usuário com os dados fornecidos
            novo_usuario = Usuario(nome=nome, email=email, senha=senha, permissao=permissao)

            db.session.add(novo_usuario)  # Adiciona o novo usuário ao banco de dados
            db.session.commit()  # Confirma a transação no banco de dados

            flash('Usuário criado com sucesso!', 'success')  # Exibe mensagem de sucesso
            return redirect(url_for('login'))  # Redireciona para a página de login

    return render_template('cadastro.html', form=form)  # Renderiza o template de cadastro com o formulário

@application.route('/menu', methods=['GET', 'POST'])
def menu():
    # Verifica se o usuário está logado
    if 'usuario_logado' in session:
        form = Menu()  # Instancia o formulário do menu

        # Define o id_existente para a próxima comanda
        # Obtém o maior id da tabela Balanca
        maior_id_balanca = Balanca.query.order_by(Balanca.id.desc()).first().id if Balanca.query.order_by(
            Balanca.id.desc()).first() else 0

        # Obtém o maior id da tabela Bebida
        maior_id_bebida = Bebida.query.order_by(Bebida.id.desc()).first().id if Bebida.query.order_by(
            Bebida.id.desc()).first() else 0

        # Define o maior id entre as duas tabelas
        maior_id = max(maior_id_balanca, maior_id_bebida)

        # Define session['id_existente'] com o maior id mais 1
        session['id_existente'] = maior_id + 1

        # Define session['nome_existente']
        session['nome_existente'] = "Insira o nome"

        # Verifica qual botão foi pressionado no formulário
        if 'botaoBalanca' in request.form:
            return redirect(url_for('balanca'))  # Redireciona para a rota balanca

        elif 'botaoCaixa' in request.form:
            return redirect(url_for('caixa'))  # Redireciona para a rota caixa

        elif 'botaoRelatorio' in request.form:
            return redirect(url_for('relatorio'))  # Redireciona para a rota relatorio

        elif 'botaoLogout' in request.form:
            return redirect(url_for('logout'))  # Redireciona para a rota logout
    else:
        # Se o usuário não estiver logado, redireciona para a página de login
        return redirect(url_for('index'))

    # Renderiza o template do menu com o formulário
    return render_template('menu.html', form=form)
@application.route('/get_nome_comanda', methods=['GET'])
def get_nome_comanda():
    # Obtém o valor do parâmetro 'id_comanda' da query string da solicitação GET
    id_comanda = request.args.get('id_comanda')

    # Verifica se 'id_comanda' possui algum valor
    if not id_comanda:
        # Se 'id_comanda' estiver vazio, retorna uma resposta JSON com nome_comanda=None
        return jsonify(nome_comanda=None)

    # Consulta o banco de dados na tabela Balanca ou Bebida pelo 'id_comanda'
    comanda = Balanca.query.filter_by(id=int(id_comanda)).first() or \
              Bebida.query.filter_by(id=int(id_comanda)).first()

    # Retorna o nome da comanda encontrada ou None se nenhuma comanda foi encontrada
    return jsonify(nome_comanda=comanda.nome_comanda if comanda else None)
@application.route('/balanca', methods=['GET', 'POST'])
def balanca():
    global refeicao, bebida

    # Verifica se o usuário está autenticado
    if verificar_autenticacao():
        return verificar_autenticacao()

    form = AddValueForm()  # Instancia o formulário para adicionar valores

    # Calcula os totais de refeição e bebida
    total_refeicao = sum(refeicao.values())
    total_bebida = sum(total for _, total in bebida.values())
    total = locale.currency(total_refeicao + total_bebida, grouping=True)
    refeicao_valor = {numero: locale.currency(valor, grouping=True) for numero, valor in refeicao.items()}

    # Renderiza a página balanca.html com os dados necessários
    return render_template('balanca.html', form=form, valor=total,
                           refeicao=refeicao_valor, total_refeicao=total_refeicao, bebida=bebida,
                           id_existente=session.get('id_existente'), nome_comanda=session.get('nome_existente'))
@application.route('/add_value', methods=['GET', 'POST'])
def add_value():
    global refeicao, bebida, contador, max_numero_refeicoes

    # Verifica se o usuário está autenticado
    if verificar_autenticacao():
        return verificar_autenticacao()

    form = AddValueForm()  # Instancia o formulário para adicionar valores

    if 'adicionar' in request.form:
        # Lógica para adicionar valores ao pedido

        # Obtém os dados do formulário
        id = form.id_comanda.data
        if id < session['id_existente']:
            session['id_existente'] = id
        session['nome_existente'] = form.nome_comanda.data

        # Verifica se o ID da comanda já possui um nome vinculado no banco de dados
        comanda_balanca = Balanca.query.filter_by(id=session['id_existente']).first()
        # Verifica se o ID da comanda já possui um nome vinculado no banco de dados
        comanda_bebida = Bebida.query.filter_by(id=session['id_existente']).first()

        if comanda_balanca:
            # Se existir, verifica se o nome já está vinculado ao ID
            if comanda_balanca.nome_comanda != session['nome_existente']:
                flash(f"Já existe um nome {comanda_balanca.nome_comanda} vinculado ao ID {session['id_existente']}!")
                # Define o id_existente para a próxima comanda
                # Obtém o maior id da tabela Balanca
                maior_id_balanca = Balanca.query.order_by(Balanca.id.desc()).first().id if Balanca.query.order_by(
                    Balanca.id.desc()).first() else 0

                # Obtém o maior id da tabela Bebida
                maior_id_bebida = Bebida.query.order_by(Bebida.id.desc()).first().id if Bebida.query.order_by(
                    Bebida.id.desc()).first() else 0

                # Define o maior id entre as duas tabelas
                maior_id = max(maior_id_balanca, maior_id_bebida)

                # Define session['id_existente'] com o maior id mais 1
                session['id_existente'] = maior_id + 1

                # Define session['nome_existente']
                session['nome_existente'] = "Insira o nome"
                return redirect(url_for('balanca'))

        elif comanda_bebida:
            if comanda_bebida.nome_comanda != session['nome_existente']:
                flash(f"Já existe um nome {comanda_bebida.nome_comanda} vinculado ao ID {session['id_existente']}!")
                # Define o id_existente para a próxima comanda
                # Obtém o maior id da tabela Balanca
                maior_id_balanca = Balanca.query.order_by(Balanca.id.desc()).first().id if Balanca.query.order_by(
                    Balanca.id.desc()).first() else 0

                # Obtém o maior id da tabela Bebida
                maior_id_bebida = Bebida.query.order_by(Bebida.id.desc()).first().id if Bebida.query.order_by(
                    Bebida.id.desc()).first() else 0

                # Define o maior id entre as duas tabelas
                maior_id = max(maior_id_balanca, maior_id_bebida)

                # Define session['id_existente'] com o maior id mais 1
                session['id_existente'] = maior_id + 1

                # Define session['nome_existente']
                session['nome_existente'] = "Insira o nome"

                return redirect(url_for('balanca'))

        valor_refeicao = form.valor_refeicao.data
        valor_refeicao = float(valor_refeicao.replace(',', '.'))  # Converte o valor da refeição para float
        tipo_bebida = form.tipo_bebida.data
        valor_bebida = float(''.join(filter(lambda x: x.isdigit() or x == ',', tipo_bebida)).replace(',', '.'))
        quantidade_bebida = form.quantidade_bebida.data
        total_bebida = valor_bebida * quantidade_bebida  # Calcula o total da bebida

        # Recupera o máximo número de refeições do banco de dados
        result_max = db.session.execute(text("SELECT MAX(numero_refeicoes) FROM balanca WHERE id = :id_comanda"),
                                        {"id_comanda": session['id_existente']})
        max_numero_refeicoes = result_max.fetchone()[0]

        # Verifica se o nome da comanda foi inserido
        if session['nome_existente'] != "" and session['nome_existente'] != "Insira o nome":
            if valor_refeicao or quantidade_bebida:
                if valor_refeicao:
                    if max_numero_refeicoes is None:
                        numero_refeicao = len(refeicao) + 1  # Identificador único para cada refeição
                        refeicao[numero_refeicao] = valor_refeicao  # Adiciona a refeição ao dicionário
                    else:
                        numero_refeicao = max_numero_refeicoes + contador
                        refeicao[numero_refeicao] = valor_refeicao
                        contador += 1

                if quantidade_bebida:
                    if tipo_bebida in bebida:
                        bebida[tipo_bebida] = (bebida[tipo_bebida][0] + quantidade_bebida, bebida[tipo_bebida][1] + total_bebida)
                    else:
                        bebida[tipo_bebida] = (quantidade_bebida, total_bebida)

                flash('Adicionado!')
                return redirect(url_for('balanca'))
            else:
                flash('Insira um valor!')
                return redirect(url_for('balanca'))
        else:
            flash('Insira o nome!')
            return redirect(url_for('balanca'))

    elif 'confirmar' in request.form:
        # Lógica para confirmar o pedido
        # Verifica se a comanda já existe no banco de dados
        balanca_existente = Balanca.query.filter_by(id=session['id_existente'], nome_comanda=session['nome_existente']).first()
        total_refeicao = sum(refeicao.values())
        total_bebida = sum(total for _, total in bebida.values())
        total_geral = total_refeicao + total_bebida

        if balanca_existente is not None and total_geral != 0:
            try:
                # Adiciona as refeições
                usuario_id = session['usuario_logado']
                for numero, valor in refeicao.items():
                    nova_refeicao = Balanca(id=session['id_existente'], usuario_id=usuario_id, nome_comanda=session['nome_existente'],
                                            numero_refeicoes=numero, total_refeicoes=valor)
                    db.session.add(nova_refeicao)

                # Adiciona ou atualiza as bebidas
                for tipo, (quantidade, total) in bebida.items():
                    bebida_existente = Bebida.query.filter_by(id=session['id_existente'], nome_comanda=session['nome_existente'], tipo_bebida=tipo).first()
                    if bebida_existente:
                        db.session.query(Bebida).filter_by(id=session['id_existente'], nome_comanda=session['nome_existente'], tipo_bebida=tipo).update({
                            Bebida.numero_bebidas: Bebida.numero_bebidas + quantidade,
                            Bebida.total_bebidas: Bebida.total_bebidas + total
                        })
                    else:
                        nova_bebida = Bebida(id=session['id_existente'], usuario_id=usuario_id, nome_comanda=session['nome_existente'],
                                             numero_bebidas=quantidade, tipo_bebida=tipo, total_bebidas=total)
                        db.session.add(nova_bebida)

                db.session.commit()

                # Limpa os dados e reseta os contadores
                bebida.clear()
                refeicao.clear()
                contador = 1
                maior_id_balanca = Balanca.query.order_by(Balanca.id.desc()).first().id if Balanca.query.order_by(
                    Balanca.id.desc()).first() else 0

                # Obtém o maior id da tabela Bebida
                maior_id_bebida = Bebida.query.order_by(Bebida.id.desc()).first().id if Bebida.query.order_by(
                    Bebida.id.desc()).first() else 0

                # Define o maior id entre as duas tabelas
                maior_id = max(maior_id_balanca, maior_id_bebida)

                # Define session['id_existente'] com o maior id mais 1
                session['id_existente'] = maior_id + 1

                # Define session['nome_existente']
                session['nome_existente'] = "Insira o nome"

                max_numero_refeicoes = 0

                flash(f'Itens adicionados ao ID existente!')

                return redirect(url_for('balanca'))

            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao adicionar itens: {e}')
                return redirect(url_for('balanca'))

            finally:
                db.session.remove()
                return redirect(url_for('balanca'))

        elif balanca_existente is None and total_geral != 0:
            # Adiciona uma nova comanda se não existir e há itens para adicionar
            usuario_id = session['usuario_logado']
            for numero, valor in refeicao.items():
                nova_refeicao = Balanca(id=session['id_existente'], usuario_id=usuario_id, nome_comanda=session['nome_existente'],
                                        numero_refeicoes=numero, total_refeicoes=valor)
                db.session.add(nova_refeicao)

            for tipo, (quantidade, total) in bebida.items():
                nova_bebida = Bebida(id=session['id_existente'], usuario_id=usuario_id, numero_bebidas=quantidade,
                                     nome_comanda=session['nome_existente'], tipo_bebida=tipo, total_bebidas=total)
                db.session.add(nova_bebida)

            db.session.commit()

            # Limpa os dados e reseta os contadores
            bebida.clear()
            refeicao.clear()
            maior_id_balanca = Balanca.query.order_by(Balanca.id.desc()).first().id if Balanca.query.order_by(
                Balanca.id.desc()).first() else 0

            # Obtém o maior id da tabela Bebida
            maior_id_bebida = Bebida.query.order_by(Bebida.id.desc()).first().id if Bebida.query.order_by(
                Bebida.id.desc()).first() else 0

            # Define o maior id entre as duas tabelas
            maior_id = max(maior_id_balanca, maior_id_bebida)

            # Define session['id_existente'] com o maior id mais 1
            session['id_existente'] = maior_id + 1

            # Define session['nome_existente']
            session['nome_existente'] = "Insira o nome"

            flash('Compra salva!')
            return redirect(url_for('balanca'))

        else:
            flash("Primeiro precisa adicionar valores para depois confirmar!")
            return redirect(url_for('balanca'))

    elif 'limpar' in request.form:  # Se o botão "Limpar" foi pressionado
        # Lógica para limpar os dados do pedido
        bebida.clear()
        refeicao.clear()

        maior_id_balanca = Balanca.query.order_by(Balanca.id.desc()).first().id if Balanca.query.order_by(
            Balanca.id.desc()).first() else 0

        # Obtém o maior id da tabela Bebida
        maior_id_bebida = Bebida.query.order_by(Bebida.id.desc()).first().id if Bebida.query.order_by(
            Bebida.id.desc()).first() else 0

        # Define o maior id entre as duas tabelas
        maior_id = max(maior_id_balanca, maior_id_bebida)

        # Define session['id_existente'] com o maior id mais 1
        session['id_existente'] = maior_id + 1

        # Define session['nome_existente']
        session['nome_existente'] = "Insira o nome"

        contador = 1
        max_numero_refeicoes = 0

        flash('Lista de refeição limpa!')
        return redirect(url_for('balanca'))

    elif 'voltar_menu' in request.form:  # Se o botão "Voltar menu" foi pressionado
        # Lógica para retornar ao menu principal
        bebida.clear()
        refeicao.clear()
        contador = 1
        max_numero_refeicoes = 0

        return redirect(url_for('menu'))

    # Renderiza a página balanca.html com o formulário, se o formulário não foi submetido ou não é válido
    return render_template('balanca.html', form=form)
@application.route('/caixa', methods=['GET', 'POST'])
def caixa():
    global registro_balanca, registro_bebidas

    if verificar_autenticacao():
        return verificar_autenticacao()  # Redireciona para a página de login se não estiver autenticado

    form = CaixaForm()  # Instancia o formulário de caixa

    if form.validate_on_submit():
        if 'buscar' in request.form:  # Se o botão "Buscar ID" foi pressionado
            session['id_refeicao'] = int(form.id_refeicao.data)
            session['nome_existente'] = form.nome_comanda.data

            if session['id_refeicao'] != 0 and session['nome_existente'] == "Insira o nome":
                registro_balanca = db.session.execute(text("SELECT * FROM balanca WHERE id = :id_comanda"),
                    {"id_comanda": session['id_refeicao']}).fetchall()

                registro_bebidas = db.session.execute(text("SELECT * FROM bebida WHERE id = :id_comanda"),
                    {"id_comanda": session['id_refeicao']}).fetchall()

            elif session['id_refeicao'] == 0 and session['nome_existente'] != "Insira o nome":
                registro_balanca = db.session.execute(text("SELECT * FROM balanca WHERE nome_comanda = :nome_comanda"),
                    {"nome_comanda": session['nome_existente']}).fetchall()

                registro_bebidas = db.session.execute(text("SELECT * FROM bebida WHERE nome_comanda = :nome_comanda"),
                    {"nome_comanda": session['nome_existente']}).fetchall()

            elif session['id_refeicao'] == 0 and session['nome_existente'] == "Insira o nome":

                flash('Insira um valor!')
                return redirect(url_for('caixa'))

            elif session['id_refeicao'] != 0 and session['nome_existente'] != "Insira o nome":

                flash('Escolha apenas um campo para realizar a pesquisa!')
                return redirect(url_for('caixa'))

            # Verifica se algum dos registros possui forma_pagamento definida
            if all(registro.forma_pagamento is None for registro in registro_balanca) and \
                    all(registro.forma_pagamento is None for registro in registro_bebidas):

                if registro_balanca or registro_bebidas:
                    flash('Refeições:')
                    total_refeicoes = 0

                    for registro in registro_balanca:
                        if registro.forma_pagamento is None:
                            total_refeicoes += registro.total_refeicoes
                            flash(
                                f'{registro.numero_refeicoes} - {locale.currency(registro.total_refeicoes, grouping=True)}')

                    flash(f'Total de Refeições: {locale.currency(total_refeicoes, grouping=True)}')

                    flash('Bebidas:')
                    total_bebidas = 0

                    for registro in registro_bebidas:
                        if registro.forma_pagamento is None:
                            total_bebidas += registro.total_bebidas
                            flash(
                                f'{registro.numero_bebidas} - {registro.tipo_bebida} - {locale.currency(registro.total_bebidas, grouping=True)}')

                    flash(f'Total de bebidas: {locale.currency(total_bebidas, grouping=True)}')
                    flash(f'Total a pagar: {locale.currency(total_bebidas + total_refeicoes, grouping=True)}')

                    return redirect(url_for('caixa'))
                else:
                    flash('ID ou nome não encontrado!')
                    return redirect(url_for('caixa'))
            else:
                flash('ID já possui pagamento!')
                return redirect(url_for('caixa'))

        elif 'realizar_pagamento' in request.form:  # Se o botão "Realizar Pagamento" foi pressionado
            forma_pagamento = form.forma_pagamento.data  # Obtém a forma de pagamento

            if registro_balanca or registro_bebidas:
                # Verifica se algum dos registros possui forma_pagamento definida
                if all(registro.forma_pagamento is None for registro in registro_balanca) and \
                        all(registro.forma_pagamento is None for registro in registro_bebidas):

                    # Atualiza a forma de pagamento diretamente no banco de dados
                    db.session.execute(text("UPDATE balanca SET forma_pagamento = :forma_pagamento WHERE id = :id_comanda OR nome_comanda = :nome_comanda"),
                                       {"forma_pagamento": forma_pagamento, "id_comanda": session['id_refeicao'], "nome_comanda": session['nome_existente']})

                    db.session.execute(text("UPDATE bebida SET forma_pagamento = :forma_pagamento WHERE id = :id_comanda OR nome_comanda = :nome_comanda"),
                                       {"forma_pagamento": forma_pagamento, "id_comanda": session['id_refeicao'], "nome_comanda": session['nome_existente']})

                    db.session.commit()  # Confirma a transação
                    session.pop('id_refeicao', None)
                    session.pop('nome_existente', None)
                    registro_balanca = None
                    registro_bebidas = None
                    flash('Pagamento realizado com sucesso!')
                    return redirect(url_for('caixa'))

                else:
                    flash('ID já possui pagamento ou ID não cadastrado!')
                    return redirect(url_for('caixa'))
            else:
                flash('Primeiro precisa realizar a pesquisa!')
                return redirect(url_for('caixa'))

        elif 'cancelar' in request.form:  # Se o botão "Cancelar" foi pressionado
            session.pop('id_refeicao', None)
            session.pop('nome_existente', None)
            registro_balanca = None
            registro_bebidas = None
            return redirect(url_for('caixa'))

        elif 'voltar_menu' in request.form:  # Se o botão "Voltar menu" foi pressionado
            session.pop('id_refeicao', None)
            session.pop('nome_existente', None)
            registro_balanca = None
            registro_bebidas = None
            return redirect(url_for('menu'))

    return render_template('caixa.html', form=form)
@application.route('/relatorio', methods=['POST', 'GET'])
def relatorio():
    if verificar_autenticacao():
        return verificar_autenticacao()  # Redireciona para a página de login se não estiver autenticado

    form = RelatorioForm()  # Instancia o formulário de relatório

    if form.validate_on_submit():
        if 'gerar_relatorio' in request.form:  # Se o botão "Gerar Relatório" foi pressionado
            data_inicial = form.data_inicial.data  # Obtém a data inicial do formulário
            data_final = form.data_final.data  # Obtém a data final do formulário

            # Realiza a consulta no banco de dados para as refeições entre as datas fornecidas
            consulta_balanca = Balanca.query.filter(Balanca.data.between(data_inicial, data_final)).all()
            # Realiza a consulta no banco de dados para as bebidas entre as datas fornecidas
            consulta_bebida = Bebida.query.filter(Bebida.data.between(data_inicial, data_final)).all()

            # Inicializa os conjuntos para armazenar os IDs não pagos
            ids_nao_pagos = set()
            ids_pagos =set()

            # Inicializa as variáveis para armazenar os totais
            total_refeicoes = 0
            total_valor_refeicoes = 0
            total_bebidas = 0
            total_valor_bebidas = 0

            # Calcula os totais e verifica os campos de pagamento para as refeições
            for registro in consulta_balanca:
                total_refeicoes += 1
                total_valor_refeicoes += registro.total_refeicoes

                if registro.forma_pagamento:
                    ids_pagos.update([registro.id])
                else:
                    ids_nao_pagos.update([registro.nome_comanda])

            # Calcula os totais e verifica os campos de pagamento para as bebidas
            for registro in consulta_bebida:
                total_bebidas += registro.numero_bebidas
                total_valor_bebidas += registro.total_bebidas

                if registro.forma_pagamento:
                    ids_pagos.update([registro.id])
                else:
                    ids_nao_pagos.update([registro.nome_comanda])

            # Calcula o valor total arrecadado com refeições e bebidas
            total_arrecadado = total_valor_refeicoes + total_valor_bebidas

            # Formata os valores monetários
            total_valor_refeicoes = locale.currency(total_valor_refeicoes, grouping=True)
            total_valor_bebidas = locale.currency(total_valor_bebidas, grouping=True)
            total_arrecadado = locale.currency(total_arrecadado, grouping=True)

            # Gere o relatório em PDF
            file_name = "Relatorio.pdf"
            generate_relatorio_pdf(total_refeicoes, total_valor_refeicoes, total_bebidas,
                                   total_valor_bebidas, total_arrecadado, ids_pagos, ids_nao_pagos,
                                   data_inicial, data_final, file_name)
            time.sleep(2)
            return redirect(url_for('relatorio'))

        elif 'voltar_menu' in request.form:  # Se o botão "Voltar menu" foi pressionado
            return redirect(url_for('menu'))

    return render_template('relatorio.html', form=form)