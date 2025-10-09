class Database:
    @staticmethod
    def populate_database(conn):
        cursor = conn.cursor()
        records_len = 5
        usr_list = [{'username': f'test_{i}', 'occupation': f'test_{i}'} for i in range(records_len)]
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                occupation TEXT NOT NULL
            );
        """)
        conn.commit()
        cursor.executemany("INSERT INTO users (username, occupation) VALUES (?, ?)",
                           [(user['username'], user['occupation']) for user in usr_list])
        conn.commit()

    @staticmethod
    def add_user(conn, user_name, occupation):
        conn.execute("INSERT INTO users (username, occupation) VALUES (?, ?)", (user_name, occupation))
        conn.commit()

    @staticmethod
    def update_user(conn, user_id, occupation):
        conn.execute("UPDATE users SET occupation=? WHERE id = ?", (occupation, user_id))
        conn.commit()

    @staticmethod
    def delete_user(conn, user_id):
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()

    @staticmethod
    def get_user(conn, user_id):
        cursor = conn.execute('SELECT * FROM users WHERE id=?', (user_id,))
        return cursor.fetchone()

    @staticmethod
    def get_users(conn):
        cursor = conn.execute('SELECT * FROM users')
        return cursor.fetchall()
