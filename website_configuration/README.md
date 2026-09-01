# Website Configuration & Backup Strategy

This directory contains configuration files and snippets for the `jaimineeyasamavedam.org` WordPress website.

## 1. Custom CSS
The file `additional_css.css` contains all the custom CSS overrides applied to the Astra theme.
*   **Location:** `Appearance > Customize > Additional CSS`

## 2. Backing up WordPress Configuration
Since the site is dynamic (WordPress), "source code" refers to the database and uploads content.

### A. Exporting Content (Posts, Pages, Media)
1.  Go to **Tools > Export** in the WP Dashboard.
2.  Select **All content**.
3.  Click **Download Export File**.
4.  Save the resulting XML file in this directory (e.g., `wordpress_export_DATE.xml`).

### B. Exporting Theme Settings (Astra)
1.  Install the **Astra Customizer Reset** or similar export plugin if available, OR:
2.  Use the **"Import / Export Customizer Settings"** plugin (if installed).
3.  Save the export file here.

### C. Plugin List
It is good practice to keep a list of active plugins.
*   Astra Theme (Version X.X)
*   (List other critical plugins here)
