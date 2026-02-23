paddleocr‑ha‑addon stellt einen lokal laufenden PaddleOCR‑FastAPI‑OCR‑Server als Home‑Assistant‑Supervisor‑Add‑on bereit und liefert eine begleitende HACS‑Integration als image_processing‑Platform zur automatischen Beleg‑ und Quittungserkennung.
Ziel ist lokale, datenschutzfreundliche OCR‑Verarbeitung mit strukturierter Feldextraktion für Tankquittungen.

Features
- Lokal laufender OCR‑Server auf Basis von PaddleOCR
- REST‑API zum Hochladen von Bildern und Abrufen strukturierter OCR‑Ergebnisse
- HACS‑Integration als image_processing‑Platform für Home Assistant
- Beleg‑Parser mit Regex und Heuristiken für Datum, Betrag, Händler, Liter, Preis pro Liter
- Konfigurierbar: Host, Port, Sprache, API‑Key optional
- Lizenz: Add‑on & Integration unter MIT License; PaddleOCR unter Apache 2.0

Repository Aufbau
paddleocr-ha-addon/
├─ addon/
│  ├─ Dockerfile
│  ├─ run.sh
│  ├─ app.py
│  └─ requirements.txt
├─ custom_components/paddleocr/
│  ├─ manifest.json
│  ├─ __init__.py
│  ├─ config_flow.py
│  ├─ image_processing.py
│  └─ parser.py
├─ hacs.json
├─ config.json
├─ README.md
└─ LICENSE



Installation – Add‑on (Supervisor)
- Add‑on‑Repository‑URL im Home‑Assistant‑Supervisor‑Add‑on‑Store → Repositories hinzufügen
- Add‑on installieren
- Add‑on konfigurieren (Port, Sprache, use_gpu) und starten
- Optional: Ingress aktivieren oder internen Host verwenden: http://supervisor:8000
Beispiel config.json Optionsauszug
{
  "options": {
    "port": 8000,
    "lang": "de",
    "use_gpu": false
  }
}



Installation – Integration über HACS
- HACS installieren (falls nicht vorhanden)
- HACS → Integrations → Custom Repository hinzufügen mit Repo‑URL paddleocr-hacs, Typ integration
- HACS → PaddleOCR → Installieren
- Integration über UI konfigurieren oder configuration.yaml nutzen
Beispiel configuration.yaml
image_processing:
  - platform: paddleocr
    name: paddleocr_receipt
    host: "http://supervisor:8000"
    api_key: "DEIN_API_KEY_OPTIONAL"
    lang: "de"



REST‑API Endpunkte
POST /ocr
- Bild hochladen → OCR‑Ergebnis als JSON
- Form‑Data: file (jpeg/png)
- Antwort:
{"lines":[{"text":"...","confidence":0.98,"box":[...]}, ...]}


POST /parse_receipt
- OCR + Parser → strukturierte Felder
- Form‑Data: file
- Antwort:
{
  "amount": "12.34",
  "date": "2026-02-23",
  "merchant": "ARAL",
  "liters": "40.00",
  "price_per_liter": "1.23",
  "raw_lines": [...]
}


Sicherheit
- Optionaler API‑Key via Header X-API-KEY
- Alternativ Basic Auth aktivierbar

Home Assistant Integration Details
Platform: image_processing
Entity Attributes
|  |  | 
| last_text |  | 
| parsed_amount |  | 
| parsed_date |  | 
| merchant |  | 
| raw_lines |  | 


Verhalten (image_processing.py)
- async_process_image sendet Bild an http://<host>:<port>/ocr
- Ergebnis wird als Entity‑Attribute gespeichert
- Optionaler Service paddleocr.parse_receipt ruft /parse_receipt auf
Beispiel Automation
automation:
  - alias: "OCR Receipt on Camera Snapshot"
    trigger:
      platform: state
      entity_id: camera.receipt_cam
      to: 'on'
    action:
      - service: image_processing.scan
        target:
          entity_id: image_processing.paddleocr_receipt



Parser‑Regeln und Heuristiken
Betrag
- Regex: \b\d{1,3}[.,]\d{2}\b
- Auswahl: höchste Wahrscheinlichkeit, Nähe zu Keywords wie TOTAL, SUMME, Betrag
Datum
- Formate: DD.MM.YYYY, DD/MM/YY, YYYY-MM-DD
- Validierung: plausibles Datum, Nähe zu Keywords DATE, DATUM
Händler
- obere Zeilen des Belegs
- Suche nach Tankstellen‑Keywords (SHELL, ARAL, TOTAL)
- Fallback: erste nicht‑leere Großbuchstaben‑Zeile
Liter & Preis pro Liter
- Liter: \b\d+[.,]\d{1,3}\s*l\b
- Preis/Liter: \b\d+[.,]\d{2}\s*(€|EUR)?\s*/\s*l\b

Performance & Hardware Hinweise
- CPU vs GPU: CPU nutzbar, GPU deutlich schneller
- RAM: mind. 2 GB empfohlen
- Modelle werden beim ersten Start geladen und gecached
- Optimierung: Grayscale, Resize, Denoise

Sicherheit & Netzwerk
- Add‑on standardmäßig lokal
- Keine öffentliche Exposition empfohlen
- Ingress bevorzugt
- Optionaler API‑Key oder Basic Auth

Troubleshooting
- Langsame Verarbeitung
Bildgröße reduzieren, Preprocessing aktivieren, GPU nutzen
- Model‑Download‑Fehler
Add‑on‑Logs prüfen, Netzwerkzugriff sicherstellen
- 401/403
API‑Key prüfen
- ARM‑Probleme
CPU‑kompatible Wheels nutzen oder Add‑on neu bauen

Entwicklung & Contribution
- Repo forken, Feature‑Branches nutzen
- PRs sollten Tests für parser.py enthalten
- Releases semantisch taggen (v0.1.0)
- CI: GitHub Actions für Linting & Tests
- Issues mit Logs & Repro‑Schritten eröffnen

Roadmap
- v0.1 Basis Add‑on, FastAPI OCR, HACS Integration, Grundparser
- v0.2 Config‑Flow‑UI, API‑Key, Ingress, erweiterte Parserregeln
- v0.3 Mehrsprachigkeit, Model‑Caching, ARM‑Optimierung, Beispiel‑Automationen

Lizenz
- Dieses Repository: MIT License
- PaddleOCR & PaddlePaddle: Apache 2.0

Kontakt & Support
- Repository: GitHub‑URL im Repo eintragen
- Issues: bitte mit Logs, HA‑Version, Add‑on‑Konfiguration & Repro‑Schritten
- Codeowner: @yourgithub im manifest.json


