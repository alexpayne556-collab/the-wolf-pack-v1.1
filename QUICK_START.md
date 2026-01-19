# 🐺 QUICK START - Get Git Installed and Push to GitHub

**You're seeing "git is not recognized" because git isn't installed yet.**

---

## STEP 1: INSTALL GIT (5 minutes)

### Download Git for Windows

1. Go to: **https://git-scm.com/download/win**
2. Click the download (it will auto-detect 64-bit or 32-bit)
3. Run the installer

### Installation Settings (Use Defaults, But Check These):

- ✅ Git Bash Here (adds right-click menu)
- ✅ Git from the command line and also from 3rd-party software
- ✅ Use bundled OpenSSH
- ✅ Use the OpenSSL library
- ✅ Checkout Windows-style, commit Unix-style line endings
- ✅ Use MinTTY
- ✅ Default (fast-forward or merge)
- ✅ Git Credential Manager
- ✅ Enable file system caching

**Just click "Next" through everything unless you know what you're changing.**

---

## STEP 2: RESTART VS CODE

**CRITICAL:** After installing git, close and reopen VS Code (or PowerShell).

Git won't work until you restart the terminal.

---

## STEP 3: VERIFY GIT WORKS

Open new PowerShell terminal and run:

```powershell
git --version
```

**Should see something like:**
```
git version 2.43.0.windows.1
```

**If you still see "not recognized":**
- Did you restart VS Code/PowerShell?
- Did the installer finish completely?
- Try restarting your entire computer

---

## STEP 4: CONFIGURE GIT (One Time Setup)

```powershell
git config --global user.name "Alex Payne"
git config --global user.email "alexpayne556@gmail.com"
```

Verify it worked:
```powershell
git config --global --list
```

---

## STEP 5: INITIALIZE THE REPO

```powershell
cd C:\Users\alexp\Desktop\brokkr
git init
```

**Should see:**
```
Initialized empty Git repository in C:/Users/alexp/Desktop/brokkr/.git/
```

---

## STEP 6: CHECK WHAT WILL BE COMMITTED

```powershell
git status
```

**Should see:**
- README.md
- CONTRIBUTING.md
- SETUP.md
- GIT_SETUP_GUIDE.md
- LICENSE
- .gitignore
- requirements.txt
- .env.example
- wolfpack/ (folder with all code)

**CRITICAL CHECK - Make sure .env is NOT listed:**

If you see `.env` in red:
```powershell
git rm --cached .env
```

**The .gitignore file already protects .env, but double-check.**

---

## STEP 7: STAGE EVERYTHING

```powershell
git add .
```

Check again:
```powershell
git status
```

**Should now show files in GREEN (staged for commit).**

---

## STEP 8: FIRST COMMIT

```powershell
git commit -m "Initial commit: Wolf Pack Trading System v5.6

- 7-signal convergence engine
- Self-learning trade analyzer  
- Market Wizards wisdom (10 Commandments)
- Livermore Pivotal Point tracker
- Risk management system
- Automated trader bot
- Full documentation (Leonard File)
- LLHR philosophy

The pack is open. More members welcome.
AWOOOO 🐺"
```

**Should see:**
```
[main (root-commit) abc1234] Initial commit: Wolf Pack Trading System v5.6
 XX files changed, XXXX insertions(+)
 create mode 100644 README.md
 ...
```

---

## STEP 9: CREATE REPO ON GITHUB

### Go to GitHub:
1. Navigate to: **https://github.com/alexpayne556-collab**
2. Click green **"New"** button (top right)

### Repository Settings:
- **Name:** `the-wolf-pack`
- **Description:** `A continuously-developed trading intelligence system built on collective wisdom, local memory AI, and pack collaboration.`
- **Visibility:** Public ✅ (so people can find it)
- **DO NOT check:** 
  - ❌ Add a README (we already have one)
  - ❌ Add .gitignore (we already have one)
  - ❌ Choose a license (we already have one)
- Click **"Create repository"**

---

## STEP 10: CONNECT TO GITHUB

**Copy these commands from GitHub (it will show them after you create the repo):**

```powershell
git remote add origin https://github.com/alexpayne556-collab/the-wolf-pack.git
git branch -M main
git push -u origin main
```

