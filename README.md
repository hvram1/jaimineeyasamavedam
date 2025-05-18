# jaimineeyasamavedam
Jaimini Sama Vedam 
This project converts the Sama Vedam text present in the pdf file S1.pdf into Unicode text. The document was created using a propreitary font called Krishna Vedic.  These are the steps done to convert the document

  Extract the embedded fonts from the Adobe PDF document using an online tool. These fonts are stored in the directory fonts. The majority of the texts are using the Krishna Vedic font
  
  Create a set of unique ascii characters present in the PDF file and print the characters using that font. 
  
  Use a tool like FontBook (in Mac) to find the corresponding Unicode values. 
  
  Create the mapping in the file char_map.py 
    
  Take care of certain idiosynchorancies (e.g.) some characters needs to be reversed . Some need a different ordering 
    
  The mapping is present in the file [output_text/mapping.html](output_text/mapping.html) 
  
  The generated text file is present in [output_text/output_grantha.txt](output_text/output_grantha.txt)
  
  This can be converted into other Unicode languages like Devanagari etc. using converters like [Aksharamuka]( https://www.aksharamukha.com/converter  ). 

# How to run the code 

Check out the repository. Create an environment and 
```
pip install PyPDF2
```

# Where to modify 

There would be mistakes in the character mapping . The file to modify is the char_map.py file. The mapping can be viewed in the file [output_text/mapping.html](mapping.html)

# How to generate 
```
python3 extract_pdf_text.py 
```

will generate the file [output_text/grantha_output.txt](output_text/grantha_output.txt)
