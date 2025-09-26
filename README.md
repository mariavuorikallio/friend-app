# friend-app

## Sovelluksen toiminnot

* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan seuranhakuilmoituksia
* Käyttäjä näkee sovellukseen lisätyt seuranhakuilmoitukset
* Käyttäjä pystyy etsimään ilmoituksia hakusanalla
* Käyttäjä voi valita ilmoitukseen yhden tai useamman luokittelun. (esim. oman ikänsä)

## Sovelluksen asennus

Asenna flask -kirjasto:

...

$ pip install flask 
...

Luo tietokannan taulut ja lisää alkutiedot:

...

$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
...

Voit käynnistää sovelluksen näin:

...

$ flask run
...

- mahdolliset luokat tallennetaan tietokantaan.
