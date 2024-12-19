import mysql.connector
from datetime import datetime

class AddUserCommand:
    """Command: Represents a request to modify user data."""
    def __init__(self, email, ticker, high_value, low_value):
        self.email = email
        self.ticker = ticker
        self.high_value = high_value
        self.low_value = low_value
class UpdateUserCommand:
    """Command: Represents a request to modify user data."""
    def __init__(self, email, ticker, high_value, low_value):
        self.email = email
        self.ticker = ticker
        self.high_value = high_value
        self.low_value = low_value
class DeleteUserCommand:
    """Command: Represents a request to delete a user."""
    def __init__(self, email):
        self.email = email
class GetLatestStockValueQuery:
    """Query: Represents a request to retrieve the latest stock value."""
    def __init__(self, email):
        self.email = email
        
class GetAverageStockValueQuery:
    def __init__(self, email, count):
        self.email = email
        self.count = count
class SaveStockDataCommand:
    """Comando per salvare i dati azionari."""
    def __init__(self, email, ticker, value):
        self.email = email
        self.ticker = ticker
        self.value = value

class UserWriteService:
    """Write Model: Handles commands to modify the data in the database."""

    def __init__(self):
        # Configurazione della connessione al database
        self.db_config = {
            "host": "mysql",
            "user": "Admin",
            "password": "1234",
            "database": "sistema_finanza"
        }

    def _get_db_connection(self):
        """Crea e restituisce una connessione al database."""
        return mysql.connector.connect(**self.db_config)

    def handle_register_user(self, command):
        """Registra un nuovo utente nel database."""
        conn = self._get_db_connection()
        cursor = conn.cursor()

        try:
            # Query per inserire un nuovo utente
            query = """
                INSERT INTO utenti (email, ticker, high_value, low_value) 
                VALUES (%s, %s,%s,%s)
            """
            cursor.execute(query, (command.email, command.ticker, command.high_value, command.low_value))
            conn.commit()
            print(f"Utente registrato: {command.email}, ticker: {command.ticker} high_value: {command.high_value} low_value: {command.low_value}")
        except mysql.connector.IntegrityError:
            print(f"Errore: L'email {command.email} è già registrata.")
        finally:
            cursor.close()
            conn.close()

    def handle_update_user(self, command):
        """Aggiorna il ticker di un utente esistente nel database."""
        conn = self._get_db_connection()
        cursor = conn.cursor()

        try:
            # Query per aggiornare il ticker di un utente
            query = """
                UPDATE utenti 
                SET ticker = %s, aggiornato_il = %s, high_value = %s, low_value = %s
                WHERE email = %s
            """
            updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Passa i parametri nell'ordine corretto
            cursor.execute(query, (command.ticker, updated_at, command.high_value, command.low_value, command.email))
            conn.commit()

            if cursor.rowcount > 0:
                print(f"Utente aggiornato: {command.email}, nuovo ticker: {command.ticker}, high_value: {command.high_value}, low_value: {command.low_value}")
            else:
                print(f"Errore: Nessun utente trovato con l'email {command.email}.")
        finally:
            cursor.close()
            conn.close()


    def handle_delete_user(self, command):
        """Cancella un utente dal database."""
        conn = self._get_db_connection()
        cursor = conn.cursor()

        try:
            # Query per cancellare un utente
            query = "DELETE FROM utenti WHERE email = %s"
            cursor.execute(query, (command.email,))
            conn.commit()

            if cursor.rowcount > 0:
                print(f"Utente cancellato: {command.email}")
            else:
                print(f"Errore: Nessun utente trovato con l'email {command.email}.")
        finally:
            cursor.close()
            conn.close()

