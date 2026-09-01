import json
import sys
import re
import grapheme
import urllib.parse
from requests.models import PreparedRequest
url_protocol = 'file://'
url_protocol ='' # Use this for local file system access, or set to '' for web URLs
issue_url='https://github.com/hvram1/jaimineeyasamavedam/issues/new'
def my_encodeURL(url,param1,value1,param2,value2):
    #x=urllib.parse.quote(URL)
    #print("URL is ",url, "param1 is ",param1,"value1 is ",value1,"param2 is ",param2,"value2 is ",value2)
    #x=urllib.parse.quote(url+"?"+param1+"="+value1+"&"+param2+"="+value2)
    req = PreparedRequest()
    params = {param1:value1,param2:value2}
    req.prepare_url(url, params)
    #print(req.url)
    return req.url

if len(sys.argv) < 2:
    print("Usage: python render-finaljson.py <input_json_file>")
    sys.exit(1)

input_json_file = sys.argv[1]
with open(input_json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)
    
html = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>𑌜𑍈𑌮𑌿𑌨𑍀𑌯  𑌸𑌾𑌮  𑌪𑍍𑌰𑌕𑍃𑌤𑌿  𑌗𑌾𑌨𑌮𑍍</title>
    <style>
        body { font-family: FONT-TO-BE-USED; margin: 20px; }
        
        .supersection, .section, .subsection { margin: 8px 0; }
        .supersection-title, .section-title {
            cursor: pointer;
            background: #e0e0e0;
            padding: 8px;
            border-radius: 4px;
            margin-bottom: 4px;
            font-weight: bold;
            display: inline-block;
            font-family: FONT-TO-BE-USED;
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

if input_json_file.endswith('final-Grantha.json'):
    html = html.replace('FONT-TO-BE-USED', '"Noto Sans Grantha", sans-serif')
    filename='output_text/pages-Grantha/render-finaljson.html'
elif input_json_file.endswith('final-Devanagari.json'):
    html = html.replace('FONT-TO-BE-USED', '"Noto Sans Devanagari", sans-serif')
    filename='output_text/pages-Devanagari/render-finaljson.html'
elif input_json_file.endswith('final-Tamil.json'):
    html = html.replace('FONT-TO-BE-USED', '"Noto Sans Tamil", sans-serif')
    filename='output_text/pages-Tamil/render-finaljson.html'
elif input_json_file.endswith('final-Malayalam.json'):
    html = html.replace('FONT-TO-BE-USED', '"Noto Sans Malayalam", sans-serif')
    filename='output_text/pages-Malayalam/render-finaljson.html'
with open(filename, 'w', encoding='utf-8') as f:
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
    table.mantra-table-error {
        border-collapse: collapse;
        margin: 0;
        padding: 0;
        border: 5px solid red;
    }
    table.mantra-table tr, table.mantra-table td, table.mantra-table-error tr, table.mantra-table-error td {
        margin: 0;
        padding: 0 2px;
        border: none;
        font-size: 1.2em;
        vertical-align: bottom;
        white-space: pre;
    }
    
    .swara-cell {
        font-family: FONT-TO-BE-USED;
        color: #00796b;
        font-size: 0.9em;
        text-align: center;
    }
    .mantra-cell {
        font-family: FONT-TO-BE-USED;
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

            f'<img src="{url_protocol}../{header_image}" alt="Header Mantra Image" style="max-width:100%; border:1px solid #ccc;">'
            f'</div>'
            f'<h2 onclick="toggleImageVisibility(\'img-preview-{k}\')" style="cursor:pointer;">{header_number} {header}</h2>'
            )
            for l, mantra_set in enumerate(mantra_sets):
                img_src=mantra_set.get('image-ref', '')
                errorFlag=mantra_set.get('probableError', '')
                page_html +=(
                f'<div onclick="toggleImageVisibility(\'img-preview-{k}-{l}\')" id="img-preview-{k}-{l}" style="display:none; margin-bottom:8px; cursor:pointer;">'

                f'<img src="{url_protocol}../{img_src}" alt="Mantra Image" style="max-width:100%; border:1px solid #ccc;">'
                f'</div>'
                
                )
                table_class_name="mantra-table"
                if errorFlag == True:
                    table_class_name="mantra-table-error"
                
                page_html +=(
                f'<table class="{table_class_name}">'
                f'<tr onclick="toggleImageVisibility(\'img-preview-{k}-{l}\')" style="cursor:pointer;">'
                )
                mantra_words=mantra_set.get("mantra-words", "")
                count_instance=mantra_set.get("instance", 0)
                number_of_columns = len(mantra_words)
                issue_title=f'Issue in Swara for section {i+1}-{j+1}-{k+1}-{l+1}'
                #for mantra_word in mantra_words:
                #    page_html += f'<td class="mantra-cell">{mantra_word.get("word", "")}</td>'
                #f'</tr>'
                swara_list = mantra_set.get("swara", "").split()
                #page_html += f'<tr>'
                m=0
                # This regex pattern matches a string with an optional prefix, a parenthesis group, and a suffix:
                # ([^\(]*)   : Group 1 - matches any characters except '(' (the prefix before the first '(')
                # (\()       : Group 2 - matches the literal '('
                # ([^\)]*)   : Group 3 - matches any characters except ')' (the content inside the parentheses)
                # (\))       : Group 4 - matches the literal ')'
                # (.*)       : Group 5 - matches any remaining characters after the closing ')' (the suffix)
                pattern1 = r'([^\(]*)(\()([^\)]*)(\))(.*)'
                
                swara_line="<tr>"
                mantra_line=""
                mantra_for_issue=""
                for mantra_word in mantra_words:
                    
                    match1=re.search(pattern1, mantra_word.get("word", ""))
                    #print(f"Match is {match1} {match2} for {mantra_word.get("word")}")
                    mantra_for_issue+=mantra_word.get("word", "")
                    if match1:
                        match_group_len=len(match1.groups())
                        mantra_word_prefix=match1.group(1)
                        empty_space_len=grapheme.length(mantra_word_prefix)
                        empty_spaces='&nbsp;' * (empty_space_len)
                        
                        swara_word=match1.group(3)
                        mantra_word_suffix=match1.group(5)
                        mantra_line += f'<td class="mantra-cell">{mantra_word_prefix}{mantra_word_suffix}</td>'
                        swara_line += f'<td class="swara-cell">{empty_spaces}{swara_word}</td>'
                    else:
                        mantra_line += f'<td class="mantra-cell">{mantra_word.get("word", "")}</td>'
                        swara_line += f'<td class="swara-cell"></td>'
                        
                if (count_instance !=0):
                    mantra_line += f'<td></td><td>{count_instance}</td>'
                    
                
                page_html +=mantra_line
                issue_body=(
                    f' This is the current swara position . {mantra_for_issue}. \n\n'
                    f'Please enter the new swara in the same format (i.e.) mantra(swara)mantramantra(swara) and log a correction'
                )
                issue_link=my_encodeURL(issue_url,"title",issue_title,"body",issue_body)
                swara_line += f'<td><a href="{issue_link}" target="_blank">Raise a correction</a></td>'
                swara_line+=f'</tr>'
                page_html +=swara_line
                page_html += f'</tr></table>'
            page_html+= '''
            </body>
            </html>
            ''' 
            if input_json_file.endswith('final-Grantha.json'):
                page_html = page_html.replace('FONT-TO-BE-USED', '"Noto Sans Grantha", sans-serif')
                #filename='output_text/pages-grantha/render-finaljson.html'
                file_name = f"output_text/pages-Grantha/subsection-{i+1:01d}-{j+1:02d}-{k+1:03d}.html"
            elif input_json_file.endswith('final-Devanagari.json'):
                page_html = page_html.replace('FONT-TO-BE-USED', '"Noto Sans Devanagari", sans-serif')
                file_name = f"output_text/pages-Devanagari/subsection-{i+1:01d}-{j+1:02d}-{k+1:03d}.html"
            elif input_json_file.endswith('final-Tamil.json'):
                page_html = page_html.replace('FONT-TO-BE-USED', '"Noto Sans Tamil", sans-serif')
                file_name = f"output_text/pages-Tamil/subsection-{i+1:01d}-{j+1:02d}-{k+1:03d}.html"
            elif input_json_file.endswith('final-Malayalam.json'):
                page_html = page_html.replace('FONT-TO-BE-USED', '"Noto Sans Malayalam", sans-serif')
                file_name = f"output_text/pages-Malayalam/subsection-{i+1:01d}-{j+1:02d}-{k+1:03d}.html"
            else:
                file_name = f"output_text/pages/subsection-{i+1:01d}-{j+1:02d}-{k+1:03d}.html"

            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(page_html)

