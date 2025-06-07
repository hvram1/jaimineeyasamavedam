import json
url_protocol = 'file://'
url_protocol ='' # Use this for local file system access, or set to '' for web URLs
with open('output_text/final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

html = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>𑌜𑍈𑌮𑌿𑌨𑍀𑌯  𑌸𑌾𑌮  𑌪𑍍𑌰𑌕𑍃𑌤𑌿  𑌗𑌾𑌨𑌮𑍍</title>
    <style>
        body { font-family: "Noto Sans Grantha", sans-serif; margin: 20px; }
        
        .supersection, .section, .subsection { margin: 8px 0; }
        .supersection-title, .section-title {
            cursor: pointer;
            background: #e0e0e0;
            padding: 8px;
            border-radius: 4px;
            margin-bottom: 4px;
            font-weight: bold;
            display: inline-block;
            font-family: "Noto Sans Grantha", sans-serif;
        }
        .section-content, .subsection-content {
            display: none;
            margin-left: 24px;
        }
        .subsection-title {
            margin-left: 16px;
            padding: 4px 0;
        }
        .iframe-container {
            flex: 1 1 50%;
            min-width: 400px;
            margin-left: 24px;
        }
        .iframe-container iframe {
            width: 100%;
            height:1600px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        .table-class {
            border-collapse: collapse;
            width: 100%;
        }
        .table-row {
            border-bottom: 1px solid #ccc;
        }
        .table-cell-1 {
            padding: 8px;
            vertical-align: top;
            width:30%;
            height: 1600px;
        }
        .table-cell-2 {
            padding: 8px;
            vertical-align: top;
            width:70%;
            height: 1600px;
        }
    </style>

    <script>
        function toggle(id) {
            var el = document.getElementById(id);
            if (el.style.display === "block") {
                el.style.display = "none";
            } else {
                el.style.display = "block";
            }
        }
        function showInIframe(url, event) {
            if (event) event.stopPropagation();
            document.getElementById('content-iframe').src = url;
            return false;
        }
    </script>
    
    
</head>
<body>
    <h1>𑌜𑍈𑌮𑌿𑌨𑍀𑌯  𑌸𑌾𑌮  𑌪𑍍𑌰𑌕𑍃𑌤𑌿  𑌗𑌾𑌨𑌮𑍍</h1>
    <p> Click on the titles to expand or collapse sections. Click on subsection titles to load content.</p>
    <p> Click on the mantra to see the actual images of the mantras. This can be used for proof reading.</p>
    <p> The swara positions are shown below the mantra words. The swara positions are not correct. This is work in process and will be fixed.</p>
    <div><table class="table-class"><tr class="table-row"><td class="table-cell-1">
'''
supersections = data.get('supersection', {})
for i, supersection in enumerate(supersections):
    #print(f"Supersection {i}: {supersections[supersection].get('supersection_title', 'Untitled')}")
    super_id = f"super_{i}"
    html += f'<div class="supersection">'
    html += f'<div class="supersection-title" onclick="toggle(\'{super_id}\')">{supersections[supersection].get("supersection_title", "Untitled Supersection")}</div>'
    html += f'<div class="section-content" id="{super_id}">'
    for j, section in enumerate(supersections[supersection].get('sections', [])):
        sections = supersections[supersection].get('sections', [])
        sec_id = f"{super_id}_sec_{j+1}"
        count = sections[section].get('count', 0).get('current_count')
        html += f'<div class="section">'
        html += f'<div class="section-title" onclick="toggle(\'{sec_id}\')">Section {j+1} (Count: {count})'
        html += f'<div class="subsection-content" id="{sec_id}">'
        for k, subsection in enumerate(sections[section].get('subsections', [])):
            content_id = f"{sec_id}_sub_{k+1}"
            subsections = sections[section].get('subsections', [])
            header = subsections[subsection].get('header', {}).get('header', 'Untitled Header')
            header_number = subsections[subsection].get('header', {}).get('header_number', 0)
            mantra_sets = subsections[subsection].get('mantra_sets', [])
            instance_count = sum(1 for ms in mantra_sets if 'instance' in ms)
            #print(f" header {header}")
            #url="https://www.sringeri.net/gallery/downloadables/panchangam"
            url = f"{url_protocol}subsection-{i+1:01d}-{j+1:02d}-{k+1:03d}.html"
            html+= f'<div class="subsection">'
            html += (
                f'<div class="subsection-title" id="{content_id}" '
                f'onclick="showInIframe(\'{url}\', event)">{header_number} {header} (Count: {instance_count})</div>'
            )
            #html += f'<div class="subsection-title" id="{content_id}" onclick="toggle(\'{content_id}\')">{header_number} {header} (Count: {instance_count})</div>'
            #html += f'<div class="subsection-content" id="{content_id}">HTML link</div>'
            html += f'</div>'
        html += '</div></div></div>'
    html += '</div></div>'

html += '''
        </div>
        </td><td class="table-cell-2">
        <div class="iframe-container">
            <iframe id="content-iframe" src=""></iframe>
        </div>
        </td></tr></table>
    </div>
</body>
</html>
'''

with open('output_text/pages/render-finaljson.html', 'w', encoding='utf-8') as f:
    f.write(html)
    
page_html_init = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Final JSON Render</title>
    <style>
    table.mantra-table {
        border-collapse: collapse;
        margin: 0;
        padding: 0;
    }
    table.mantra-table tr, table.mantra-table td {
        margin: 0;
        padding: 0 2px;
        border: none;
        font-size: 1.2em;
        vertical-align: bottom;
        white-space: pre;
    }
    .swara-cell {
        font-family: 'Noto Sans Devanagari', sans-serif;
        color: #00796b;
        font-size: 0.9em;
        text-align: center;
    }
    .mantra-cell {
        font-family: 'Noto Sans Devanagari', sans-serif;
        text-align: center;
    }
</style>
<script>
function toggleImageVisibility(imgDivId) {
    const imgDiv = document.getElementById(imgDivId);
    if (imgDiv.style.display === "none" || imgDiv.style.display === "") {
        imgDiv.style.display = "block";
    } else {
        imgDiv.style.display = "none";
    }
}
</script>
</head>
<body>
    <h1>Final JSON Render</h1>
'''
supersections = data.get('supersection', {})
for i, supersection in enumerate(supersections):
    for j, section in enumerate(supersections[supersection].get('sections', [])):
        sections = supersections[supersection].get('sections', [])
        for k, subsection in enumerate(sections[section].get('subsections', [])):
            subsections = sections[section].get('subsections', [])
            page_html=page_html_init
            header = subsections[subsection].get('header', {}).get('header', 'Untitled Header')
            header_number = subsections[subsection].get('header', {}).get('header_number', 0)
            header_image = subsections[subsection].get('header', {}).get('image-ref', '')
            mantra_sets = subsections[subsection].get('mantra_sets', [])
            page_html = page_html.replace("Final JSON Render", header)
            instance_count = sum(1 for ms in mantra_sets if 'instance' in ms)
            page_html +=(
            f'<div id="img-preview-{k}" style="display:none; margin-bottom:8px;">'

            f'<img src="{url_protocol}../{header_image}" onclick="toggleImageVisibility(\'img-preview-{k}\')" alt="Header Mantra Image" style="max-width:100%; border:1px solid #ccc;">'
            f'</div>'
            f'<h2 onclick="toggleImageVisibility(\'img-preview-{k}\')" style="cursor:pointer;">{header_number} {header}</h2>'
            )
            for l, mantra_set in enumerate(mantra_sets):
                img_src=mantra_set.get('image-ref', '')
                page_html +=(
                f'<div id="img-preview-{k}-{l}" style="display:none; margin-bottom:8px;">'

                f'<img src="{url_protocol}../{img_src}" onclick="toggleImageVisibility(\'img-preview-{k}-{l}\')" alt="Mantra Image" style="max-width:100%; border:1px solid #ccc;">'
                f'</div>'
                
                )
                page_html +=(
                f'<table class="mantra-table">'
                f'<tr onclick="toggleImageVisibility(\'img-preview-{k}-{l}\')" style="cursor:pointer;">'
                )
                mantra_words=mantra_set.get("mantra-words", "")
                number_of_columns = len(mantra_words)
                for mantra_word in mantra_words:
                    page_html += f'<td class="mantra-cell">{mantra_word.get("word", "")}</td>'
                f'</tr>'
                swara_list = mantra_set.get("swara", []).split()
                page_html += f'<tr>'
                m=0
                while m < number_of_columns:

                    if m < len(swara_list):
                        page_html += f'<td class="swara-cell">{swara_list[m]}</td>'
                    else:
                        page_html += f'<td class="swara-cell"></td>'
                    m += 1

                page_html += f'</tr></table>'
            page_html+= '''
            </body>
            </html>
            ''' 
            file_name = f"output_text/pages/subsection-{i+1:01d}-{j+1:02d}-{k+1:03d}.html"

            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(page_html)

