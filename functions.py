import locale
from fpdf import FPDF
import qrcode
import os
import webbrowser

# Defina a localidade para o Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

'''def generate_pdf(id, nome_comanda, refeicao, bebidas, total_geral, qr_code_data, file_name):
    # Diretório onde o relatório será salvo
    directory = 'static'

    # Crie o diretório se ele não existir
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Caminho completo do arquivo
    file_path = os.path.join(directory, file_name)

    # Se o arquivo já existir, exclua-o
    if os.path.exists(file_path):
        os.remove(file_path)

    pdf = FPDF()

    # Adicione uma página ao PDF
    pdf.add_page()

    # Defina a fonte para o título (Arial, negrito, 16)
    pdf.set_font("Arial", "B", 16)

    # Escreva o título da comanda
    pdf.cell(200, 10, "Comanda", ln=True, align="C")

    # Adicione uma quebra de linha
    pdf.ln(10)

    # Adicione os detalhes do registro (ID e lista de refeições)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"ID: {id}", ln=True)
    pdf.cell(200, 10, f"Nome: {nome_comanda}", ln=True)

    # Adicione a lista de refeições, formatada como moeda brasileira
    pdf.cell(200, 10, "Refeições:", ln=True)
    for numero, valor in refeicao.items():
        pdf.cell(200, 10, f"{numero}. {locale.currency(valor, grouping=True)}", ln=True)

    # Adicione o total de refeições
    total_refeicoes = sum(refeicao.values())
    pdf.cell(200, 10, f"Total de refeições: {locale.currency(total_refeicoes, grouping=True)}", ln=True)

    # Adicione uma quebra de linha
    pdf.ln(5)

    # Adicione a lista de bebidas, formatada como moeda brasileira
    pdf.cell(200, 10, "Bebidas:", ln=True)
    for tipo_bebida, (quantidade, total) in bebidas.items():
        pdf.cell(200, 10, f"{tipo_bebida}: {quantidade} unidades - Total: {locale.currency(total, grouping=True)}",
                 ln=True)

    # Adicione o total de bebidas
    total_bebidas = sum(total for _, total in bebidas.values())
    pdf.cell(200, 10, f"Total de bebidas: {locale.currency(total_bebidas, grouping=True)}", ln=True)

    # Adicione uma quebra de linha
    pdf.ln(5)

    # Adicione o total geral (refeições + bebidas)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, f"Total geral: {locale.currency(total_geral, grouping=True)}", ln=True)

    # Adicione uma quebra de linha
    pdf.ln(10)

    # Adicione o QR Code de pagamento
    pdf.cell(200, 10, "QR Code de Pagamento:", ln=True)
    pdf.ln(5)
    pdf.image(qr_code_data, x=20, y=pdf.get_y(), w=50, h=50)

    pdf.output(file_path)

    # Abrir o arquivo PDF no visualizador padrão do sistema
    #webbrowser.open(file_path)'''

def generate_relatorio_pdf(total_refeicoes, total_valor_refeicoes, total_bebidas, total_valor_bebidas, total_arrecadado, ids_pagos, ids_nao_pagos, data_inicial, data_final, file_name):
    # Diretório onde o relatório será salvo
    directory = 'static'

    # Crie o diretório se ele não existir
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Caminho completo do arquivo
    file_path = os.path.join(directory, file_name)

    # Se o arquivo já existir, exclua-o
    if os.path.exists(file_path):
        os.remove(file_path)

    pdf = FPDF()

    # Adicione uma página ao PDF
    pdf.add_page()

    # Defina a fonte para o título (Arial, negrito, 16)
    pdf.set_font("Arial", "B", 16)

    # Escreva o título do relatório
    pdf.cell(200, 10, "Relatório de Vendas", ln=True, align="C")

    # Adicione uma quebra de linha
    pdf.ln(10)

    # Adicione os detalhes do relatório
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Data inicial: {data_inicial.strftime('%d/%m/%Y')}", ln=True)
    pdf.cell(200, 10, f"Data final: {data_final.strftime('%d/%m/%Y')}", ln=True)
    pdf.cell(200, 10, f"Total de refeições vendidas: {total_refeicoes}", ln=True)
    pdf.cell(200, 10, f"Valor total arrecadado com refeições: {total_valor_refeicoes}", ln=True)
    pdf.cell(200, 10, f"Total de bebidas vendidas: {total_bebidas}", ln=True)
    pdf.cell(200, 10, f"Valor total arrecadado com bebidas: {total_valor_bebidas}", ln=True)
    pdf.cell(200, 10, f"Quantidade de pagadores: {len(ids_pagos)}", ln=True)
    pdf.cell(200, 10, f"Quantidade de não pagadores: {len(ids_nao_pagos)}", ln=True)
    pdf.cell(200, 10, f"Total arrecadado: {total_arrecadado}", ln=True)

    # Adicione uma quebra de linha
    pdf.ln(10)

    # Exiba zero se o conjunto de IDs não pagos estiver vazio, caso contrário, exiba os IDs
    pdf.cell(200, 10, "Nomes que não pagaram:", ln=True)
    if ids_nao_pagos:
        for id_nao_pago in sorted(ids_nao_pagos):
            pdf.cell(200, 10, f"- {id_nao_pago}", ln=True)
    else:
        pdf.cell(200, 10, "Nenhum", ln=True)

    # Adicione uma quebra de linha
    pdf.ln(10)

    pdf.output(file_path)

    # Abrir o arquivo PDF no visualizador padrão do sistema
    # webbrowser.open(file_path)
def generate_qr_code(data, file_name):
    # Função para gerar um QR Code usando a biblioteca qrcode
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(data)  # Adicione os dados ao QR Code
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_name)  # Salve a imagem do QR Code no arquivo especificado por file_name