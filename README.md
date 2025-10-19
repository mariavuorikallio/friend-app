# Friend App

**Friend App** on Flask-pohjainen web-sovellus, jossa käyttäjät voivat luoda profiilin, selata ja julkaista seuranhakuilmoituksia sekä keskustella muiden käyttäjien kanssa yksityisesti.

##  Sovelluksen toiminnot

* Käyttäjä voi luoda tunnuksen ja kirjautua sisään sovellukseen.
* Käyttäjä voi päivittää omaa profiiliaan (ikä, bio ja profiilikuva).
* Käyttäjä voi luoda, muokata ja poistaa omia seuranhakuilmoituksia.
* Käyttäjä voi selata ja hakea muiden ilmoituksia hakusanan perusteella.
* Käyttäjät voivat lähettää yksityisviestejä ilmoitusten kautta.
* Profiilikuvan lisäys ja muokkaus (.jpg, max 100 kt).
* Ilmoituksille voidaan määrittää luokkia tai ikäryhmiä.

---

## Asennusohjeet

1. **Kloonaa projekti:**
   ```bash
   git clone <repo-url>
   cd friend-app

2. **Luo ja aktivoi virtuaaliympäristö:**
   ```python3 -m venv venv
   source venv/bin/activate

 3. **Asenna riippuvuudet:**
    ```pip install -r requirements.txt

 4. **Luo tietokanta ja lisää alkutiedot:**
   sqlite3 database.db < schema.sql
   sqlite3 database.db < init.sql
   
 5. **Käynnistä sovellus:**
    flask run

 6. **Avaa selaimessa:**
    http://127.0.0.1:5000



