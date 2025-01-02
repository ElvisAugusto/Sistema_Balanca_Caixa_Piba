import os

# SECRET_KEY é usado pelo Flask para algumas funcionalidades de segurança,
# como proteger dados de sessão. É importante manter esta chave secreta e segura.
SECRET_KEY = 'bshvbsdvbp4u4385u33h'

# db_path cria um caminho absoluto para o arquivo do banco de dados SQLite.
# A função os.path.join é usada para garantir que o caminho seja construído de
# forma correta, independente do sistema operacional.
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db/banco.db')

# SQLALCHEMY_DATABASE_URI é a URI de conexão que SQLAlchemy usa para se conectar ao banco de dados.
# Neste caso, está sendo usado SQLite, que é um banco de dados leve e fácil de configurar.
# A URI é composta pelo esquema 'sqlite:///' seguido pelo caminho absoluto do arquivo do banco de dados.
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_path

# SQLALCHEMY_TRACK_MODIFICATIONS é uma configuração que, quando definida como False,
# desativa um recurso de rastreamento de modificações que consome memória adicional.
# Não é necessário para a maioria dos casos de uso e, portanto, é recomendado manter como False.
SQLALCHEMY_TRACK_MODIFICATIONS = False
