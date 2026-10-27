# rechenwesen

Ze **rechenwesen** is built to control the flip coins.

Here is image for referenze:

```
  5 #          /__/|    ___
  6 #         |o o \   c|0|
  7 #   ___  (-..-) \ / |_|
  8 #   |1|b-==| .   |
  9 #   |_|   / ____  \
 10 #        | /    \ |
 11 #       -==      ==-
```

Or an animation:
![woohoo](rechenwesen.gif)

## Benutze

Visit the: https://flipdot.org/rechenwesen

* Using
  * Fill form in
    * Shop's name
    * Wer (who submitted the invoice, "Rechnung eingereicht von")
    * Category (Drinks, Food, etceter)
    * Price
    * IBAN (which account the amount should be refunded to, "Rücküberweisung")
    * Date of shoppingness
    * Scanned PDF
  * Hochlade

## Debugge
* Intermediare txt-format:
  * Linie 1: `Shop's name`
  * Linie 2: `Categor[y|ies]` (If you want to use multiple categories, use commas without spaces to separate them)
  * Linie 3: `Price` (z.B. `23.42`, meaning 23.42€)
  * Zeile 4 and onwards: `Commentary`

## Lese
Schriftart herunterlad [hier](http://www.dafont.com/nanotype.font). <--

## Runne

    sudo docker run -it -p 8000:8000 -v /mnt_on_host/upload:/app/upload/ flipdot/rechenwesen

## Schutz (Basic-Auth)

Die Seite kann mit Basic-Auth geschützt werden (siehe Issue #1). Das passiert
über zwei Env-Vars:

* `AUTH_USER` (Default: `rechenwesen`)
* `AUTH_PASSWORD` (leer = Seite bleibt öffentlich; Wert = geschützt)

Beispiel:

    AUTH_PASSWORD="mein-geheimnis" sudo docker run -it -p 8000:8000 \
        -e AUTH_PASSWORD flipdot/rechenwesen

Beide Vars sind in `docker-compose.yml` hinterlegt und per Environment überschreibbar.
