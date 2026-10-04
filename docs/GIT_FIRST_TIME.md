# Git for the first time (no command line needed)

You can do everything here in a web browser. GitHub's screens change their wording now and then, so if a button is named slightly
differently, look for the one that means the same thing.

## Five words, in plain English
- **Repository ("repo")**: a folder that remembers every change ever made to it. This whole starter is one.
- **Commit**: a saved snapshot, with a short note saying what you changed. Like "Save", but it never overwrites the past.
- **SHA / commit ID**: the short code (like `a1b2c3d`) that names one exact snapshot. The website records which one it was built from.
- **Branch**: a parallel copy for trying things. **Ignore this for now.** Stay on the default one, called `main`.
- **Push / pull**: sending your changes up to GitHub, and bringing others' changes down. You only need these if you use GitHub Desktop.

## 1. Create the repository (about 10 minutes)
1. Make a free account at github.com.
2. Click **New repository**.
3. Name it `world-table-contributions`.
4. Choose **Public**. This is fine because everything in here is meant to be public. It also means **nothing private may ever be put in it** (see "What never goes in", below).
5. Leave **Add a README**, **.gitignore** and **license** all *unticked*. The starter already has its own.
6. Click **Create repository**.

## 2. Put the starter in
1. Unzip the starter on your computer. You get a folder called `world-table-contributions`.
2. On the empty repository page, click the link that says **uploading an existing file**.
3. Open the unzipped folder and drag **everything inside it** (the folders and files, not the zip) onto the GitHub page.
   - On a Mac, press **Cmd + Shift + .** first so hidden items (`.github`, `.gitignore`) are visible and come along.
   - If dragging folders does not work in your browser, try Chrome or Edge.
4. In the box at the bottom write a note such as `Add starter structure`, then click **Commit changes**. That is your first commit.

## 3. Add the licence text
The recipes are CC BY-SA 4.0, so the repo should carry the official licence.
1. Go to https://creativecommons.org/licenses/by-sa/4.0/ and follow the link to the **full legal code**.
2. Copy the whole text.
3. In your repo click **Add file → Create new file**, name it `LICENSE`, paste the text, and **Commit**.

## 4. Turn on the automatic checker (optional but lovely)
The starter includes a checker (`tools/validate.py`) that reads every recipe and tells you in plain English what is wrong.
GitHub can run it for you every time you commit, so you don't need Python.
1. Click the **Actions** tab. If GitHub asks, allow workflows to run.
2. After each commit, a small **green tick** (all good) or **red cross** (something to fix) appears next to it.
3. Click a red cross, open the failed run, and read the lines starting with `problem:`. They say exactly which file and what to change.

## 5. Add a recipe by hand
1. Open `examples/example-tomato-bruschetta.json` and copy its contents.
2. Open the `recipes` folder, click **Add file → Create new file**, and name it `recipes/your-recipe-name.json`. The name must be lowercase, with hyphens, and match the `slug` inside the file.
3. Paste, then change every field. `docs/RECORD_FORMAT.md` explains each one. Commit.
4. Watch for the green tick. If it is red, fix what it says and commit again. Each fix is a new commit and that is completely normal.
5. A photo: only if the contributor confirmed it is theirs. Click **Add file → Upload files** inside `images/`, and set the `image.file` field to match.

## 6. Pinning: how the website knows exactly what it is showing
Every commit has a SHA. When the website is built it records the SHA it used, the same way it records one for the main 501 recipes.
- To copy a SHA: click the **commits** link on the repo's front page and copy the short code beside any commit.
- **Never delete or rewrite history.** To undo a mistake, open the commit and use **Revert**, which makes a *new* commit that undoes it.

## What never goes in (the repo is public)
- Passwords, `config.php`, anything from the website's `admin` folder
- IP addresses, emails, or contributors' private details
- Recipes that are **not approved yet**, or that someone asked to withdraw
- Photos you don't have permission to publish

## If you prefer a desktop app
Install **GitHub Desktop**, choose **Clone a repository**, copy your recipe files into the folder it creates, then **Commit to main** and **Push origin**. It does exactly what the web steps do.

## You cannot break the live website by editing this repo
Until the website's build is connected to it, nothing here changes anything public. And because Git remembers everything, any mistake can be undone.

## Later (not needed now)
A private repository with an access token, branches and pull requests for reviewing changes, and the build step that merges these recipes into the site.
