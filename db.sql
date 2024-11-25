-- Creazione del Database (solo se non esiste già)
CREATE DATABASE IF NOT EXISTS sistema_finanza;

-- Selezionare il database
USE sistema_finanza;

-- Creazione della tabella degli utenti (solo se non esiste già)
CREATE TABLE IF NOT EXISTS utenti (
    id_utente INT AUTO_INCREMENT PRIMARY KEY,         -- ID univoco per ogni utente
    email VARCHAR(255) UNIQUE NOT NULL,                -- Email dell'utente, unica
    ticker VARCHAR(20) NOT NULL,                       -- Codice dell'azione associato all'utente
    creato_il DATETIME DEFAULT CURRENT_TIMESTAMP,      -- Data e ora di creazione
    aggiornato_il DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  -- Data e ora di aggiornamento
);

-- Creazione della tabella dei valori azionari (solo se non esiste già)
CREATE TABLE IF NOT EXISTS azioni (
    id_azione INT AUTO_INCREMENT PRIMARY KEY,         -- ID univoco per ogni valore azionario
    email VARCHAR(255),                                -- Email dell'utente a cui appartiene il valore
    ticker VARCHAR(20),                               -- Codice dell'azione
    valore FLOAT,                                      -- Valore dell'azione
    time_stamp DATETIME DEFAULT CURRENT_TIMESTAMP,      -- Data e ora in cui è stato recuperato il valore
    FOREIGN KEY (email) REFERENCES utenti(email) ON DELETE CASCADE  -- Relazione con la tabella degli utenti
);

-- Creazione del trigger per gestire l'aggiornamento dei ticker nella tabella azioni
DELIMITER $$

CREATE TRIGGER before_update_ticker
BEFORE UPDATE ON utenti
FOR EACH ROW
BEGIN
    -- Elimina le azioni associate al vecchio ticker dell'utente se viene aggiornato il ticker associato all'utente
    DELETE FROM azioni 
    WHERE email = OLD.email AND ticker = OLD.ticker;
END$$

DELIMITER ;

-- Creazione dell'utente Admin (solo se non esiste già)
CREATE USER IF NOT EXISTS 'Admin'@'%' IDENTIFIED BY '1234';

-- Concedere tutti i privilegi all'utente Admin per il database sistema_finanza
GRANT ALL PRIVILEGES ON sistema_finanza.* TO 'Admin'@'%';

-- Applicare i privilegi
FLUSH PRIVILEGES;

-- Inserimento di dati nella tabella utenti esempio in modo che il data collector trovi già dei dati
INSERT INTO utenti (email, ticker)
VALUES
    ('utente1@example.com', 'AAPL'),
    ('utente2@example.com', 'GOOG');

-- Inserimento di dati nella tabella azioni esempio in modo da debuggare la media degli ultimi n valori
INSERT INTO azioni (email, ticker, valore)
VALUES
    ('utente1@example.com', 'AAPL', 150.25),
    ('utente2@example.com', 'GOOG', 2800.50);
