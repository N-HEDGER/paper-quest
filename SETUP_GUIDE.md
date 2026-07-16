# Paper Quest — Setup Guide

This guide covers how to set up Google Sheets as a lightweight database for storing student progress, both for local development and Streamlit Community Cloud deployment.

---

## 1. Create a Google Cloud Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one) — e.g. "paper-quest"
3. Enable the **Google Sheets API**:
   - Go to **APIs & Services → Library**
   - Search for "Google Sheets API" and click **Enable**
4. Enable the **Google Drive API** (same steps — search "Google Drive API", click Enable)
5. Create a service account:
   - Go to **APIs & Services → Credentials**
   - Click **Create Credentials → Service Account**
   - Name it something like `paper-quest-sheets`
   - Skip the optional role/access steps
6. Create a key for the service account:
   - Click on the new service account
   - Go to the **Keys** tab
   - Click **Add Key → Create new key → JSON**
   - A `.json` file will download — keep this safe, you'll need it shortly

## 2. Create the Google Sheet

1. Go to [Google Sheets](https://sheets.google.com/) and create a new blank spreadsheet
2. Name it something like "Paper Quest Progress"
3. **Share it with the service account**: click "Share", paste the `client_email` from the JSON key file (it looks like `paper-quest-sheets@your-project.iam.gserviceaccount.com`), and give it **Editor** access
4. Copy the spreadsheet URL — you'll need it for the next step

The app will automatically create the header row (`username`, `week_4`, `week_5`, `week_7`, `week_8`, `week_9`, `week_10`, `xp`) the first time a user logs in.

## 3. Configure Secrets — Local Development

1. Copy the example secrets file:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
2. Open `.streamlit/secrets.toml` and fill in:
   - `sheet_url` — paste the full URL of your Google Sheet
   - `[gcp_service_account]` — copy every field from the downloaded JSON key file into the corresponding TOML fields

   The JSON key has fields like `"type": "service_account"`, `"project_id": "..."`, etc. Paste each value into the TOML template. The `private_key` field contains `\n` characters — keep them as-is.

3. Run the app locally:
   ```bash
   streamlit run app.py
   ```

**Important:** `.streamlit/secrets.toml` is already in `.gitignore` — never commit it.

## 4. Configure Secrets — Streamlit Community Cloud

1. Push your code to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io/) and deploy the app from your repo
3. Once the app is created, go to **Settings → Secrets**
4. Paste the entire contents of your `secrets.toml` into the secrets box. It should look like:

   ```toml
   sheet_url = "https://docs.google.com/spreadsheets/d/ABC123/edit"

   [gcp_service_account]
   type = "service_account"
   project_id = "paper-quest"
   private_key_id = "abc123"
   private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   client_email = "paper-quest-sheets@paper-quest.iam.gserviceaccount.com"
   client_id = "123456789"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
   ```

5. Click **Save** — the app will reboot with the new secrets

## 5. How It Works

- When secrets are configured, the app shows a login screen asking for a username
- The first time a username is entered, a new row is created in the Google Sheet
- Progress (which stage of each week the student is on) and XP are saved after every stage transition
- When a student logs in again, their progress is restored
- **Week gating**: each week is locked until the previous week is completed (stage = 5)
- When secrets are **not** configured (no `gcp_service_account` in secrets), the app runs without login — all weeks are unlocked and progress is not persisted. This is useful for quick local testing without setting up Google Sheets.

## 6. Checking the Sheet

The Google Sheet will look something like:

| username | week_4 | week_5 | week_7 | week_8 | week_9 | week_10 | xp  |
|----------|--------|--------|--------|--------|--------|---------|-----|
| jsmith   | 5      | 3      | 0      | 0      | 0      | 0       | 85  |
| abrown   | 5      | 5      | 2      | 0      | 0      | 0       | 140 |

Each `week_N` column stores the current stage (0–5). Stage 5 means the week is complete.
