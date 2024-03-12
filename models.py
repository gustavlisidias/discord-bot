import asyncpg

from settings import pguser, pgpass, pgbase, pghost


class Log:
    def __init__(self, funcao, mensagem):
        self.funcao = funcao
        self.mensagem = mensagem

    async def save(self):
        try:
            conn = await asyncpg.connect(user=pguser, password=pgpass, database=pgbase, host=pghost)
            await conn.execute('INSERT INTO logs (funcao, mensagem) VALUES ($1, $2)', self.funcao, self.mensagem)
            await conn.close()

        except asyncpg.exceptions.PostgresError as e:
            print(f'Erro ao inserir log: {e}')


class Sala:
    def __init__(self, servidor, status=False):
        self.servidor = servidor
        self.status = status

    async def get(self):
        try:
            conn = await asyncpg.connect(user=pguser, password=pgpass, database=pgbase, host=pghost)
            sala = await conn.fetch('SELECT id FROM salas WHERE servidor = $1', self.servidor)
            await conn.close()
            return sala[0]['id'] if sala else None

        except asyncpg.exceptions.PostgresError as e:
            print(f'Erro ao selecionar sala: {e}')

    async def save(self):
        try:
            conn = await asyncpg.connect(user=pguser, password=pgpass, database=pgbase, host=pghost)
            await conn.execute('INSERT INTO salas (servidor, status) VALUES ($1, $2)', self.servidor, self.status)
            await conn.close()

        except asyncpg.exceptions.PostgresError as e:
            print(f'Erro ao inserir sala: {e}')

    async def update(self):
        try:
            conn = await asyncpg.connect(user=pguser, password=pgpass, database=pgbase, host=pghost)
            await conn.execute('UPDATE salas SET status = $1 WHERE servidor = $2', self.status, self.servidor)
            await conn.close()

        except asyncpg.exceptions.PostgresError as e:
            print(f'Erro ao inserir sala: {e}')


class Comando:
    def __init__(self, sala, autor, comando):
        self.sala = sala
        self.autor = autor
        self.comando = comando

    async def get(self):
        try:
          conn = await asyncpg.connect(user=pguser, password=pgpass, database=pgbase, host=pghost)
          comando = await conn.fetch('SELECT * FROM comandos WHERE sala = $1 and autor = $2', self.sala, self.autor)
          await conn.close()
          return comando
        
        except asyncpg.exceptions.PostgresError as e:
            print(f'Erro ao selecionar comando: {e}')

    async def save(self):
        try:
            conn = await asyncpg.connect(user=pguser, password=pgpass, database=pgbase, host=pghost)
            await conn.execute('INSERT INTO comandos (sala, autor, comando) VALUES ($1, $2, $3)', self.sala, self.autor, self.comando)
            await conn.close()
            
        except asyncpg.exceptions.PostgresError as e:
            print(f'Erro ao inserir comando: {e}')


class Mensagem:
    def __init__(self, autor, mensagem=None, sala=None, arquivo=None, resposta=None):
        self.sala = sala
        self.autor = autor
        self.mensagem = mensagem
        self.arquivo = arquivo
        self.resposta = resposta

    async def get(self):
        try:
          conn = await asyncpg.connect(user=pguser, password=pgpass, database=pgbase, host=pghost)

          if self.sala:
            mensagem = await conn.fetch('SELECT * FROM mensagens WHERE sala = $1 and autor = $2', self.sala, self.autor)
          else:
            mensagem = await conn.fetch('SELECT * FROM mensagens WHERE sala is null and autor = $1', self.autor)
              
          await conn.close()
          return mensagem
        
        except asyncpg.exceptions.PostgresError as e:
            print(f'Erro ao selecionar mensagem: {e}')

    async def save(self):
        try:
            conn = await asyncpg.connect(user=pguser, password=pgpass, database=pgbase, host=pghost)
            await conn.execute('INSERT INTO mensagens (sala, autor, mensagem, arquivo, resposta) VALUES ($1, $2, $3, $4, $5)', self.sala, self.autor, self.mensagem, self.arquivo, self.resposta)
            await conn.close()
            
        except asyncpg.exceptions.PostgresError as e:
            print(f'Erro ao inserir mensagem: {e}')