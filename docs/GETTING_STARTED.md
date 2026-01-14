# Getting Started - Schritt-für-Schritt Anleitung

Diese Anleitung führt dich durch alle Schritte, um den WhatsApp Chatbot von Null auf Live zu bringen.

---

## 📋 Übersicht der Schritte

1. **Twilio Account & WhatsApp einrichten** (15-20 Min)
2. **OpenAI API Key besorgen** (5 Min)
3. **Lokale Installation & Test** (10 Min)
4. **Deployment auf Railway** (15 Min)
5. **Twilio Webhook konfigurieren** (5 Min)
6. **End-to-End Test** (5 Min)

**Gesamtzeit: ca. 60 Minuten**

---

## Schritt 1: Twilio Account & WhatsApp einrichten

### 1.1 Twilio Account erstellen

1. **Gehe zu**: https://www.twilio.com/try-twilio
2. **Registrieren** mit Email, Name, Passwort
3. **Verifiziere** deine Email-Adresse
4. **Phone Number**: Gib deine echte Nummer an (für Verifikation)
5. **Verifikationscode** eingeben (kommt per SMS)

### 1.2 WhatsApp Sandbox aktivieren

1. **Im Twilio Dashboard**: Links → "Messaging" → "Try it out" → "Send a WhatsApp message"
2. **Oder direkt**: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
3. Du siehst eine **Sandbox-Nummer** (z.B. `+1 415 523 8886`)
4. Du siehst einen **Join-Code** (z.B. `join world-mountain`)

#### WhatsApp Sandbox aktivieren (wichtig!):

1. **Öffne WhatsApp** auf deinem Handy
2. **Neue Nachricht** an die Sandbox-Nummer (z.B. `+1 415 523 8886`)
3. **Sende den Join-Code exakt**: z.B. `join world-mountain`
4. Du bekommst Antwort: "Twilio Sandbox: ✅ You are all set!"

### 1.3 API Credentials kopieren

1. **Im Twilio Dashboard**: Startseite → "Account Info" (rechte Seite)
2. **Kopiere diese 3 Werte**:
   - **Account SID** (beginnt mit `AC...`)
   - **Auth Token** (klicke auf "Show" zum Anzeigen)
   - **Twilio WhatsApp Number** (die Sandbox-Nummer, z.B. `+14155238886`)

**Speichere sie temporär in einem Textdokument!**

---

## Schritt 2: OpenAI API Key besorgen

### 2.1 OpenAI Account erstellen

1. **Gehe zu**: https://platform.openai.com/signup
2. **Registrieren** mit Email oder Google/Microsoft
3. **Verifiziere** deine Email

### 2.2 Zahlungsmethode hinzufügen

> **Wichtig**: Für API-Zugang brauchst du eine hinterlegte Zahlungsmethode (auch wenn Free Credits verfügbar sind)

1. **Gehe zu**: https://platform.openai.com/account/billing/overview
2. **Add payment method** → Kreditkarte hinzufügen
3. **Optional**: Setze ein monatliches Limit (z.B. 10€) unter "Usage limits"

### 2.3 API Key erstellen

1. **Gehe zu**: https://platform.openai.com/api-keys
2. **"Create new secret key"** klicken
3. **Name**: z.B. "muuh-chatbot"
4. **Kopiere den Key** (beginnt mit `sk-proj-...` oder `sk-...`)

⚠️ **WICHTIG**: Der Key wird nur EINMAL angezeigt! Speichere ihn sicher.

**Kosten-Einschätzung für Tests**: 
- Pro Conversation: ~€0.001-0.003
- 100 Test-Conversations: ~€0.10-0.30
- Sehr überschaubar!

---

## Schritt 3: Lokale Installation & Test

### 3.1 Projekt Setup

```bash
# Terminal öffnen und ins Projekt-Verzeichnis
cd /Users/tomadomeit/WhatsApp_ChatBot_Muuuh

# Setup-Script ausführen (installiert alles)
bash setup.sh
```

Das Script:
- ✅ Erstellt Virtual Environment
- ✅ Installiert Dependencies
- ✅ Erstellt .env Datei
- ✅ Initialisiert Datenbank

### 3.2 .env Datei ausfüllen

```bash
# .env Datei bearbeiten
nano .env
# oder mit deinem Editor öffnen
```

**Fülle diese Werte aus**:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-DEIN_KEY_HIER

# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=dein_auth_token_hier
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Rest kann so bleiben
DATABASE_URL=sqlite:///./muuh_chatbot.db
ENVIRONMENT=development
LOG_LEVEL=INFO
HR_EMAIL=recruiting@muuuh.de
```

**Speichern**: `Ctrl+O`, `Enter`, `Ctrl+X` (bei nano)

### 3.3 Lokaler Test (ohne WhatsApp)

```bash
# Virtual Environment aktivieren (falls noch nicht aktiv)
source venv/bin/activate

