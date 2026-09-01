# JSV Website - Quick Reference Guide

## 🔗 Essential Links

| Resource | URL |
|----------|-----|
| **Website** | https://jaimineeyasamavedam.org |
| **WordPress Admin** | https://jaimineeyasamavedam.org/wp-admin |
| **Hostinger hPanel** | https://hpanel.hostinger.com |
| **GoDaddy** | https://godaddy.com |
| **Google Analytics** | https://analytics.google.com |

---

## 🎨 Design System

### Color Palette
### Color Palette
```css
Background (Eggshell): #F9F4E8
Cards (Antique White): #EFE6D5
Text (Charcoal): #2C2C2C
Accent (Saffron): #FF6B35  /* Headings, Links, Active States */
Gold (Earthy): #C08535     /* Borders, Tints */
```

### Typography
- **Devanagari**: Noto Sans Devanagari
- **Grantha**: Noto Sans Grantha  
- **Malayalam**: Noto Sans Malayalam
- **English**: Astra default (Inter/System fonts)

---

## 🔌 Plugin List (Release 1)

### Essential Plugins
- ✅ Really Simple SSL (Security)
- ✅ Site Kit by Google (Analytics)
- ✅ UpdraftPlus (Backup)
- ✅ Contact Form 7 (Forms)

### Feature Plugins
- ✅ Download Monitor (PDF tracking)
- ✅ HTML5 Audio Player (Audio)
- ✅ WP Google Maps (Map)
- ✅ TablePress (Tables)

---

## 📄 Page Structure

```
Home (/)
├── Sacred Texts (/texts/)
│   └── Padhathi Guide (/padhathis/)
├── Audio Archives (/audio/)
├── Video Archives (/video/)
├── Learn Sama Veda
│   ├── Getting Started (/learn/)
│   ├── Find Gurukulam (/find-gurukulam/)
│   └── FAQ (/faq/)
├── Community
│   ├── Articles (/articles/)
│   ├── Newsletter (/newsletter/) [Placeholder]
│   └── Agraharams (/agraharams/)
└── Contact (/contact/)
```

---

## 🎯 Indic Font CSS

Quick copy-paste for Additional CSS:

```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600&family=Noto+Sans+Grantha&family=Noto+Sans+Malayalam:wght@400;600&display=swap');

.devanagari, .sanskrit {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 1.2em;
  line-height: 1.8;
}

.grantha {
  font-family: 'Noto Sans Grantha', serif;
  font-size: 1.2em;
  line-height: 1.8;
}

.malayalam {
  font-family: 'Noto Sans Malayalam', sans-serif;
  font-size: 1.2em;
  line-height: 1.8;
}
```

---

## 🛠️ Common WordPress Tasks

### Add New Text PDF
1. Media → Add New → Upload PDF
2. Posts → Add New
3. Category: "Sacred Texts"
4. Add download button using Download Monitor

### Add Audio File
1. Media → Add New → Upload MP3
2. Edit Audio Archives page
3. Add Audio block → Select file

### Add Video (YouTube)
1. Upload to YouTube first
2. Edit Video Archives page
3. Add Embed block → Paste URL

### Create New Article
1. Posts → Add New
2. Categories: Articles
3. Add Featured Image
4. Publish

---

## 📊 Analytics Setup

### Google Analytics Events to Track
- PDF Downloads
- Audio Plays
- Video Views
- Contact Form Submissions
- Persona Navigation Patterns

---

## 🔐 Security Checklist

- [ ] SSL Enabled (https://)
- [ ] Strong admin password
- [ ] Regular backups via UpdraftPlus
- [ ] Keep WordPress updated
- [ ] Keep plugins updated
- [ ] Limit login attempts (consider plugin)

---

## 📱 SEO Quick Checklist

For each new page/post:
- [ ] Set SEO title (max 60 chars)
- [ ] Write meta description (max 160 chars)
- [ ] Add focus keyword
- [ ] Use header hierarchy (H1 → H2 → H3)
- [ ] Add alt text to images
- [ ] Internal linking

---

## 🌍 GoDaddy DNS Settings

**Nameservers** (if needed to reference):
```
ns1.dns-parking.com
ns2.dns-parking.com
```

---

## 🚀 Launch Checklist

### Pre-Launch
- [ ] All pages created
- [ ] Navigation menu configured
- [ ] SSL working (padlock visible)
- [ ] At least 3 PDFs uploaded
- [ ] 2-3 audio files uploaded
- [ ] Contact form tested
- [ ] Mobile responsive tested
- [ ] Analytics tracking verified

### Content to Prepare
- [ ] Gurukulam directory data (min 3-5 centers)
- [ ] Initial batch of PDFs (min 5 texts)
- [ ] Sample audio chants (min 3-5)
- [ ] YouTube videos URLs (min 3)
- [ ] 2-3 articles for blog
- [ ] Padhathi guide content

---

## 📞 Support Contacts

| Issue | Contact |
|-------|---------|
| Hostinger Support | Live chat in hPanel |
| WordPress Issues | [wordpress.org/support](https://wordpress.org/support/) |
| Plugin Problems | Check individual plugin support forums |

---

## 💰 Monthly Costs

| Item | Cost |
|------|------|
| Hostinger Hosting | ₹149/month |
| Domain Renewal (annual) | Already paid at GoDaddy |
| **Total** | **₹149/month** |

---

## 📅 Maintenance Schedule

| Task | Frequency |
|------|-----------|
| WordPress updates | Weekly check |
| Plugin updates | Weekly check |
| Backup check | Weekly |
| Content addition | As available |
| Analytics review | Monthly |
| Security audit | Quarterly |

---

## 🎓 Three Personas - Quick Reminder

| Persona | Pages They Use | Priority Content |
|---------|---------------|------------------|
| 📚 Student/Teacher | Texts, Padhathis, Download | PDFs, comparisons |
| 🔍 Seeker | Learn, Find Gurukulam, FAQ | Getting started, map |
| 👥 Community | Articles, Newsletter, Events | Fresh content, updates |