class UserReadService:
    """Read Model: Handles queries to retrieve data from the database."""

    def __init__(self):
        # Configurazione della connessione al database
        self.db_config = {
            "host": "mysql",
            "user": "Admin",
            "password": "1234",
            "database": "sistema_finanza"
        }

    def _get_db_connection(self):
        """Crea e restituisce una connessione al database."""
        return mysql.connector.connect(**self.db_config)

    def is_user_registered(self, email):
        """Verifica se un utente esiste già nel database."""
        conn = self._get_db_connection()
        cursor = conn.cursor()

        try:
            query = "SELECT id_utente FROM utenti WHERE email = %s"
            cursor.execute(query, (email,))
            user_exists = cursor.fetchone()
            return user_exists is not None
        finally:
            cursor.close()
            conn.close()
    def get_all_users(self):
        """Recupera tutti gli utenti registrati nel database."""
        conn = self._get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT email, ticker FROM utenti")
            users = cursor.fetchall()
            return users
        finally:
            cursor.close()
            conn.close()

class StockReadService:
    def __init__(self):
        self.db_config = {
            "host": "mysql",
            "user": "Admin",
            "password": "1234",
            "database": "sistema_finanza"
        }

    def _get_db_connection(self):
        """Crea e restituisce una connessione al database."""
        return mysql.connector.connect(**self.db_config)

    def get_latest_stock_value(self, query):
        """Recupera l'ultimo valore del ticker di un utente."""
        conn = self._get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT ticker, valore, time_stamp FROM azioni WHERE email = %s ORDER BY time_stamp DESC LIMIT 1", 
                (query.email,)
            )
            result = cursor.fetchone()

            if result:
                ticker, valore, timestamp = result
                timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S") if isinstance(timestamp, datetime) else str(timestamp)
                return ticker, valore, timestamp_str
            else:
                return None, 0.0, ""
        finally:
            cursor.close()
            conn.close()
            
    def get_average_stock_value(self, query):
        """Recupera i valori delle azioni per calcolare la media."""
        conn = self._get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT valore FROM azioni WHERE email = %s ORDER BY time_stamp DESC LIMIT %s", 
                (query.email, query.count)
            )
            results = cursor.fetchall()

            if results:
                # Calcola la media dei valori
                total_value = sum([row[0] for row in results])
                average_value = total_value / len(results)
                return average_value
            else:
                return 0.0  # Se non ci sono dati, la media è 0
        finally:
            cursor.close()
            conn.close()
            
    def get_users_for_threshold_alert(self):
        """Recupera i valori più recenti delle azioni per verificare le soglie."""
        conn = self._get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT 
                    u.email, 
                    u.ticker, 
                    u.high_value, 
                    u.low_value, 
                    a.valore
                FROM 
                    utenti u
                LEFT JOIN (
                    SELECT 
                        email, 
                        ticker, 
                        valore, 
                        time_stamp
                    FROM 
                        azioni a1
                    WHERE 
                        (a1.email, a1.ticker, a1.time_stamp) IN (
                            SELECT 
                                email, 
                                ticker, 
                                MAX(time_stamp) AS ultimo_aggiornamento
                            FROM 
                                azioni
                            GROUP BY 
                                email, 
                                ticker
                        )
                ) a 
                ON 
                    u.email = a.email AND u.ticker = a.ticker
                WHERE 
                    ((u.high_value IS NOT NULL AND a.valore > u.high_value) OR (u.high_value = 0 AND a.valore > 0))
                    OR 
                    ((u.low_value IS NOT NULL AND a.valore < u.low_value) OR (u.low_value = 0 AND a.valore < 0));
                """
            )
            results = cursor.fetchall()
            return results
        finally:
            cursor.close()
            conn.close()



class StockWriteService:
    """Write Model: Handles commands to modify stock data in the database."""

    def __init__(self):
        self.db_config = {
            "host": "mysql",
            "user": "Admin",
            "password": "1234",
            "database": "sistema_finanza"
        }

    def _get_db_connection(self):
        """Crea e restituisce una connessione al database."""
        return mysql.connector.connect(**self.db_config)

    def save_stock_data(self, command):
        """Memorizza i dati relativi al valore azionario nel database."""
        conn = self._get_db_connection()
        cursor = conn.cursor()

        try:
            query = """
                INSERT INTO azioni (email, ticker, valore)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (command.email, command.ticker, command.value))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
