# Azure App Service — Deployment Guide

## Step 1 — Create Azure App Service (Free Tier)

1. Go to [portal.azure.com](https://portal.azure.com)
2. **Create a resource** → **Web App**
3. Fill in:
   - **Resource Group**: create new, e.g. `caulong-rg`
   - **Name**: e.g. `caulong` (your URL will be `caulong.azurewebsites.net`)
   - **Runtime stack**: `Python 3.11`
   - **Operating System**: `Linux`
   - **Region**: Southeast Asia (or nearest)
   - **Pricing plan**: `Free F1` (select "Explore pricing plans" → Free)
4. Click **Review + Create** → **Create**

---

## Step 2 — Configure App Settings

In Azure Portal → your Web App → **Configuration** → **Application settings**, add:

| Name | Value |
|------|-------|
| `SECRET_KEY` | any long random string (e.g. `my-super-secret-key-2024`) |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |

Click **Save**.

---

## Step 3 — Set Startup Command

In Azure Portal → your Web App → **Configuration** → **General settings**:

- **Startup Command**: `bash startup.sh`

Click **Save**.

---

## Step 4 — Deploy via GitHub Actions

### 4a. Get Publish Profile
In Azure Portal → your Web App → **Overview** → **Download publish profile**

### 4b. Add GitHub Secrets
In your GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Secret Name | Value |
|-------------|-------|
| `AZURE_WEBAPP_NAME` | your app name (e.g. `caulong`) |
| `AZURE_PUBLISH_PROFILE` | paste the full contents of the downloaded `.PublishSettings` file |

### 4c. Trigger Deployment
Push to `main` branch — GitHub Actions will automatically deploy to Azure.

---

## Step 5 — Initialize Database (First Deploy Only)

After first deployment, open Azure Portal → your Web App → **SSH** (or use Kudu console at `https://<appname>.scm.azurewebsites.net`):

```bash
cd /home/site/wwwroot
python seed.py
```

This creates the SQLite database at `/home/caulong.db` and seeds sample data.

**Admin login:** `https://<appname>.azurewebsites.net/dang-nhap`  
**Credentials:** `admin` / `admin123`

---

## Free Tier Limitations (F1)

| Limit | Value |
|-------|-------|
| CPU | 60 minutes/day |
| RAM | 1 GB |
| Storage | 1 GB |
| Custom domain | Not supported (use `.azurewebsites.net`) |
| SSL | Included on `.azurewebsites.net` |
| Always On | Not available (app sleeps after inactivity) |

> **Note:** SQLite database is stored at `/home/caulong.db` which persists across restarts.
> Uploaded images are stored at `/home/uploads/` for the same reason.

---

## Troubleshooting

**App won't start:**
- Check **Log stream** in Azure Portal for errors
- Verify startup command is `bash startup.sh`
- Check that `SCM_DO_BUILD_DURING_DEPLOYMENT` = `true`

**Login not working:**
- Run `python seed.py` via SSH console to reset the admin password

**Uploads not saving:**
- Azure Free tier uses `/home/` as persistent storage — uploads go to `/home/uploads/`
- Make sure the `/home/uploads/` directory exists (created automatically by the app)
