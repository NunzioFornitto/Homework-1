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

        # Genero un request_id univoco per ogni richiesta (non gestito dal server)
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

                # Inserimento dei parametri high_value e low_value aggiuntivi
                high_value, low_value = None, None
                while True:
                    print("Inserisci almeno uno dei seguenti valori (o premi 'b' per tornare indietro):")
                    high_value_input = input("Valore massimo (high_value): ")
                    low_value_input = input("Valore minimo (low_value): ")

                    if high_value_input.lower() == 'b' or low_value_input.lower() == 'b':
                        break

                    # Convertire i valori in float se forniti (nel db sono in float)
                    high_value = float(high_value_input) if high_value_input else None
                    low_value = float(low_value_input) if low_value_input else None

                    # Controllo di almeno uno dei due valori deve essere fornito
                    if high_value is None and low_value is None:
                        print("Errore: devi fornire almeno uno tra high_value e low_value.")
                        continue

                    # Controllo: high_value deve essere maggiore di low_value se entrambi sono forniti
                    if high_value is not None and low_value is not None and high_value <= low_value:
                        print("Errore: il valore massimo (high_value) deve essere maggiore del valore minimo (low_value).")
                        continue

                    break  # Uscita dal ciclo se i valori sono validi

                # Se l'utente ha scelto di tornare indietro
                if high_value_input.lower() == 'b' or low_value_input.lower() == 'b':
                    break

                user_request = service_pb2.UserRequest(
                    email=email,
                    ticker=ticker,
                    high_value=high_value if high_value is not None else 0.0,
                    low_value=low_value if low_value is not None else 0.0,
                    request_id=request_id
                )
                response = user_stub.RegisterUser(user_request)
                print(f"Registrazione Utente: Success: {response.success}, Message: {response.message}")
                break  # Torna al menu principale dopo l'operazione
        #Simile al caso 1, ma con la differenza che si aggiorna il ticker dell'utente
        elif scelta == '2':
            while True:
                print("\n-- Aggiornamento Ticker Utente --")
                email = input("Inserisci l'email dell'utente (o premi 'b' per tornare indietro): ")
                if email.lower() == 'b':
                    break
                ticker = input("Inserisci il nuovo ticker dell'azione (o premi 'b' per tornare indietro): ")
                if ticker.lower() == 'b':
                    break

                # Inserimento dei parametri high_value e low_value
                high_value, low_value = None, None
                while True:
                    print("Inserisci almeno uno dei seguenti valori (o premi 'b' per tornare indietro):")
                    high_value_input = input("Valore massimo (high_value): ")
                    low_value_input = input("Valore minimo (low_value): ")

                    if high_value_input.lower() == 'b' or low_value_input.lower() == 'b':
                        break

                    # Convertire i valori in float se forniti
                    high_value = float(high_value_input) if high_value_input else None
                    low_value = float(low_value_input) if low_value_input else None

                    # Controllo: almeno uno dei due valori deve essere fornito
                    if high_value is None and low_value is None:
                        print("Errore: devi fornire almeno uno tra high_value e low_value.")
                        continue

                    # Controllo: high_value deve essere maggiore di low_value se entrambi sono forniti
                    if high_value is not None and low_value is not None and high_value <= low_value:
                        print("Errore: il valore massimo (high_value) deve essere maggiore del valore minimo (low_value).")
                        continue

                    break  # Uscita dal ciclo se i valori sono validi

                # Se l'utente ha scelto di tornare indietro
                if high_value_input.lower() == 'b' or low_value_input.lower() == 'b':
                    break
                #creazione della richiesta per l'aggiornamento del ticker
                user_request = service_pb2.UserRequest(
                    email=email,
                    ticker=ticker,
                    high_value=high_value if high_value is not None else 0.0,
                    low_value=low_value if low_value is not None else 0.0,
                    request_id=request_id
                )
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










