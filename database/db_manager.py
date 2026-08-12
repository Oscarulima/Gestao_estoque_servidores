import sqlite3

class DBManager:
    def __init__(self, db_name="estoque_servidores.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS servidores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    serial_number TEXT UNIQUE NOT NULL,
                    marca TEXT NOT NULL,
                    modelo TEXT NOT NULL,
                    fator_forma TEXT,
                    qtd_baias TEXT,
                    tipo_slot TEXT,
                    tem_trilho TEXT,
                    tem_bezel TEXT,
                    modulo_gerenciamento TEXT,
                    observacoes TEXT,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            novas_colunas = [
                ("qtd_baias", "TEXT"),
                ("tem_bezel", "TEXT"),
                ("modulo_gerenciamento", "TEXT")
            ]
            for col, tipo in novas_colunas:
                try:
                    cursor.execute(f"ALTER TABLE servidores ADD COLUMN {col} {tipo}")
                except sqlite3.OperationalError:
                    pass

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS componentes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    servidor_id INTEGER,
                    tipo_componente TEXT,
                    part_number TEXT,
                    quantidade TEXT,
                    detalhes_extras TEXT,
                    FOREIGN KEY (servidor_id) REFERENCES servidores (id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def salvar_servidor(self, dados_servidor, lista_componentes):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO servidores (
                    serial_number, marca, modelo, fator_forma, qtd_baias, 
                    tipo_slot, tem_trilho, tem_bezel, modulo_gerenciamento, observacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, dados_servidor)
            
            servidor_id = cursor.lastrowid

            for comp in lista_componentes:
                cursor.execute("""
                    INSERT INTO componentes (servidor_id, tipo_componente, part_number, quantidade, detalhes_extras)
                    VALUES (?, ?, ?, ?, ?)
                """, (servidor_id, comp['tipo'], comp['pn'], comp['qtd'], comp['detalhes']))
            
            conn.commit()

    def atualizar_servidor(self, servidor_id, dados_servidor, lista_componentes):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE servidores 
                SET serial_number=?, marca=?, modelo=?, fator_forma=?, qtd_baias=?, 
                    tipo_slot=?, tem_trilho=?, tem_bezel=?, modulo_gerenciamento=?, observacoes=?
                WHERE id=?
            """, (*dados_servidor, servidor_id))

            cursor.execute("DELETE FROM componentes WHERE servidor_id=?", (servidor_id,))

            for comp in lista_componentes:
                cursor.execute("""
                    INSERT INTO componentes (servidor_id, tipo_componente, part_number, quantidade, detalhes_extras)
                    VALUES (?, ?, ?, ?, ?)
                """, (servidor_id, comp['tipo'], comp['pn'], comp['qtd'], comp['detalhes']))

            conn.commit()

    def listar_servidores(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, serial_number, marca, modelo, fator_forma, tipo_slot, tem_trilho, tem_bezel FROM servidores ORDER BY id DESC")
            return cursor.fetchall()

    def obter_servidor_completo_por_id(self, servidor_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, serial_number, marca, modelo, fator_forma, qtd_baias, tipo_slot, tem_trilho, tem_bezel, modulo_gerenciamento, observacoes
                FROM servidores WHERE id=?
            """, (servidor_id,))
            servidor = cursor.fetchone()

            cursor.execute("""
                SELECT tipo_componente, part_number, quantidade, detalhes_extras
                FROM componentes WHERE servidor_id=?
            """, (servidor_id,))
            componentes = cursor.fetchall()

            return servidor, componentes