# Test-Conversation Script starten
python scripts/test_conversation.py
```

**Test-Conversation**:

```
👤 You: Hallo!
🤖 Bot: Hi! 👋 Ich bin der muuh Recruiting-Bot...

👤 You: Welche Jobs sind offen?
🤖 Bot: Aktuell suchen wir: • (Junior) Conversational AI Developer...

👤 You: quit
```

✅ **Wenn das funktioniert, ist alles korrekt installiert!**

### 3.4 Server lokal starten

```bash
# FastAPI Server starten
python -m uvicorn app.main:app --reload
```

**Du solltest sehen**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Teste im Browser**: http://localhost:8000
- Du solltest JSON sehen: `{"message": "muuh Recruiting Chatbot API", ...}`

**Health Check**: http://localhost:8000/health
- Sollte `{"status": "healthy"}` zeigen

✅ **Server läuft!** → `Ctrl+C` zum Stoppen

---

## Schritt 4: Deployment auf Railway

### 4.1 Code auf GitHub pushen

#### Falls noch kein Git Repository:

```bash
# Im Projekt-Verzeichnis
cd /Users/tomadomeit/WhatsApp_ChatBot_Muuuh

# Git initialisieren
git init

# Alle Dateien hinzufügen
git add .

# Erster Commit
git commit -m "Initial commit: muuh WhatsApp Recruiting Chatbot"

# GitHub Repository erstellen (im Browser):
# 1. Gehe zu github.com
# 2. Klick auf "+" rechts oben → "New repository"
# 3. Name: "muuh-recruiting-chatbot"
# 4. Private oder Public (deine Wahl)
# 5. KEIN README, .gitignore, License (haben wir schon)
# 6. Create repository

# GitHub Remote hinzufügen (URL aus GitHub kopieren)
git remote add origin https://github.com/DEIN_USERNAME/muuh-recruiting-chatbot.git

# Pushen
git branch -M main
git push -u origin main
```

### 4.2 Railway Account erstellen

1. **Gehe zu**: https://railway.app
2. **"Login with GitHub"** (empfohlen) oder Email
3. **Autorisiere Railway** für GitHub-Zugriff

### 4.3 Projekt auf Railway deployen

1. **Dashboard**: Klick auf **"New Project"**
2. **"Deploy from GitHub repo"** auswählen
3. **Repository auswählen**: `muuh-recruiting-chatbot`
4. **"Deploy Now"** klicken

Railway erkennt automatisch Python und startet den Build.

### 4.4 Environment Variables hinzufügen

1. **In deinem Railway Projekt**: Tab **"Variables"** klicken
2. **"Raw Editor"** klicken (einfacher)
3. **Paste diese Werte** (mit DEINEN Credentials):

```bash
OPENAI_API_KEY=sk-proj-DEIN_KEY_HIER
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=dein_auth_token_hier
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
DATABASE_URL=sqlite:///./muuh_chatbot.db
ENVIRONMENT=production
LOG_LEVEL=INFO
HR_EMAIL=recruiting@muuuh.de
```

4. **"Update Variables"** klicken

Railway deployt automatisch neu mit den neuen Variablen.

### 4.5 Deployment URL finden

1. **Tab "Settings"** → Bereich **"Networking"**
2. **"Generate Domain"** klicken
3. Du bekommst eine URL wie: `https://muuh-recruiting-chatbot-production.up.railway.app`

**Kopiere diese URL!**

4. **Teste die URL im Browser**: `https://deine-url.railway.app`
   - Sollte JSON zeigen: `{"message": "muuh Recruiting Chatbot API", ...}`

5. **Health Check testen**: `https://deine-url.railway.app/health`

✅ **Deployment erfolgreich!**

---

## Schritt 5: Twilio Webhook konfigurieren

### 5.1 Webhook URL in Twilio eintragen

1. **Twilio Console**: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox
2. **Oder**: Messaging → Try it out → WhatsApp Sandbox Settings

3. **"WHEN A MESSAGE COMES IN"** Feld:
   - **URL eintragen**: `https://deine-railway-url.railway.app/webhook`
   - **Beispiel**: `https://muuh-recruiting-chatbot-production.up.railway.app/webhook`
   - **HTTP Method**: `POST` (sollte schon ausgewählt sein)

4. **"Save"** klicken

✅ **Webhook konfiguriert!**

---

## Schritt 6: End-to-End Test

### 6.1 Test-Nachricht senden

1. **Öffne WhatsApp** auf deinem Handy
2. **Gehe zum Chat** mit der Twilio Sandbox-Nummer
3. **Sende**: `Hallo!`

