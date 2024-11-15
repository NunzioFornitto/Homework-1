import grpc
from concurrent import futures
import time
import mysql.connector
from datetime import datetime
import service_pb2
import service_pb2_grpc

# Cache separate per la registrazione e l'aggiornamento
register_cache = {}
update_cache = {}

# Connessione al database MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="mysql",
        user="Admin", 
        password="1234",  
        database="sistema_finanza"
    )

# Implementazione del servizio UserService
class UserService(service_pb2_grpc.UserServiceServicer):

    def RegisterUser(self, request, context):
        # Verifica se la richiesta di registrazione è già stata processata (at-most-once) la verifica è fatta su email
        if request.email in register_cache:
            return service_pb2.UserResponse(success=False, message="La richiesta di registrazione è già stata processata.")

        # Connessione al database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se l'utente esiste già
        cursor.execute("SELECT id_utente FROM utenti WHERE email = %s", (request.email,))
        user_exists = cursor.fetchone()

        if user_exists:
            cursor.close()
            conn.close()
            return service_pb2.UserResponse(success=False, message="Utente già registrato.")

        # Inserisce il nuovo utente nella tabella utenti
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("INSERT INTO utenti (email, ticker, creato_il, aggiornato_il) VALUES (%s, %s, %s, %s)",
                       (request.email, request.ticker, created_at, created_at))
        conn.commit()

        # Memorizza la richiesta nella cache di registrazione
        register_cache[request.email] = request.ticker

        # Chiude la connessione al database
        cursor.close()
        conn.close()

        return service_pb2.UserResponse(success=True, message="Utente registrato con successo.")

    def UpdateUser(self, request, context):
        # Verifica se la richiesta di aggiornamento è già stata processata (at-most-once) la verifica è fatta sia su email in questo caso e anche sul ticker
        if request.email in update_cache and update_cache[request.email] == request.ticker:
            return service_pb2.UserResponse(success=False, message="La richiesta di aggiornamento è già stata processata con lo stesso ticker.")

        # Connessione al database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se l'utente esiste
        cursor.execute("SELECT id_utente FROM utenti WHERE email = %s", (request.email,))
        user_exists = cursor.fetchone()

        if not user_exists:
            cursor.close()
            conn.close()
            return service_pb2.UserResponse(success=False, message="Utente non trovato.")

        # Aggiorna il ticker dell'utente solo se è diverso
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("UPDATE utenti SET ticker = %s, aggiornato_il = %s WHERE email = %s",
                       (request.ticker, updated_at, request.email))
        conn.commit()

        # Memorizza la richiesta nella cache di aggiornamento
        update_cache[request.email] = request.ticker

        # Chiude la connessione al database
        cursor.close()
        conn.close()

        return service_pb2.UserResponse(success=True, message="Utente aggiornato con successo.")

    def DeleteUser(self, request, context):
        # Connessione al database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se l'utente esiste
        cursor.execute("SELECT id_utente FROM utenti WHERE email = %s", (request.email,))
        user_exists = cursor.fetchone()

        if not user_exists:
            cursor.close()
            conn.close()
            return service_pb2.UserResponse(success=False, message="Utente non trovato.")

        # Cancella l'utente dalla tabella utenti
        cursor.execute("DELETE FROM utenti WHERE email = %s", (request.email,))
        conn.commit()

        # Rimuove l'utente anche dalle cache se presente
        if request.email in register_cache:
            del register_cache[request.email]
        if request.email in update_cache:
            del update_cache[request.email]

        cursor.close()
        conn.close()

        return service_pb2.UserResponse(success=True, message="Utente cancellato con successo.")

# Implementazione del servizio StockService
class StockService(service_pb2_grpc.StockServiceServicer):

    def GetLatestStockValue(self, request, context):
        # Connessione al database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Recupera l'ultimo valore del ticker dell'utente
        cursor.execute("SELECT ticker, valore, time_stamp FROM azioni WHERE email = %s ORDER BY time_stamp DESC LIMIT 1", (request.email,))
        result = cursor.fetchone()

        if result:
            ticker, valore, timestamp = result
            # Converte il timestamp in una stringa nel formato desiderato
            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S") if isinstance(timestamp, datetime) else str(timestamp)
            cursor.close()
            conn.close()
            return service_pb2.StockResponse(ticker=ticker, value=valore, timestamp=timestamp_str)
        else:
            cursor.close()
            conn.close()
            return service_pb2.StockResponse(ticker="", value=0.0, timestamp="")

    def GetAverageStockValue(self, request, context):
        # Connessione al database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Recupera i dati per calcolare la media
        cursor.execute("SELECT valore FROM azioni WHERE email = %s ORDER BY time_stamp DESC LIMIT %s", (request.email, request.count))
        results = cursor.fetchall()

        if results:
            total_value = sum([row[0] for row in results])
            average_value = total_value / len(results)
            cursor.close()
            conn.close()
            return service_pb2.StockAverageResponse(average=average_value)
        else:
            cursor.close()
            conn.close()
            return service_pb2.StockAverageResponse(average=0.0)

# Funzione per avviare il server gRPC
def serve():
    # Creo il server con un pool di thread per gestire le richieste
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Registro i servizi al server precedentemente creato
    service_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    service_pb2_grpc.add_StockServiceServicer_to_server(StockService(), server)
    # Metto in ascolto il server sulla porta 50051 su tutte le interfacce di rete disponibili
    server.add_insecure_port('[::]:50051')
    print("Server gRPC in esecuzione sulla porta 50051...")
    # Avvio il server
    server.start()
    # Ciclo infinito in cui il server è su, ma se premo ctrl+c il server si ferma perchè viene sollevata un'eccezione
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
