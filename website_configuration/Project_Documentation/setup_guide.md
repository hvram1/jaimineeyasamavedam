# Jaimineeya Sama Vedam Website - Complete Setup Guide

This guide will walk you through setting up jaimineeyasamavedam.org from scratch using Hostinger and WordPress.

---

## Prerequisites

- [x] Domain registered: **jaimineeyasamavedam.org** (at GoDaddy)
- [ ] Hostinger account (will create in Step 1)
- [ ] Email address for admin account
- [ ] Payment method for Hostinger (~₹149/month)

---

## Part 1: Hostinger Account & WordPress Installation

### Step 1: Sign Up for Hostinger

1. **Visit Hostinger**: Go to [hostinger.in](https://www.hostinger.in)

2. **Choose Single Web Hosting Plan**:
   - Click on "Web Hosting" → "Single Web Hosting"
   - Price: ~₹149/month (may have promotional pricing)
   - Features included:
     - 100 GB SSD storage
     - ~10,000 visits/month
     - Free SSL certificate
     - 1 website

3. **Select Duration**:
   - Recommended: 12 months (usually best value)
   - Can start with 1 month to test

4. **Create Account**:
   - Enter email address
   - Create password
   - Complete payment

5. **Access hPanel**:
   - After payment, you'll receive login credentials
   - Go to [hpanel.hostinger.com](https://hpanel.hostinger.com)
   - Log in with your credentials

---

### Step 2: Install WordPress

1. **In hPanel Dashboard**:
   - Click on "Websites" in left sidebar
   - Click "Add Website" or "Setup Website"

2. **Choose WordPress**:
   - Select "Install WordPress"
   - Choose "Latest Version"

3. **Configure WordPress Installation**:
   ```
   Site Title: Jaimineeya Sama Vedam
   Admin Username: [Choose a secure username]
   Admin Password: [Choose a strong password - SAVE THIS!]
   Admin Email: [Your email address]
   Language: English
   ```

4. **Important - Save These Credentials**:
   ```
   WordPress Admin URL: Will be provided after installation
   WordPress Username: [What you chose]
   WordPress Password: [What you chose]
   ```

5. **Click "Install"**:
   - Installation takes 1-3 minutes
   - You'll see a success message with your WordPress admin URL

6. **Access WordPress**:
   - Your temporary URL will be something like: `http://[numbers].hostingersite.com`
   - Admin login: `http://[numbers].hostingersite.com/wp-admin`
   - Login with the credentials you created

> [!IMPORTANT]
> **Keep this temporary URL accessible** - you'll use it while DNS is propagating (24-48 hours).

---

## Part 2: Connect Your GoDaddy Domain

### Step 3: Get Hostinger Nameservers

1. **In Hostinger hPanel**:
   - Go to "Domains" section
   - Click "Connect Domain"
   - Select "Use existing domain"
   - Enter: `jaimineeyasamavedam.org`

2. **Copy Nameservers**:
   - Hostinger will show you nameservers, typically:
     ```
     ns1.dns-parking.com
     ns2.dns-parking.com
     ```
   - **Copy these exactly** - you'll need them in the next step

---

### Step 4: Update GoDaddy Nameservers

1. **Log into GoDaddy**:
   - Go to [godaddy.com](https://www.godaddy.com)
   - Sign in to your account

2. **Access Domain Settings**:
   - Click on your profile icon → "My Products"
   - Find "jaimineeyasamavedam.org"
   - Click "DNS" or "Manage DNS"

3. **Change Nameservers**:
   - Scroll down to "Nameservers" section
   - Click "Change" or "Manage"
   - Select "I'll use my own nameservers"

4. **Enter Hostinger Nameservers**:
   ```
   Nameserver 1: ns1.dns-parking.com
   Nameserver 2: ns2.dns-parking.com
   ```
   (Use the exact nameservers Hostinger provided)

5. **Save Changes**:
   - Click "Save"
   - You'll see a warning that changes take 24-48 hours
   - Click "Continue"

> [!WARNING]
> **DNS Propagation Time**: It takes 24-48 hours for nameserver changes to propagate worldwide. During this time:
> - Use the temporary Hostinger URL to work on your site
> - Your domain may show old content or "not found"
> - This is normal and will resolve automatically

---

### Step 5: Verify Domain Connection (After 24-48 hours)

1. **Check Domain Status**:
   - After 24-48 hours, visit: `http://jaimineeyasamavedam.org`
   - You should see the default WordPress page

2. **Update WordPress URLs**:
   - Go to WordPress Admin: `http://jaimineeyasamavedam.org/wp-admin`
   - Navigate to: Settings → General
   - Update both fields to:
     ```
     WordPress Address (URL): https://jaimineeyasamavedam.org
     Site Address (URL): https://jaimineeyasamavedam.org
     ```
   - Click "Save Changes"

3. **Enable SSL (HTTPS)**:
   - In Hostinger hPanel, go to "SSL"
   - Enable SSL for jaimineeyasamavedam.org
   - Install "Really Simple SSL" plugin in WordPress (covered in next section)

---

## Part 3: WordPress Theme & Plugin Installation

### Step 6: Install a Theme

1. **Choose a Theme**:
   - **Recommended for Release 1**: Astra (free)
   - Alternative: GeneratePress (free)

2. **Install Astra Theme**:
   - In WordPress Admin, go to: Appearance → Themes
   - Click "Add New"
   - Search for "Astra"
   - Click "Install" on Astra theme
   - Click "Activate"

3. **Basic Astra Configuration**:
   - Go to: Appearance → Customize
   - Set colors:
     - Primary Color: `#FF6B35` (Saffron)
     - Text Color: `#2C3E50` (Dark Gray)
     - Background: `#FEFAE0` (Cream)
   - Click "Publish"

---

### Step 7: Install Essential Plugins

Install these plugins one by one:

#### Security & Performance

| Plugin | Purpose | Installation |
|--------|---------|--------------|
| **Really Simple SSL** | Enable HTTPS | Plugins → Add New → Search → Install → Activate |
| **Site Kit by Google** | Analytics | Plugins → Add New → Search → Install → Activate |
| **UpdraftPlus** | Backup | Plugins → Add New → Search → Install → Activate |

#### For Release 1 Core Features

| Plugin | Purpose |
|--------|---------|
| **Contact Form 7** | Contact forms |
| **Download Monitor** | PDF download tracking |
| **HTML5 Audio Player** | Audio player for chants |
| **WP Google Maps** | Gurukulam finder map |
| **TablePress** | For padhathi comparison tables |

#### Installation Steps (Same for All):
1. Go to: Plugins → Add New
2. Search for plugin name
3. Click "Install Now"
4. Click "Activate"

> [!TIP]
> **Don't install all plugins at once**. Install 3-4, activate them, then install the next batch. This makes troubleshooting easier if there are conflicts.

---

### Step 8: Configure Google Fonts for Indic Scripts

WordPress supports Unicode by default, but you'll want proper fonts for Devanagari, Grantha, and Malayalam.

#### Method 1: Using a Plugin (Easiest)

1. Install plugin: **Use Any Font** or **Custom Fonts**
2. Upload Noto fonts from Google Fonts

#### Method 2: Manual CSS (Recommended)

1. Go to: Appearance → Customize → Additional CSS

2. Add this code:
```css
/* Import Google Fonts for Indic Scripts */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600&family=Noto+Sans+Grantha&family=Noto+Sans+Malayalam:wght@400;600&display=swap');

/* Apply Devanagari font */
.devanagari, .sanskrit {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 1.2em;
  line-height: 1.8;
}

/* Apply Grantha font */
.grantha {
  font-family: 'Noto Sans Grantha', serif;
  font-size: 1.2em;
  line-height: 1.8;
}

/* Apply Malayalam font */
.malayalam {
  font-family: 'Noto Sans Malayalam', sans-serif;
  font-size: 1.2em;
  line-height: 1.8;
}
```

3. Click "Publish"

---

## Part 4: Create Page Structure

### Step 9: Create Main Pages

Create these pages in WordPress:

1. **Go to**: Pages → Add New

2. **Create these pages** (one at a time):

| Page Title | URL Slug | Template |
|------------|----------|----------|
| Home | home | Homepage |
| Sacred Texts | texts | Default |
| Padhathi Guide | padhathis | Default |
| Audio Archives | audio | Default |
| Video Archives | video | Default |
| Gurukulam Finder | find-gurukulam | Default |
| Getting Started | learn | Default |
| FAQ | faq | Default |
| Articles | articles | Blog |
| Newsletter | newsletter | Default |
| Agraharams Directory | agraharams | Default |
| Contact | contact | Default |

#### For Each Page:
1. Enter page title
2. Set URL slug (click "Edit" next to permalink)
3. Add placeholder content: "Coming Soon"
4. Click "Publish"

---

### Step 10: Set Up Navigation Menu

1. **Go to**: Appearance → Menus

2. **Create Main Menu**:
   - Menu Name: "Main Navigation"
   - Click "Create Menu"

3. **Add Pages to Menu**:
   - Check these pages from the left sidebar:
     - Home
     - Audio Archives
     - Video Archives
     - Learn Sama Veda (with sub-items: Getting Started, Find Gurukulam, FAQ)
     - Community (with sub-items: Articles, Newsletter, Agraharams)
     - Contact
   - **For Sacred Texts (Library)**:
     - Click "Custom Links" arrow
     - URL: `https://sekharnarayanaswamy-del.github.io/jaimineeyasamavedam/index.html`
     - Link Text: "Sacred Texts"
     - Click "Add to Menu"
   - Click "Add to Menu" for the other checked pages

4. **Drag to organize**:
   - Drag items to create hierarchy
   - Indent items to create dropdown menus

5. **Set Menu Location**:
   - Check "Primary Menu" under Display location
   - Click "Save Menu"

---

### Step 11: Configure Homepage

1. **Set Static Homepage**:
   - Go to: Settings → Reading
   - Select "A static page"
   - Homepage: Select "Home"
   - Posts page: Select "Articles"
   - Click "Save Changes"

2. **Edit Homepage**:
   - Go to: Pages → All Pages
   - Click "Edit" on "Home"
   - Add content using blocks (next section has templates)

---

## Part 5: Content Templates

### Template: Homepage Three-Column Layout

Use this structure for the homepage:

```
[Three Columns Block]

Column 1: 📚 DOWNLOAD TEXTS
- Quick access to books & PDFs
- [Button: Browse Texts → /texts/]

Column 2: 🔍 LEARN SAMA VEDA
- New here? Start your journey
- [Button: Get Started → /learn/]

Column 3: 👥 COMMUNITY UPDATES
- Articles, news & events
- [Button: Read More → /articles/]

[Latest Updates Section]
- Recent posts from Articles

[Featured Audio Section]
- Embed sample audio player
```

---

### Template: Text Library Page (`/texts/`)

```markdown
# Sacred Texts Library

Browse and download Jaimineeya Sama Veda texts in multiple scripts.

## Available Texts

[Table using TablePress]

| Text | Script | Download |
|------|--------|----------|
| Purvarchika Samhita | Devanagari | [Download PDF] |
| Purvarchika Samhita | Grantha | [Download PDF] |
| Uttararchika Samhita | Devanagari | [Download PDF] |

[Search box - using SearchWP if installed]

---

📋 [View Padhathi Comparison Guide →](/padhathis/)
```

---

### Template: Gurukulam Finder (`/find-gurukulam/`)

```markdown
# Find a JSV Gurukulam

Locate Jaimineeya Sama Veda learning centers.

[WP Google Maps - Interactive Map]

## Directory

[Accordion or Cards for each gurukulam]

### 🏫 [Gurukulam Name], Chennai
- **Location**: Full address
- **Padhathi**: [Specific padhathi]
- **Programs**: Full-time, Weekend classes
- **Contact**: Phone, Email
- [Google Maps Link]

---

### 🏫 [Gurukulam Name], Kumbakonam
- **Location**: Full address
- **Padhathi**: [Specific padhathi]
- **Programs**: Residential
- **Contact**: Phone, Email
- [Google Maps Link]
```

---

### Template: Newsletter Page (Placeholder for Release 1)

```markdown
# Newsletter

## 📧 Coming Soon!

We're preparing a regular newsletter to keep you updated on:
- New texts and resources added to our library
- Upcoming events at JSV gurukulams
- Articles exploring Sama Veda traditions
- Community news and updates

**In the meantime**, bookmark our [Articles](/articles/) page for the latest content.

---

*Want to be notified when our newsletter launches?*  
[Contact us](/contact/) with "Newsletter Interest" in the subject line.
```

---

## Part 6: Final Configuration

### Step 12: Configure Site Kit for Analytics

1. **In WordPress Admin**:
   - Go to: Site Kit → Settings
   - Click "Connect to Google"
   - Follow authentication steps

2. **Enable Google Analytics**:
   - Select your Google account
   - Create or connect Analytics property
   - Follow prompts to complete setup

---

### Step 13: Test Everything

| Feature | Test | Expected Result |
|---------|------|-----------------|
| SSL/HTTPS | Visit https://jaimineeyasamavedam.org | 🔒 Shows secure |
| Navigation | Click all menu items | Pages load correctly |
| Indic Fonts | Add Devanagari text to a page | Displays correctly |
| Contact Form | Submit test form | Receives email |
| Mobile | Visit site on phone | Responsive design works |
| Download | Upload PDF, test download | File downloads with tracking |

---

## Part 7: Content Entry Workflow

### For Adding a New Text (PDF)

1. **Upload PDF**:
   - Media → Add New → Upload file
   - Or use Download Monitor plugin

2. **Create Text Entry**:
   - Create new page or post
   - Title: "Purvarchika Samhita - Devanagari"
   - Category: "Sacred Texts"
   - Script tag: "Devanagari"
   - Add download button linking to PDF

---

### For Adding Audio Files

1. **Upload to Media Library**:
   - Media → Add New
   - Upload MP3 file
   - Add title and description

2. **Embed on Page**:
   - Edit the Audio Archives page
   - Add "Audio" block
   - Select uploaded file
   - Or use HTML5 Audio Player plugin shortcode

---

### For Adding Video (YouTube)

1. **Upload video to YouTube** (recommended for storage)

2. **Embed on site**:
   - Edit Video Archives page
   - Add "Embed" block
   - Paste YouTube URL
   - Video embeds automatically

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Domain not working after 48 hours | Check nameservers in GoDaddy match Hostinger exactly |
| Devanagari shows boxes | Ensure Noto fonts CSS is added |
| SSL not working | Reinstall SSL in Hostinger, activate Really Simple SSL plugin |
| Slow site | Install caching plugin (WP Super Cache) |
| Can't upload large PDFs | Increase PHP upload limit in hPanel |

---

## Next Steps After Setup

1. ✅ Populate gurukulam directory with real data
2. ✅ Upload initial batch of PDF texts
3. ✅ Upload sample audio files
4. ✅ Embed sample videos
5. ✅ Write padhathi guide content
6. ✅ Add initial articles to blog
7. ✅ Test all user flows for 3 personas

---

## Support Resources

| Resource | URL |
|----------|-----|
| Hostinger Help Center | [support.hostinger.com](https://support.hostinger.com) |
| WordPress Documentation | [wordpress.org/support](https://wordpress.org/support/) |
| Astra Theme Docs | [wpastra.com/docs](https://wpastra.com/docs/) |

---

## Credentials Checklist

Keep these credentials safe:

```
✓ Hostinger hPanel Login: [email/password]
✓ WordPress Admin URL: https://jaimineeyasamavedam.org/wp-admin
✓ WordPress Username: [username]
✓ WordPress Password: [password]
✓ GoDaddy Login: [email/password]
✓ Google Account for Analytics: [email]
```

---

**Estimated Time to Complete**: 3-4 hours (excluding DNS propagation wait)

**Cost**: ~₹149/month (Hostinger Single Plan)
