# 🔄 Clear Browser Autofill

## Issue
Browser is auto-filling old username "kaldhar" in the login form.

## ✅ Fixed
I've updated the login and register forms to disable autocomplete with `autocomplete="off"`.

## How to Clear Auto-filled Data

### Method 1: Clear Individual Entry (Quick)
1. Click in the username field
2. You'll see a dropdown with saved usernames
3. Hover over "kaldhar"
4. Press `Shift + Delete` (Windows) or `Shift + Fn + Delete` (Mac)
5. This removes that specific entry

### Method 2: Clear Browser Cache (Complete)

#### Google Chrome
1. Press `Ctrl + Shift + Delete` (Windows) or `Cmd + Shift + Delete` (Mac)
2. Select "All time" from time range
3. Check "Autofill form data" or "Passwords and other sign-in data"
4. Click "Clear data"

#### Microsoft Edge
1. Press `Ctrl + Shift + Delete`
2. Select "All time"
3. Check "Passwords" and "Autofill form data"
4. Click "Clear now"

#### Firefox
1. Press `Ctrl + Shift + Delete`
2. Select "Everything"
3. Check "Form & Search History"
4. Click "Clear Now"

### Method 3: Use Incognito/Private Mode
1. Open browser in Incognito/Private mode
2. Go to http://127.0.0.1:5000
3. No autofill will happen
4. Login with any account

## Test Accounts

After clearing, you can login with:

**Admin:**
```
Username: admin
Password: password123
```

**Test User:**
```
Username: testuser
Password: test123
```

**Demo User:**
```
Username: demo_user
Password: password123
```

## ✅ Changes Made

Updated both forms to disable autocomplete:
- `templates/login.html` - Added `autocomplete="off"`
- `templates/register.html` - Added `autocomplete="off"`

## Refresh the Page

After I made the changes:
1. Go to http://127.0.0.1:5000/auth/login
2. Press `Ctrl + F5` (hard refresh)
3. The form should no longer auto-fill

## Note

The username "kaldhar" is not in your database. Your actual users are:
- admin
- demo_user
- testuser
- loki
- 123
- 1234

If you want to create a "kaldhar" user, you can register it!
