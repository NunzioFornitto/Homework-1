import grpc
from concurrent import futures
import time
import mysql.connector
import service_pb2
import service_pb2_grpc
import threading
from cqrs import UserWriteService, AddUserCommand, UserReadService, UpdateUserCommand, GetLatestStockValueQuery, StockReadService, GetAverageStockValueQuery,DeleteUserCommand

# Cache sia per aggiornamento che per cancellazione
register_update_cache = {}
cache_lock = threading.Lock()

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
        with cache_lock:  # Blocca l'accesso alla cache
            if request.email in register_update_cache:
                cached_user = register_update_cache[request.email]
                if (cached_user['ticker'] == request.ticker and
                        cached_user['high_value'] == request.high_value and
                        cached_user['low_value'] == request.low_value):
                    return service_pb2.UserResponse(success=False, message="L'utente è già registrato con questi parametri.")

        read_service = UserReadService()
        write_service = UserWriteService()

        # Verifica se l'utente esiste già nel database
        if read_service.is_user_registered(request.email):
            return service_pb2.UserResponse(success=False, message="Utente già registrato nel database.")

        # Crea il comando per registrare l'utente
        command = AddUserCommand(
            email=request.email,
            ticker=request.ticker,
            high_value=request.high_value,
            low_value=request.low_value
        )

        try:
            write_service.handle_register_user(command)

            # Aggiungi l'utente nella cache dopo averlo registrato
            with cache_lock:
                register_update_cache[request.email] = {
                    'ticker': request.ticker,
                    'high_value': request.high_value,
                    'low_value': request.low_value
                }

            return service_pb2.UserResponse(success=True, message="Utente registrato con successo.")
        except Exception as e:
            return service_pb2.UserResponse(success=False, message=f"Errore durante la registrazione: {str(e)}")

    def UpdateUser(self, request, context):
        with cache_lock:  # Blocca l'accesso alla cache
            if request.email in register_update_cache:
                cached_user = register_update_cache[request.email]
                if (cached_user['ticker'] == request.ticker and
                        cached_user['high_value'] == request.high_value and
                        cached_user['low_value'] == request.low_value):
                    return service_pb2.UserResponse(success=False, message="La richiesta di aggiornamento è già stata processata con questi parametri.")

        read_service = UserReadService()
        write_service = UserWriteService()

        try:
            if not read_service.is_user_registered(request.email):
                return service_pb2.UserResponse(success=False, message="Utente non trovato, registralo prima di aggiornarlo.")

            # Crea il comando per aggiornare l'utente
            command = UpdateUserCommand(
                email=request.email,
                ticker=request.ticker,
                high_value=request.high_value,
                low_value=request.low_value
            )

            write_service.handle_update_user(command)

            # Aggiorna la cache con i nuovi valori
            with cache_lock:
                register_update_cache[request.email] = {
                    'ticker': request.ticker,
                    'high_value': request.high_value,
                    'low_value': request.low_value
                }

            return service_pb2.UserResponse(success=True, message="Utente aggiornato con successo.")
        except Exception as e:
            return service_pb2.UserResponse(success=False, message=f"Errore durante l'aggiornamento: {str(e)}")


    def DeleteUser(self, request, context):
        
        read_service = UserReadService()
        write_service = UserWriteService()

        # Verifica se l'utente esiste
        if not read_service.is_user_registered(request.email):
            return service_pb2.UserResponse(success=False, message="Utente non trovato.")
            
        # Cancella l'utente dalla tabella utenti
        command = DeleteUserCommand(email=request.email)
        write_service.handle_delete_user(command)
        
        # Rimuove l'utente anche dalle cache se presente
        with cache_lock:
           register_update_cache.pop(request.email, None)
        return service_pb2.UserResponse(success=True, message="Utente cancellato con successo.")
    
# Implementazione del servizio StockService
class StockService(service_pb2_grpc.StockServiceServicer):

    def GetLatestStockValue(self, request, context):
        # Crea una query per recuperare l'ultimo valore dell'azione
        query = GetLatestStockValueQuery(request.email)
        stock_read_service = StockReadService()
        
        # Passa la query al servizio di lettura
        ticker, value, timestamp = stock_read_service.get_latest_stock_value(query)
        
        if ticker:
            return service_pb2.StockResponse(ticker=ticker, value=value, timestamp=timestamp)
        else:
            return service_pb2.StockResponse(ticker="", value=0.0, timestamp="")

    def GetAverageStockValue(self, request, context):
        # Crea una query per calcolare la media del valore delle azioni
        query = GetAverageStockValueQuery(request.email, request.count)
        stock_read_service = StockReadService()
        
        # Passa la query al servizio di lettura
        average_value = stock_read_service.get_average_stock_value(query)
        
        return service_pb2.StockAverageResponse(average=average_value)

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


