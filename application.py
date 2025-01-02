from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt


# Inicialização da aplicação Flask
application = Flask(__name__)

# Carregamento das configurações da aplicação a partir do arquivo config.py
application.config.from_pyfile('config.py')

# Inicialização do SQLAlchemy para interagir com o banco de dados
db = SQLAlchemy(application)

# Inicialização do CSRFProtect para proteção contra ataques CSRF
csrf = CSRFProtect(application)

# Inicialização do Bcrypt para criptografia de senhas
bcrypt = Bcrypt(application)

# Importação das rotas da aplicação
from routes import *

# Execução do aplicativo Flask se este arquivo for o arquivo de entrada
if __name__ == '__main__':
    application.run(host="0.0.0.0", debug=True, port=8085)
