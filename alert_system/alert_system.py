from confluent_kafka import Consumer, Producer
import json
import time
from cqrs import StockReadService


# Funzione per produrre messaggi Kafka
def produce_sync(producer, topic, value):
    """
    Funzione per produrre messaggi in modo sincrono (bloccante fino a che il messaggio non è inviato).
    """
    try:
        producer.produce(topic, value)
        producer.flush()  # Blocca fino a che tutti i messaggi in sospeso non sono inviati
        print(f"Messaggio prodotto sincrono su {topic}: {value}")
    except Exception as e:
        print(f"Errore durante la produzione del messaggio: {e}")

# Connessione al database MySQL
def get_user_data():
    """
    Recupera i dati degli utenti e i relativi ticker, high_value, low_value dal database.
    Continua a riprovare finché non si trovano dati.
    """
    stock_service = StockReadService()

    while True:
        try:
            user_data = stock_service.get_users_for_threshold_alert()
            if user_data:  # Se ci sono dati, li restituisce
                return user_data
            print("Nessun dato trovato nel database, riprovo...")
            time.sleep(5)  # Aspetta 5 secondi prima di riprovare
        except Exception as e:
            print(f"Errore durante il recupero dei dati dal database: {e}")
            time.sleep(5)  # Aspetta 5 secondi prima di riprovare


def listen_for_alerts():
    """
    Ascolta le notifiche nel topic 'to-alert-system' e verifica le condizioni di soglia per gli utenti.
    """
    consumer.subscribe([topic_alert_system])  # Sottoscrivo al topic 'to-alert-system'

    while True:
        # Poll per i nuovi messaggi dal topic
        msg = consumer.poll(1.0)
        if msg is None:
            continue  # Nessun messaggio ricevuto, continuo a fare polling
        if msg.error():
            print(f"Errore del consumer: {msg.error()}")
            continue

        print("Notifica ricevuta. Avvio la scansione del database...")

        # Recupera i dati degli utenti
        users = get_user_data()

        # Se non ci sono utenti, non fare commit dell'offset
        if not users:
            print("Nessun utente trovato nel DB, riprovo a fare polling...")
            continue

        success_count = 0  # Contatore per tracciare se sono stati trovati utenti da notificare

        for user in users:
            email = user['email']
            ticker = user['ticker']
            high_value = user['high_value']
            low_value = user['low_value']
            valore_ticker = user['valore']

            if valore_ticker is not None:
                if high_value is not None and high_value > 0 and valore_ticker >= high_value:
                    condition = 'high_value exceeded'
                elif low_value is not None and low_value > 0 and valore_ticker <= low_value:
                    condition = 'low_value exceeded'
                else:
                    continue  # Non è stato superato nessun limite

                # Creazione della notifica
                notification = {'email': email, 'ticker': ticker, 'condition': condition}
                produce_sync(producer, topic_notifier, json.dumps(notification))
                success_count += 1  # Se elaborato con successo, incrementa il contatore

        # Commit dell'offset solo se ci sono stati messaggi elaborati
        if success_count > 0:
            consumer.commit(asynchronous=False)  # Commit solo dopo aver elaborato messaggi

        time.sleep(1)

if __name__ == "__main__":
    time.sleep(20) 
    consumer_config = {
        'bootstrap.servers': 'kafka:9092',  # Kafka broker address
        'group.id': 'alert-system-group',  # Consumer group ID
        'auto.offset.reset': 'latest',  # Start reading from the latest message
        'enable.auto.commit': False,  # Automatically commit offsets periodically
    }
    producer_config = {
        'bootstrap.servers': 'kafka:9092',  # Kafka broker address
        'acks': 'all',  # Ensure all in-sync replicas acknowledge the message
        'batch.size': 500,  # Maximum number of bytes to batch in a single request
        'max.in.flight.requests.per.connection': 1,  # Only one in-flight request per connection
        'retries': 3  # Retry up to 3 times on failure
    }

    consumer = Consumer(consumer_config)
    producer = Producer(producer_config)

    topic_alert_system = 'to-alert-system'  # Topic for receiving notifications
    topic_notifier = 'to-notifier'  # Topic for sending notifications
    listen_for_alerts()