**Du solltest eine Antwort bekommen**:
```
Hi! 👋 Ich bin der muuh Recruiting-Bot.
Ich helfe dir gerne bei Fragen zu unseren offenen Stellen 
und dem Bewerbungsprozess.
Was möchtest du wissen?
```

### 6.2 Vollständigen Flow testen

**Test-Konversation**:

```
Du: Hallo!
Bot: [Begrüßung]

Du: Welche Jobs sind offen?
Bot: [Liste der Positionen]

Du: Ja, Conversational AI Developer interessiert mich
Bot: [Fragt nach AI-Erfahrung]

Du: Ja, ich arbeite mit ChatGPT und APIs
Bot: [Fragt nach API-Kenntnissen]

Du: Ja, täglich!
Bot: [Fragt nach Verfügbarkeit]

Du: Teilzeit
Bot: [Fragt nach Kontaktdaten]

Du: Max Mustermann, max@example.com
Bot: [Bestätigung mit Score]
```

### 6.3 Datenbank überprüfen

#### Lokal die Datenbank ansehen:

```bash
# In deinem Projekt-Verzeichnis
sqlite3 muuh_chatbot.db

# SQL Query
SELECT name, email, qualification_score FROM leads;

# Beenden
.exit
```

Du solltest deinen Test-Lead sehen!

### 6.4 Logs checken (Railway)

1. **Railway Dashboard** → dein Projekt
2. **Tab "Deployments"** → aktives Deployment
3. **"View Logs"** klicken

Du solltest sehen:
```
INFO - Received message from whatsapp:+49... : Hallo!
INFO - Extracted intent: greeting
INFO - Sending response: Hi! 👋 ...
```

✅ **Alles funktioniert End-to-End!**

---

## 🎉 Geschafft! Was jetzt?

### Nächste Schritte:

#### 1. **Für Demo-Video** (optional):
```bash
# Screen-Recording starten (macOS)
# Cmd+Shift+5 → Record

# WhatsApp Conversation durchführen
# Railway Logs zeigen
# Datenbank zeigen

# Video mit Loom hochladen: https://loom.com
```

#### 2. **Für Job-Bewerbung vorbereiten**:

Erstelle ein **GitHub README Badge** (sieht professionell aus):
```bash
# Repository auf public stellen (GitHub)
# README.md anpassen:
# - Link zu Railway-Demo
# - Link zu Loom-Video
# - Deine Kontaktdaten
```

#### 3. **Optimierungen** (optional):

- **Email-Benachrichtigungen**: Siehe `DEPLOYMENT.md` für SMTP-Setup
- **PostgreSQL**: Für Production-Skalierung
- **Rate Limiting**: API-Missbrauch verhindern
- **Analytics**: Track Metriken

---

## 🆘 Troubleshooting

### Problem: Bot antwortet nicht

**Checken**:
1. Railway Logs: Kommt die Nachricht an?
2. Webhook URL korrekt in Twilio?
3. Environment Variables auf Railway gesetzt?
4. Health Check funktioniert? (`/health`)

### Problem: OpenAI Fehler

**Mögliche Ursachen**:
- API Key falsch
- Billing nicht aktiv
- Rate Limit erreicht

**Lösung**: Platform.openai.com → Billing → Check Usage

### Problem: Twilio Fehler

**Checken**:
- Twilio Console → Monitor → Logs → Errors
- Webhook signature validation

### Problem: Railway Deployment failed

**Häufigste Ursachen**:
- `requirements.txt` fehlt
- Python Version inkompatibel
- Environment Variables fehlen

**Lösung**: Railway Logs checken für genaue Fehlermeldung

---

## 📞 Support

**Dokumentation**:
- `README.md` - Projekt-Übersicht
- `ARCHITECTURE.md` - Technische Details
- `DEPLOYMENT.md` - Deployment-Details

**Externe Ressourcen**:
- Twilio Docs: https://www.twilio.com/docs/whatsapp/api
- OpenAI Docs: https://platform.openai.com/docs
- Railway Docs: https://docs.railway.app

---

## ✅ Checkliste

Hake ab, wenn erledigt:

- [ ] Twilio Account erstellt
- [ ] WhatsApp Sandbox joined
- [ ] Twilio Credentials kopiert
- [ ] OpenAI API Key erstellt
- [ ] Lokal getestet (`test_conversation.py`)
- [ ] Server lokal läuft (`uvicorn`)
- [ ] Code auf GitHub gepusht
- [ ] Railway Projekt erstellt
- [ ] Environment Variables auf Railway gesetzt
- [ ] Deployment erfolgreich
- [ ] Railway URL funktioniert
- [ ] Twilio Webhook konfiguriert
- [ ] End-to-End WhatsApp Test erfolgreich
- [ ] Lead in Datenbank gespeichert

---

**Viel Erfolg! 🚀**
