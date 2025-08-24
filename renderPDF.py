#from docx import Document
from pathlib import Path
import re


import sys
#from doc_utils import escape_for_latex
import jinja2
import subprocess
import tempfile
import os
import json
import urllib.parse
from requests.models import PreparedRequest
import grapheme

'''
Bug : Need to add the english prefix into the json tree
'''
def combine_ardhaksharas(text):
    """
    Combine ardhaksharas (half consonants) with following characters to form complete units.
    For example: ग् + ना -> ग्ना as a single unit
    """
    grapheme_list = list(grapheme.graphemes(text))
    combined_list = []
    i = 0
    
    while i < len(grapheme_list):
        current_grapheme = grapheme_list[i]
        
        # Check if current grapheme ends with halant (virama) - indicating an ardhakshara
        if current_grapheme.endswith('\u094D'):  # \u094D is the halant/virama character
            # Combine with next grapheme if it exists
            if i + 1 < len(grapheme_list):
                combined_grapheme = current_grapheme + grapheme_list[i + 1]
                combined_list.append(combined_grapheme)
                i += 2  # Skip the next grapheme as it's already combined
            else:
                combined_list.append(current_grapheme)
                i += 1
        else:
            combined_list.append(current_grapheme)
            i += 1
    
    return combined_list

def my_encodeURL(url,param1,value1,param2,value2):
    #x=urllib.parse.quote(URL)
    #print("URL is ",url, "param1 is ",param1,"value1 is ",value1,"param2 is ",param2,"value2 is ",value2)
    #x=urllib.parse.quote(url+"?"+param1+"="+value1+"&"+param2+"="+value2)
    req = PreparedRequest()
    params = {param1:value1,param2:value2}
    req.prepare_url(url, params)
    #print(req.url)
    return req.url

def my_format(my_number):
    my_int=int(my_number)
    my_string=f"{my_int:3d}"
    return my_string

def CreateCompilation():
    outputdir="outputs/md/Compilation"
    templateFileName_md="templates/PanchasatCompile_main.md"
    templateFileName_tex="templates/PanchasatCompile_main.tex"
    exit_code=0
    ts_string = Path("TS_withPadaGhanaJataiKrama.json").read_text(encoding="utf-8")
    parseTree = json.loads(ts_string)
    for kanda in parseTree['TS']['Kanda']:
        kandaInfo=kanda['id']
        for prasna in kanda['Prasna']:
            prasnaInfo=prasna['id']
            
            CreateMd(templateFileName_md,f"TS_{kandaInfo}_{prasnaInfo}","Compilation",prasna)
            '''
            result=CreatePdf(templateFileName_tex,f"TS_{kandaInfo}_{prasnaInfo}","Compilation",prasna)
            
            if result != 0:
                exit_code=1
                print("stopping the process since there is an error at",kandaInfo,prasnaInfo)
                return
            '''
                        






def CreatePdf (templateFileName,name,DocfamilyName,data):
    data=escape_for_latex(data)
    
    outputdir="output_text"
    logdir=f"{outputdir}/logs"
    exit_code=0
    
    TexFileName=f"{name}_{DocfamilyName}_Unicode.tex"
    PdfFileName=f"{name}_{DocfamilyName}_Unicode.pdf"
    TocFileName=f"{name}_{DocfamilyName}_Unicode.toc"
    LogFileName=f"{name}_{DocfamilyName}_Unicode.log"
    template = templateFileName
    outputdir = f"{outputdir}/pdf/{name}"
    Path(outputdir).mkdir(parents=True, exist_ok=True)
    Path(logdir).mkdir(parents=True, exist_ok=True)
    document = template.render(supersections=data)
    

    tmpdirname="."
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpfilename=f"{tmpdirname}/{TexFileName}"

        with open(tmpfilename,"w") as f:
            f.write(document)
        #result = subprocess.Popen(["latexmk","-lualatex", "--interaction=nonstopmode","--silent",tmpfilename],cwd=tmpdirname)
        #result.wait()
        src_pdf_file=Path(f"{tmpdirname}/{PdfFileName}")
        dst_pdf_file=Path(f"{outputdir}/{PdfFileName}")
        src_log_file=Path(f"{tmpdirname}/{LogFileName}")
        dst_log_file=Path(f"{logdir}/{LogFileName}")
        #src_toc_file=Path(f"{tmpdirname}/{TocFileName}")
        #dst_toc_file=Path(f"{outputdir}/{TocFileName}")
        src_tex_file=Path(f"{tmpdirname}/{TexFileName}")
        dst_tex_file=Path(f"{outputdir}/{TexFileName}")
        
        #if result.returncode != 0:
        #    print('Exit-code not 0  check Code!',src_tex_file)
        #    exit_code=1
        path = Path(src_tex_file)
        if path.is_file():
            src_tex_file.rename(dst_tex_file)  
        path = Path(src_pdf_file)
        if path.is_file():      
            src_pdf_file.rename(dst_pdf_file)
        path = Path(src_log_file)
        if path.is_file():
            src_log_file.rename(dst_log_file)
        #src_toc_file.rename(dst_toc_file)
    return exit_code


