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

        if scelta == '1':
            while True:
                print("\n-- Registrazione Utente --")
                email = input("Inserisci l'email dell'utente (o premi 'b' per tornare indietro): ")
                if email.lower() == 'b':
                    break
                ticker = input("Inserisci il ticker dell'azione associata (o premi 'b' per tornare indietro): ")
                if ticker.lower() == 'b':
                    break
                user_request = service_pb2.UserRequest(email=email, ticker=ticker, request_id=request_id)
                response = user_stub.RegisterUser(user_request)
                print(f"Registrazione Utente: Success: {response.success}, Message: {response.message}")
                break  # Torna al menu principale dopo l'operazione

        elif scelta == '2':
            while True:
                print("\n-- Aggiornamento Ticker Utente --")
                email = input("Inserisci l'email dell'utente (o premi 'b' per tornare indietro): ")
                if email.lower() == 'b':
                    break
                ticker = input("Inserisci il nuovo ticker dell'azione (o premi 'b' per tornare indietro): ")
                if ticker.lower() == 'b':
                    break
                user_request = service_pb2.UserRequest(email=email, ticker=ticker, request_id=request_id)
                response = user_stub.UpdateUser(user_request)
                print(f"Aggiornamento Utente: Success: {response.success}, Message: {response.message}")
                break  

        elif scelta == '3':
            while True:
                print("\n-- Recupero Ultimo Valore Azione --")
                email = input("Inserisci l'email dell'utente (o premi 'b' per tornare indietro): ")
                if email.lower() == 'b':
                    break
                stock_request = service_pb2.StockRequest(email=email)
                stock_response = stock_stub.GetLatestStockValue(stock_request)
                print(f"Ultimo Valore Stock: Ticker: {stock_response.ticker}, Value: {stock_response.value}, Timestamp: {stock_response.timestamp}")
                break  

        elif scelta == '4':
            while True:
                print("\n-- Calcolo della Media degli Ultimi Valori Azionari --")
                email = input("Inserisci l'email dell'utente (o premi 'b' per tornare indietro): ")
                if email.lower() == 'b':
                    break
                count = input("Inserisci il numero di valori per calcolare la media (o premi 'b' per tornare indietro): ")
                if count.lower() == 'b':
                    break
                if not count.isdigit():
                    print("Errore: Devi inserire un numero valido.")
                    continue
                count = int(count)
                stock_average_request = service_pb2.StockAverageRequest(email=email, count=count)
                stock_average_response = stock_stub.GetAverageStockValue(stock_average_request)
                print(f"Media degli ultimi {count} valori: {stock_average_response.average}")
                break  

        elif scelta == '5':
            while True:
                print("\n-- Cancellazione Utente --")
                email = input("Inserisci l'email dell'utente da cancellare (o premi 'b' per tornare indietro): ")
                if email.lower() == 'b':
                    break
                user_request = service_pb2.UserRequest(email=email, ticker="", request_id=request_id)
                response = user_stub.DeleteUser(user_request)
                print(f"Cancellazione Utente: Success: {response.success}, Message: {response.message}")
                break  

        elif scelta == '6':
            print("Uscita dal programma...")
            break

        else:
            print("Scelta non valida, per favore scegli tra 1 e 6.")

if __name__ == "__main__":
    run()
