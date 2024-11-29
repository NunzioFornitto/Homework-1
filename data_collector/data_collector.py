import time
import yfinance as yf
import mysql.connector
from datetime import datetime
from circuit_breaker import CircuitBreaker, CircuitBreakerOpenException

# Configura il Circuit Breaker
circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)

# Funzione per recuperare i dati da yfinance
def get_stock_data(ticker):
    """
    Recupera i dati dell'azione da yfinance per un determinato ticker.
    """
    #Recupero i dati dell'azione da yfinance per un giorno e restituisco il valore di chiusura e il timestamp
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")  # Recuperiamo i dati per 1 giorno
    if data.empty:
        raise Exception(f"Nessun dato disponibile per {ticker}")
    latest_value = data['Close'].iloc[-1]  # Ultimo valore di chiusura
    timestamp = data.index[-1]  # Timestamp dell'ultimo valore
    return latest_value, timestamp

# Funzione per recuperare gli utenti dal database
def get_users_from_db():
    """
    Recupera gli utenti registrati dal database.
    """
    connection = mysql.connector.connect(
        host='mysql', 
        user='Admin', 
        password='1234', 
        database='sistema_finanza'
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT email, ticker FROM utenti")
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    return users

# Funzione per memorizzare i dati nel database
def save_stock_data(email, ticker, value):
    """
    Memorizza i dati relativi al valore azionario nel database.
    """
    connection = mysql.connector.connect(
        host='mysql', 
        user='Admin', 
        password='1234', 
        database='sistema_finanza'
    )
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO azioni (email, ticker, valore)
        VALUES (%s, %s, %s)
    """, (email, ticker, value))  # Non passo il timestamp perche' se lo calcola nel database, quando faccio diretto la insert
    connection.commit()
    cursor.close()
    connection.close()

# Funzione principale del Data Collector
def run_data_collector():
    """
    Esegue il Data Collector che recupera i dati e li salva nel database.
    """
    while True:
        # Recupera gli utenti dal database dalla tabella utenti e mi metto in email e ticker l'utente e il ticker azione
        users = get_users_from_db()
        
        for user in users:
            email = user['email']
            ticker = user['ticker']
            
            # Usa il Circuit Breaker per gestire il recupero dei dati da yfinance
            try:
                # Usa il circuito per chiamare get_stock_data in modo protetto
                #Qui non si passano gli argomenti in get_stock_data perche' vengono passati in call
                #la funzione call fatta nel circuit breaker permette di chiamare
                #qualsiasi funzione e passare gli argomenti "esternamente".
                value, timestamp = circuit_breaker.call(get_stock_data, ticker)
                save_stock_data(email, ticker, value)  
                print(f"Valore salvato per {email}: {ticker} - {value} - {timestamp}")
            except CircuitBreakerOpenException:
                print(f"Impossibile recuperare i dati per {ticker} - Circuit Breaker attivato.")
            except Exception as e:
                print(f"Errore durante il processo per {email}: {e}")
        
        # Aspetta 1 minuto prima di ripetere il processo
        time.sleep(60)

if __name__ == "__main__":
    run_data_collector()