'''
if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            escaped_key = escape_for_latex(key) if isinstance(key, str) else key
            new_data[escaped_key] = escape_for_latex(value)
        return new_data
'''
def escape_for_latex(data):
    if isinstance(data, dict):
        new_data = {}
        for key in data.keys():
            new_data[key] = escape_for_latex(data[key])
        return new_data
    elif isinstance(data, list):
        return [escape_for_latex(item) for item in data]
    elif isinstance(data, str):
        # Adapted from https://stackoverflow.com/q/16259923
        latex_special_chars = {
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\^{}",
            "\\": r"\textbackslash{}",
            "\n": "\\newline%\n",
            "-": r"{-}",
            "\xA0": "~",  # Non-breaking space
            "[": r"{[}",
            "]": r"{]}",
        }
        return "".join([latex_special_chars.get(c, c) for c in data])

    return data
MAX_COLUMNS = 18

def replacecolon(data):
    if isinstance(data,str):
        data=data.replace(":","ः")
    return data
        
        
def format_mantra_sets(mantra_sets,section_title,subsection_title):
    global MAX_COLUMNS
    issue_url='https://github.com/hvram1/jaimineeyasamavedam/issues/new'
    unicode_pattern = re.compile(
    r'(?P<main_text>[\u0000-\u0027,\u0030-\u0FFF]+)(?P<open_paren>\(*)\s*(?P<inner_text>[\u0000-\u0027,\u0030-\u0FFF]+)\s*(?P<close_paren>\)*)',
    re.UNICODE
    )

    danda_pattern = re.compile(r'\s*[। ॥]\s*')
    number_pattern = re.compile(r'\s*([0-9]*)\s*')

    unicode_pattern_1 = re.compile(
    r'(?P<word_1>[\u0000-\u0027,\u0030-\u0FFF]+)\s*(?P<danda>[।॥])\s*(?P<open_paren>\()(?P<word_2>[\u0000-\u0027,\u0030-\u0FFF]+)(?P<close_paren>\))',
    re.UNICODE
    )
    errorFlag=False    

    column_spec_1 = "llllllllllllllllll"
    column_spec_2 = "colsep=0pt"
    #while len(column_spec) < MAX_COLUMNS:
    #    column_spec += "lll"
    #tblr_start_string = f"\\begin{{tblr}}{{colspec={column_spec},colsep=0pt}}" # Removed the colsep=0.5 pt
    #print(f" The start string is {tblr_start_string}")
    formatted_sets = []
    #formatted_sets.append(tblr_start_string)
    mantra_for_issues=""
    
    for mantra_set in mantra_sets:
        probable_error = mantra_set.get('probableError', False)
        mantra_words = mantra_set.get('mantra-words', [])
        swara = mantra_set.get('swara','')
        swara_list=swara.split()
        formatted_set = []
        
        mantra_for_issue=""
        if probable_error == True:
            errorFlag=True
        corrected_mantra = mantra_set.get('corrected-mantra',"")
        instance_value = mantra_set.get('instance',0)
        if len(corrected_mantra)>0:
            mantra = corrected_mantra
            errorFlag=False
        else :
            mantra=""
            for w,word in enumerate(mantra_words):
                actual_word = word.get('word', 'WORD')
                
                mantra+=" " +actual_word
          
        
        #This is what needs to be done
             
        #     For every word in mantra with () in them create a column with the last graphene before the ( and the characters within the ()
        #     Enclose the characters with the () to be in the smallredfont
        #     For these 2 columns set the colsep to 0pt ( column numbering starts from 1)
        #     For words with । and ॥ enclose these within \( \). Make this a column with right colsep since
        #     there is already a gap in the left 
             
        instance_pattern = r'॥\s*(\d+)\s*॥'     
         
        mantra=mantra.replace("।"," । ")
        mantra=mantra.replace("॥"," ॥ ")
        mantra=mantra.replace("{[}","X")
        mantra=mantra.replace(":","ः")
        
        if match_instance := re.search(instance_pattern,mantra):
            mantra = mantra.replace(match_instance.group(0),"")
        
        
        for match in re.finditer(unicode_pattern_1, mantra):
            word_1 = match.group("word_1")
            danda = match.group("danda")
            word_2 = match.group("word_2")
            #print(f" matched pattern word_1 is {word_1} word_2 is {word_2} danda is {danda}")
            mantra = mantra.replace(
            match.group(0),
            f" {word_1.strip()}({word_2.strip()}) {danda}"
            )
        mantra_for_issue = mantra
        result_mantra="" 
        for w,actual_word in enumerate(mantra.split()):
            #print(f" actual_word is {actual_word}")
            match_pattern = re.search(unicode_pattern, actual_word)
            if match_pattern:
                mydict=match_pattern.groupdict()
                open_paren=mydict.get("open_paren","")
                close_paren=mydict.get("close_paren","")
                if open_paren !="" and close_paren !="":
                    mantra_word=mydict.get("main_text")
                    swara_word=mydict.get("inner_text")
                else:
                    mantra_word=mydict.get("main_text","")+mydict.get("inner_text","")
                    swara_word=""
                
                if swara_word !="":
                    #mylist=list(grapheme.graphemes(mantra_word))
                    mylist=combine_ardhaksharas(mantra_word)
                    last_grapheme = mylist[-1]
                    other_graphemes = ''.join(mylist[0:-1])
                    
                    #print(f"Last grapheme of mantra_word: {last_grapheme}")
                    if other_graphemes !="":
                        res_text = f'{{{other_graphemes}}}&{{{last_grapheme}\\\\\\_smallredfont{{{swara_word}}}}}&'
                    else:
                        res_text = f'{{{last_grapheme}\\\\\\smallredfont{{{swara_word}}}}}&'
                else:
                    res_text = f'{{{mantra_word}}}&'
                #print(f" res_text 1 is {res_text}")
                result_mantra+=res_text
                
            elif (match_pattern := re.search(danda_pattern, actual_word)):
                    #print(f" matched danda {actual_word}")
                    res_text = f'{{\\({actual_word}\\)}}&'
                    #print(f" res_text 2 is {res_text}")
                    result_mantra+=res_text
            elif (match_pattern := re.search(number_pattern, actual_word)):
                
                    #print(f" matched danda {actual_word}")
                    res_text = f'{{{actual_word}}}&'
                    #print(f" res_text 3 is {res_text}")
                    result_mantra+=res_text
            else:
                    result_mantra="E R R O R . P L E A S E C H E C K"
                    break
            #print("Graphemes:", list(grapheme.graphemes(actual_word)))
        if result_mantra!="":
            zero_colsep=[]
            right_colsep=[]
            columns=result_mantra.split('&')
            for i,c in enumerate(columns):
                if '_' in c:
                    zero_colsep.append(str(i+1))
                if '।' in c or '॥' in c:
                    right_colsep.append(str(i+1))
            #print(f"{num_columns}{result_mantra}")
            result_mantra=result_mantra.replace('_small','small')
            #print(f"result_mantra is {result_mantra}")
            zcs_string=','.join(zero_colsep)
            rcs_string=','.join(right_colsep)
            tbl_start_string='\\begin{tblr}{colspec='+column_spec_1 #+','+column_spec_2
            if zcs_string !='':
                tbl_start_string+=',column{'+zcs_string+'}={leftsep=0pt,rightsep=6pt}'
            if rcs_string !='':
                tbl_start_string+=',column{'+rcs_string+'}={rightsep=3pt}'
            tbl_start_string+='}'
            #tbl_end_string='\\end{tblr}\\\\'
            tbl_end_string='\\end{tblr}'
            page_string=f'{tbl_start_string}{result_mantra}{tbl_end_string}\n'
            formatted_sets.append(page_string)
            #if instance_value != 0:
            #    instance_string='\n{instance_value}\n'
            #    formatted_sets.append(instance_string)
        mantra_for_issues+="\n"+"\n" +mantra_for_issue
    issue_body=(
                f' This is the current swara position . {mantra_for_issues}. \n\n'
                f'Please enter the new swara in the same format (i.e.) mantra(swara)mantramantra(swara) and log a correction'
            )
    issue_link=my_encodeURL(issue_url,"title","Issue in Swara section="+section_title + ",subsection=" + subsection_title,"body",issue_body)
    3#temp_string = " ".join(formatted_set)
    #ampersand_count = temp_string.count("&")
    #print(f" ampersand_count is {ampersand_count} MAX_COLUMNS is {MAX_COLUMNS} for {temp_string}")
    #while ampersand_count < MAX_COLUMNS -2:
    #    formatted_set.append("&")
    #    ampersand_count += 1
    latex_issue_link=escape_for_latex(issue_link)
    if errorFlag == False:
        col_value=f"\\textbf{{ \\href{{{latex_issue_link}}}{{ \\emoji {{lady-beetle}}}} }}"
    else:
        col_value=f"\\textbf{{ \\href{{{latex_issue_link}}}{{ \\emoji {{x}}}} }}"
    #formatted_set.append(col_value)
    #formatted_sets.append(" ".join(formatted_set) + " \\\\")
    #formatted_sets.append("\\end{tblr}\n \\\\ \n \\\\")
    formatted_sets.append("\n")
    formatted_sets.append(col_value)
    formatted_sets.append("\\newpage") # Use newpage instead of pagebreak
    #print(f" {subsection_title} {mantra_for_issues}")
    return "\n".join(formatted_sets)


