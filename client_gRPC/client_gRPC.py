import grpc
import service_pb2
import service_pb2_grpc
import sys
import uuid  

def run():
    # Connessione al server gRPC in ascolto sulla porta 50051
    channel = grpc.insecure_channel('localhost:50051')
    
    # Stub per i servizi UserService e StockService
    user_stub = service_pb2_grpc.UserServiceStub(channel)
    stock_stub = service_pb2_grpc.StockServiceStub(channel)

    while True:
        print("\nScegli una delle seguenti opzioni:")
        print("1. Registrazione Utente")
        print("2. Aggiornamento Ticker Utente")
        print("3. Recupero Ultimo Valore Azione")
        print("4. Calcolo della Media degli Ultimi Valori Azionari")
        print("5. Cancellazione Utente")
        print("6. Esci")

        scelta = input("Inserisci la tua scelta (1-6): ")

        # Genera un request_id univoco per ogni richiesta
        request_id = str(uuid.uuid4())
        
        #Con user_request, creo una richiesta, mentre con response ottengo la risposta del server remoto, chiamando il servizio e 
        #passandogli la richiesta user_reques che ho creato precedentemente.
        #Analogalmente con stock_request e stock_response.
        #Entrambi usano user_stub e stock_stub che permettono di invocare metodi come se fossero metodi locali.

        if scelta == '1':
            email = input("Inserisci l'email dell'utente: ")
            ticker = input("Inserisci il ticker dell'azione associata: ")
            user_request = service_pb2.UserRequest(email=email, ticker=ticker, request_id=request_id)
            response = user_stub.RegisterUser(user_request)
            print(f"Registrazione Utente: Success: {response.success}, Message: {response.message}")

        elif scelta == '2':
            email = input("Inserisci l'email dell'utente: ")
            ticker = input("Inserisci il nuovo ticker dell'azione: ")
            user_request = service_pb2.UserRequest(email=email, ticker=ticker, request_id=request_id)
            response = user_stub.UpdateUser(user_request)
            print(f"Aggiornamento Utente: Success: {response.success}, Message: {response.message}")

        elif scelta == '3':
            email = input("Inserisci l'email dell'utente: ")
            stock_request = service_pb2.StockRequest(email=email)
            stock_response = stock_stub.GetLatestStockValue(stock_request)
            print(f"Ultimo Valore Stock: Ticker: {stock_response.ticker}, Value: {stock_response.value}, Timestamp: {stock_response.timestamp}")

        elif scelta == '4':
            email = input("Inserisci l'email dell'utente: ")
            count = int(input("Inserisci il numero di valori per calcolare la media: "))
            stock_average_request = service_pb2.StockAverageRequest(email=email, count=count)
            stock_average_response = stock_stub.GetAverageStockValue(stock_average_request)
            print(f"Media degli ultimi {count} valori: {stock_average_response.average}")

        elif scelta == '5':
            email = input("Inserisci l'email dell'utente da cancellare: ")
            user_request = service_pb2.UserRequest(email=email, ticker="", request_id=request_id)
            response = user_stub.DeleteUser(user_request)
            print(f"Cancellazione Utente: Success: {response.success}, Message: {response.message}")

        elif scelta == '6':
            print("Uscita dal programma...")
            break

        else:
            print("Scelta non valida, per favore scegli tra 1 e 6.")

if __name__ == "__main__":
    run()
