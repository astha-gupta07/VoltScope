# VoltScope — GitHub & Cloud Deployment Guide
## Step-by-Step Instructions to Publish on GitHub and Deploy to Free Cloud Web Hosting

This guide walks you through publishing your VoltScope project to **GitHub** and deploying it to **Render** (free cloud web service) so you have a live public link to showcase on your resume and college portfolio.

---

## Part 1: Setting Up Git on Your Windows PC

Since Git is not yet installed on your system, choose either **Option A** (recommended for beginners) or **Option B** (standard command line):

### Option A: GitHub Desktop (Recommended — Visual, No Command Line)
1. Download **GitHub Desktop** from: **[https://desktop.github.com/](https://desktop.github.com/)**
2. Install and launch GitHub Desktop, then sign in with your GitHub account.
3. In the top menu, click **File** -> **Add Local Repository...**.
4. Click **Choose...** and select your project folder:
   ```
   C:\Users\ACER\OneDrive\Desktop\electric vehicle project
   ```
5. If GitHub Desktop asks: *"This directory does not appear to be a Git repository. Would you like to create a repository here?"*, click **Create a repository**.
   - Name: `VoltScope`
   - Description: `Electric Vehicle Market Performance & Insights — End-to-End Analytics Platform`
   - Git Ignore: Select **None** (VoltScope already has an optimized `.gitignore`!).
   - License: Select **None** (VoltScope data is governed under CC BY 4.0).
   - Click **Create Repository**.
6. At the bottom-left of the screen, enter a commit summary:
   `feat: initial release of VoltScope EV Analytics`
   Click **Commit to main**.
7. In the top bar, click **Publish repository**:
   - Keep "Keep this code private" **unchecked** if you want it visible on your GitHub profile.
   - Click **Publish repository**.
8. Done! Your code is now live on your GitHub account!

---

### Option B: Git for Windows (Standard Terminal / CLI)
1. Download the official installer from: **[https://git-scm.com/download/win](https://git-scm.com/download/win)**
2. Run the downloaded `.exe` installer (accept the default recommended settings).
3. Open a fresh **PowerShell** window in your project directory:
   ```powershell
   cd "C:\Users\ACER\OneDrive\Desktop\electric vehicle project"
   ```
4. Verify Git is recognized:
   ```powershell
   git --version
   ```
5. Initialize the repository:
   ```powershell
   git init
   git add .
   git commit -m "feat: complete VoltScope EV Market Performance & Insights system"
   git branch -M main
   ```
6. Create an empty repository on GitHub:
   - Go to **[https://github.com/new](https://github.com/new)**
   - Repository name: `VoltScope`
   - Leave "Initialize with README", "Add .gitignore", and "License" **unchecked**.
   - Click **Create repository**.
7. Link and push your project:
   ```powershell
   git remote add origin https://github.com/<YOUR-GITHUB-USERNAME>/VoltScope.git
   git push -u origin main
   ```

---

## Part 2: Deploying to Free Cloud Web Hosting (Render.com)

Once your code is pushed to GitHub, you can deploy the Flask web application to **Render** in under 3 minutes for free:

### 1. Sign Up & Link GitHub
1. Navigate to **[https://render.com](https://render.com)** and click **Get Started for Free**.
2. Sign in using your **GitHub** account.

### 2. Create New Web Service
1. On your Render Dashboard, click **New +** -> **Web Service**.
2. Select **Build and deploy from a Git repository** -> Click **Next**.
3. Choose your `VoltScope` repository.

### 3. Configure Deployment Settings
- **Name**: `voltscope` (or `voltscope-analytics`)
- **Region**: Choose the closest region (e.g., Singapore, Frankfurt, or Oregon).
- **Branch**: `main`
- **Runtime**: `Python 3`
- **Build Command**:
  ```bash
  pip install -r requirements.txt && python scripts/run_pipeline.py
  ```
- **Start Command**:
  ```bash
  gunicorn app:app
  ```
- **Instance Type**: Select **Free** ($0 / month).

### 4. Deploy Web Service
1. Click **Deploy Web Service** at the bottom of the page.
2. Render will build the environment, run the pipeline, populate the SQLite database, and launch Gunicorn.
3. Within 2–3 minutes, Render will provide your live public URL:
   **`https://voltscope.onrender.com`**
4. You can now open this link on your phone, tablet, or laptop, and paste it directly into your resume, LinkedIn, or academic submission!

---

## Part 3: Connecting Your Published Tableau Dashboard

Once your website is live on Render:
1. Open Tableau Desktop / Public, connect to `data/exports/tableau/`, build your dashboard according to [TABLEAU_BUILD_GUIDE.md](TABLEAU_BUILD_GUIDE.md), and publish to Tableau Public.
2. Copy the share link of your published dashboard and story.
3. In your Render Dashboard, go to your `voltscope` Web Service -> **Environment** tab.
4. Add these Environment Variables:
   - `TABLEAU_DASHBOARD_URL` = `https://public.tableau.com/views/...`
   - `TABLEAU_STORY_URL` = `https://public.tableau.com/views/...`
5. Click **Save Changes** — Render will automatically redeploy and embed your live interactive Tableau views!