#CreateGhanaFiles()

#CreateCompilation()

#CreateTxt()

#return exit_code

def main():
    # Example usage of the functions
    #ts_string = Path("TS_withPada.json").read_text(encoding="utf-8")
    #parseTree = json.loads(ts_string)

    ts_string_Grantha = Path("output_text/rewritten_final-Grantha.json").read_text(encoding="utf-8")
    data_Grantha = json.loads(ts_string_Grantha)

    template_dir="pdf_templates"
    
    templateFile_Grantha=f"{template_dir}/Grantha_main.template"
    templateFile_Devanagari=f"{template_dir}/Devanagari_main.template"
    templateFile_Tamil=f"{template_dir}/Tamil_main.template"
    templateFile_Malayalam=f"{template_dir}/Malayalam_main.template"
    



    outputdir="output_text"
    logdir="pdf_logs"
    latex_jinja_env = jinja2.Environment(
    block_start_string = r'\BLOCK{',
    block_end_string = '}',
    variable_start_string = r'\VAR{',
    variable_end_string = '}',
    comment_start_string = r'\#{',
    comment_end_string = '}',
    line_statement_prefix = '%-',
    line_comment_prefix = '%#',
    trim_blocks = True,
    lstrip_blocks=True,
    autoescape = False,
    loader = jinja2.FileSystemLoader(os.path.abspath('.')),
    extensions=['jinja2.ext.loopcontrols']
    )
    latex_jinja_env.filters["my_encodeURL"] = my_encodeURL
    latex_jinja_env.filters["escape_for_latex"] = escape_for_latex
    latex_jinja_env.filters["format_mantra_sets"] = format_mantra_sets
    latex_jinja_env.filters["replacecolon"] = replacecolon
    
    invocation=''
    title=''
    #print("running xelatex with ",samhitaTemplateFile)
    #template_file = latex_jinja_env.get_template(templateFile_Grantha)
   
    #supersections = data_Grantha.get('supersection', {})
    
    #CreatePdf(template_file,f"Grantha","Grantha",supersections)
    ts_string_Devanagari = Path("output_text/updated-final-Devanagari.json").read_text(encoding="utf-8")
    
    data_Devanagari = json.loads(ts_string_Devanagari)
    template_file = latex_jinja_env.get_template(templateFile_Devanagari)
    
    supersections = data_Devanagari.get('supersection', {})
    CreatePdf(template_file,f"Devanagari","Devanagari",supersections)
    
    #ts_string_Tamil = Path("output_text/final-Tamil.json").read_text(encoding="utf-8")
    
    #data_Tamil = json.loads(ts_string_Tamil)
    #template_file = latex_jinja_env.get_template(templateFile_Tamil)
    
    #supersections = data_Tamil.get('supersection', {})
    #CreatePdf(template_file,f"Tamil","Tamil",supersections)
    
    #ts_string_Malayalam = Path("output_text/final-Malayalam.json").read_text(encoding="utf-8")
    
    #data_Malayalam = json.loads(ts_string_Malayalam)
    #template_file = latex_jinja_env.get_template(templateFile_Malayalam)
    
    #supersections = data_Malayalam.get('supersection', {})
    #CreatePdf(template_file,f"Malayalam","Malayalam",supersections)


if __name__ == "__main__":
    main()