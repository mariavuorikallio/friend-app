# Pylint-raportti

## Pylintin palaute

### app.py
app.py:256:0: C0305: Trailing newlines (trailing-newlines)

### messages.py
messages.py:109:0: C0303: Trailing whitespace (trailing-whitespace)

### users.py
users.py:42:0: C0305: Trailing newlines (trailing-newlines)

### forum.py
forum.py:22:0: C0305: Trailing newlines (trailing-newlines)

### db.py
db.py:39:0: C0305: Trailing newlines (trailing-newlines)

---

## Perustelut

### Trailing whitespace / trailing newlines
- Useimmissa moduuleissa esiintyi ylimääräisiä välilyöntejä rivin lopussa tai tyhjiä rivejä tiedoston lopussa.  
- Nämä on poistettu VSCode-työkalulla “Trim Trailing Whitespace” ja loput tyhjät rivit on jätetty koodin selkeyden vuoksi, koska ne eivät vaikuta toimintaan.

### Docstring-ilmoitukset
- Alkuperäisissä tiedostoissa esiintyi paljon ilmoituksia `C0114` (Missing module docstring) ja `C0116` (Missing function or method docstring).  
- Sovelluksen kehityksessä päätettiin olla käyttämättä docstringejä, jotta koodi pysyy lyhyenä ja yksinkertaisena. Tämä on tietoinen valinta.

### Else-haarat returnin jälkeen
- Esimerkki ilmoituksesta: `app.py:264: R1705` ja `users.py:27:4`.  
- Koodissa else-haarat on säilytetty selkeyden vuoksi, vaikka Pylint suosittelee niiden poistamista returnin jälkeen. Tämä tuo esille eri vaihtoehtoiset polut koodissa ja parantaa luettavuutta.

### Inconsistent return
- Ilmoitukset: `app.py:250: R1710` ja `app.py:292: R1710`.  
- Nämä liittyvät funktioihin, joissa käsitellään GET ja POST -metodeja.  
- Käytännössä muita metodeja ei tule, joten funktio palauttaa aina arvon, eikä ongelmia esiinny.

### Vaarallinen oletusarvo
- Ilmoitukset: `db.py:10` ja `db.py:20` (W0102).  
- Oletusarvona olevat tyhjät listat eivät muutu funktiokutsuissa, joten ne eivät aiheuta ongelmia sovelluksessa.

### Import-ilmoitukset
- Alkuperäisissä Pylint-tuloksissa esiintyi virheilmoituksia import-komentoihin liittyen, esim. `E0401 Unable to import 'flask'` tai `Unable to import 'werkzeug.security'`.  
- Nämä johtuvat Pylintin rajoituksista, eivät siitä, että kirjasto puuttuisi. Sovelluksessa importit toimivat normaalisti kehitysympäristössä.

### Vakion nimi
- Ilmoitus: `config.py: C0103 secret_key`.  
- Sovelluksessa salaisuuteen viitataan pienellä kirjaimella `secret_key`, koska näin koodi on selkeämpi. Pylint suosittelee UPPER_CASE-muotoa vakiolle, mutta poikkeama on tietoinen valinta.

---

**Lopullinen arvio:**
- Koodin Pylint-arvosana on parantunut merkittävästi välilyöntien ja tyhjien rivien korjauksen jälkeen.  
- Sovelluksen toimivuus ei ole vaarantunut, ja kaikki Pylintin varoitukset on dokumentoitu ja perusteltu.
