import time
import yfinance as yf
from datetime import datetime, timezone, timedelta
from circuit_breaker import CircuitBreaker, CircuitBreakerOpenException
from cqrs import UserReadService, SaveStockDataCommand, StockWriteService
import threading
import socket
import prometheus_client
from prometheus_client import Gauge, Counter
from confluent_kafka import Producer
import json

# Configura il Circuit Breaker
circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)


# Configura il nome host e l'app
HOSTNAME = socket.gethostname()
APP_NAME = "data_collector"

SAVE_STOCK_DATA_CALLS = Counter(
    'save_stock_data_calls_total',  # Nome della metrica
    'Numero totale di chiamate alla funzione save_stock_data',  # Descrizione
    ['app', 'host']  # Labels per tracciare le chiamate per app e host
)

USERS_IN_DB = Gauge(
    'users_in_db',
    'Number of users in the database',
    ['app', 'host']
)

# Funzione per recuperare i dati da yfinance
def get_stock_data(ticker):
    """
    Recupera i dati dell'azione da yfinance per un determinato ticker.
    """
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")  # Recuperiamo i dati per 1 giorno
    if data.empty:
        raise Exception(f"Nessun dato disponibile per {ticker}")
    latest_value = data['Close'].iloc[-1]  # Ultimo valore di chiusura
    timestamp = data.index[-1]  # Timestamp dell'ultimo valore
    timestamp_str = timestamp.isoformat()
    return latest_value, timestamp_str

# Funzione per recuperare gli utenti dal database
def get_users_from_db():
    """
    Recupera gli utenti registrati dal database.
    """
    read_service = UserReadService()
    users = read_service.get_all_users()
    return users

# Funzione per memorizzare i dati nel database
def save_stock_data(email, ticker, value):
    """
    Memorizza i dati relativi al valore azionario nel database.
    """
    write_service = StockWriteService()
    command = SaveStockDataCommand(email, ticker, value)
    write_service.save_stock_data(command)

    # Incrementa il contatore ogni volta che save_stock_data è chiamata
    SAVE_STOCK_DATA_CALLS.labels(app=APP_NAME, host=HOSTNAME).inc()

# Funzione per inviare un messaggio a Kafka
def send_alert_to_kafka():
    """
    Invia un messaggio di notifica generico al topic Kafka `to-alert-system`.
    """
    message = {
        'status': 'update_complete',
        'message': 'Aggiornamento dei dati completato.',
        'timestamp': datetime.now(timezone(timedelta(0))).isoformat()
    }
    producer.produce(topic, json.dumps(message), callback=delivery_report)
    producer.flush()  

def delivery_report(err, msg):
    """Callback per riportare il risultato della consegna del messaggio."""
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

# Exporter Prometheus
def start_exporter():
    prometheus_client.start_http_server(8002)  # Esposizione delle metriche sulla porta 8000
    print(f"Prometheus exporter running at http://{HOSTNAME}:8002/metrics")
    while True:
        time.sleep(1)



# Funzione principale del Data Collector
def run_data_collector():
    """
    Esegue il Data Collector che recupera i dati e li salva nel database,
    quindi invia una notifica generica a Kafka.
    """
    while True:
        # Recupero gli utenti dal database
        users = get_users_from_db()
        success_count = 0

        while users is None:
            print("Ancora nessun utente nel DB, ritento il recupero degli utenti")
            users = get_users_from_db()
        #Questo numero può aumentare o diminuire, in base se eliminiamo o aggiungiamo utenti è un gauge
        USERS_IN_DB.labels(app=APP_NAME, host=HOSTNAME).set(len(users)) 

        for user in users:
            email = user['email']
            ticker = user['ticker']
            
            # Uso il Circuit Breaker per gestire il recupero dei dati da yfinance
            try:
                value, timestamp = circuit_breaker.call(get_stock_data, ticker)
                save_stock_data(email, ticker, value)  
                success_count += 1
                print(f"Valore salvato per {email}: {ticker} - {value} - {timestamp}")
            except CircuitBreakerOpenException:
                print(f"Impossibile recuperare i dati per {ticker} - Circuit Breaker attivato.")
            except Exception as e:
                print(f"Errore durante il processo per {email}: {e}")
        
        # Invio una notifica a Kafka se almeno un dato è stato aggiornato
        if success_count > 0:
            send_alert_to_kafka()
        
        # Aspetto 60 secondi prima di ripetere il processo
        time.sleep(60)

if __name__ == "__main__":
    
    time.sleep(30)  # Aspetto 30 secondi prima di iniziare (per il db)
    # Kafka configuration with custom settings
    
    exporter_thread = threading.Thread(target=start_exporter)
    exporter_thread.daemon = True  # Fa sì che il thread termini quando il main thread termina
    exporter_thread.start()
    
    producer_config = {
        'bootstrap.servers': 'kafka:9092',  # Kafka broker address
        'acks': 'all',  # Ensure all in-sync replicas acknowledge the message
        'batch.size': 500,  # Maximum number of bytes to batch in a single request
        'max.in.flight.requests.per.connection': 1,  # Only one in-flight request per connection
        'retries': 3  # Retry up to 3 times on failure
    }

    # Creo il produttore Kafka
    producer = Producer(producer_config)
    topic = 'to-alert-system'  # Topic per notificare il completamento
    run_data_collector()