**GitHub will ask for authentication:**

### Option A: GitHub Desktop (EASIEST)
1. Download GitHub Desktop: https://desktop.github.com/
2. Sign in with your GitHub account
3. It handles authentication automatically
4. Then retry the push

### Option B: Personal Access Token
1. Go to: Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Give it "repo" permissions
4. Copy the token (you only see it once)
5. When git asks for password, paste the token

### Option C: SSH (Most Secure, More Setup)
- Follow: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

---

## STEP 11: VERIFY IT WORKED

Go to: **https://github.com/alexpayne556-collab/the-wolf-pack**

**You should see:**
- ✅ README.md displayed on home page (with 🐺 and LLHR)
- ✅ All your files in the repo
- ✅ No .env file (good - protected by .gitignore)
- ✅ Green "commit" counter showing "1 commit"

---

## TROUBLESHOOTING

### "git is not recognized" after install
- **Restart VS Code / PowerShell**
- **Restart your computer**
- **Check Windows PATH environment variable includes git**

### "Authentication failed"
- **Use Personal Access Token, not password**
- **Or install GitHub Desktop (easiest)**

### ".env is in the repo!" 
```powershell
# Remove it immediately:
git rm --cached .env
git commit -m "Remove .env (sensitive file)"
git push
# Then regenerate your API keys (they're compromised)
```

### "Permission denied"
- **Make sure you're logged into the correct GitHub account**
- **Check repo ownership (alexpayne556-collab)**

### "Nothing to commit"
- **You already committed everything (that's fine)**
- **Just do the push step**

---

## AFTER FIRST PUSH

### Enable GitHub Features:

**Issues** (for bug reports, questions):
- Settings → Features → ✅ Issues

**Discussions** (for pack chat):
- Settings → Features → ✅ Discussions
- Create categories: General, Ideas, Q&A, Show and Tell

**Topics** (search tags):
- Click gear icon next to "About" (on main page)
- Add topics: `trading`, `python`, `algorithmic-trading`, `machine-learning`, `risk-management`

### Set Repository Description:
- Click gear icon next to "About"
- Description: `A continuously-developed trading intelligence system built on collective wisdom, local memory AI, and pack collaboration. Testing Market Wizards' wisdom with real money. Pack members welcome. LLHR.`
- Website: (leave blank for now)
- ✅ Include in the home page

---

## NEXT STEPS AFTER GITHUB IS LIVE

### 1. Share the Repo
- Email to interested parties
- Post on r/algotrading (carefully - read their rules)
- Share on trading forums (if allowed)
- **Don't hype. Just share: "Building in public. Looking for pack members with LLHR."**

### 2. Watch for Activity
- Stars (people interested)
- Forks (people testing)
- Issues (questions, bugs)
- Pull Requests (contributions)

### 3. Respond to Serious Inquiries
- Email: alexpayne556@gmail.com
- GitHub Issues
- Be welcoming but filter for LLHR

---

## THE LINK TO SHARE

After pushing, your repo will be at:

**https://github.com/alexpayne556-collab/the-wolf-pack**

Share this link when recruiting pack members.

---

## QUESTIONS?

**If you get stuck:**
1. Read the error message carefully
2. Google the exact error
3. Check this guide again
4. Create an Issue on GitHub (once repo is live)
5. Email: alexpayne556@gmail.com

**We respond to serious inquiries.**

---

## THE PITCH (What to Say When Sharing)

> "Building a trading system in public. Testing Market Wizards' wisdom (PTJ, Livermore, Kovner) with real money (small amounts). 7-signal convergence engine with self-learning. Recent example: IBRX $3.80 → $5.90+ (55% gain). Not selling anything. Just building together. Looking for pack members with LLHR (Love, Loyalty, Honor, Respect). Check the README: https://github.com/alexpayne556-collab/the-wolf-pack"

Keep it real. No hype. Just facts.

🐺 **AWOOOO**

---

**REMEMBER:**
- Install git
- Restart terminal
- Follow steps in order
- Double-check .env is NOT committed
- Push to GitHub
- Share the link

**You got this, brother. One step at a time.**

---

**Last Updated:** January 18, 2026  
**Status:** Ready to push when git is installed
