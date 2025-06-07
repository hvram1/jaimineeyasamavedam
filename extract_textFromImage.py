import cv2
import numpy as np
import os
import glob
from extract_pdf_text import process_text
import re

def draw_box_around_second_line_char(image_path):
    """
    Draws a box around the character in the second line that is vertically aligned with a character in the first line.
    """
    
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
     # Dilate to connect text lines
    #print(f" The structuring element size is {img.shape[1]//30} and 5")
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (img.shape[1], 5))
    height_image,width_image = gray.shape
    dilated = cv2.dilate(thresh, kernel, iterations=10)
    bounding_boxes=[]
    # Find contours (lines)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Find contours (characters)
    #contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    char_boxes = [cv2.boundingRect(c) for c in contours]
    # Sort by y (top to bottom), then x (left to right)
    char_boxes = sorted(char_boxes, key=lambda b: (b[1], b[0]))

    # Separate into two lines by y coordinate
    if len(char_boxes) < 2:
        print("Not enough characters found.")
        return

    # Find median y to split lines
    ys = [b[1] for b in char_boxes]
    median_y = np.median(ys)
    line1 = [b for b in char_boxes if b[1] < median_y]
    line2 = [b for b in char_boxes if b[1] >= median_y]

    # For each char in line2, check if its x center is within any char in line1
    for (x2, y2, w2, h2) in line2:
        center_x2 = x2 + w2 // 2
        for (x1, y1, w1, h1) in line1:
            if x1 <= center_x2 <= x1 + w1:
                # Draw rectangle around the char in line2
                cv2.rectangle(img, (x2, height_image), (x2 + w2, 0), (0, 0, 255), 2)
                
                break

    cv2.imwrite(image_path, img)
    
def combine_images(image_path,output_dir,text_lines,images_to_combine):
    i=0
    if len(images_to_combine)<2:
        return
    if len(images_to_combine)%2 !=0: # If there are odd images skip the first one . 
        images_to_combine=images_to_combine[1:]
    while (i< len(images_to_combine)):
        first_image=images_to_combine[i]
        second_image=images_to_combine[i+1]
        img1 = cv2.imread(first_image)
        img2 = cv2.imread(second_image)
        # Resize to same width if needed
        if img1.shape[1] != img2.shape[1]:
            width = min(img1.shape[1], img2.shape[1])
            img1 = cv2.resize(img1, (width, img1.shape[0]))
            img2 = cv2.resize(img2, (width, img2.shape[0]))
        combined = np.vstack((img1, img2))
        out_name = f"combined_{os.path.basename(first_image).split('_')[1].split('.')[0]}_{os.path.basename(second_image).split('_')[1].split('.')[0]}.png"
        out_path = os.path.join(output_dir, out_name)
        cv2.imwrite(out_path, combined)
        i+=2
    return

def process_line_images(image_path,output_dir,text_lines):
    header_pattern=r'^(\d+)'
    page_number_pattern=r'^\d+$'
    pattern_to_ignore=[ # These lines need not be merged 
        "𑌜𑍈𑌮𑌿𑌨𑍀𑌯  𑌸𑌾𑌮  𑌪𑍍𑌰𑌕𑍃𑌤𑌿  𑌗𑌾𑌨𑌮𑍍",
        "।।𑌆𑌗𑍍𑌨𑍇𑌯 𑌪𑌾𑌂:।।",
        "𑌹𑌰𑌿: ஓ𑌮𑍍",
        
    ]
    line_paths = sorted(glob.glob(os.path.join(output_dir, "line_*.png")))
    translated_lines=[]
    for line in text_lines:
        t_line=process_text(line)
        translated_lines.append(t_line)
        
    #print(f"Text lines {text_lines}")
    #print(f" Translated lines {translated_lines}")
    images_to_combine=[]
    for line_image in line_paths:
        base_name = os.path.basename(line_image)
        # print(f"Image name is {base_name}")
        line_num = base_name.split('_')[1].split('.')[0]
        line_index=int(line_num)-1
        text_line=translated_lines[line_index]
        match1=re.search(header_pattern,text_line)
        match2=text_line.isnumeric()
        if text_line in pattern_to_ignore:
            print(f" Ignoring line {line_num} since these are generic and no swaras")
            continue
        elif match1:
            print(f" Ignoring line {line_num} since these are headers and so swaras ")
            continue
        if match2 == True:
            print(f" Matching page number {line_num} ")
            continue
        images_to_combine.append(line_image)
        #print(f" Line number is {line_num} Text is {translated_lines[line_index]}")
    combine_images(image_path,output_dir,text_lines,images_to_combine)
    return 

def extract_lines_from_image(image_path, output_dir, text_lines):
    # Read image
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold to get binary image
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Dilate to connect text lines
    #print(f" The structuring element size is {img.shape[1]//30} and 5")
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (img.shape[1]//30, 5))
    height_image,width_image = gray.shape
    dilated = cv2.dilate(thresh, kernel, iterations=10)
    bounding_boxes=[]
    # Find contours (lines)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours top-to-bottom
    #bounding_boxes = [cv2.boundingRect(c) for c in contours]
    for contour in contours:
    # Calculate contour length
        length = cv2.arcLength(contour, closed=False)

    # Get bounding box
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h if h != 0 else float('inf')
        print(f" bounding box at x={x} y={y} w={w} h={h} aspect_ratio={aspect_ratio} length={length}")


    # Check if it's a line based on length and aspect ratio
        if length > 100 and (aspect_ratio > 5 or aspect_ratio < 0.2) and h > 100:  # Adjust threshold as needed
        #if h> 100:
        # Draw the contour (line)
            #cv2.drawContours(img, [contour], -1, (0, 0, 255), 2)
            l1=[x,y,w,h]
            #print(f"Line found at x={x}, y={y}, w={w}, h={h}")
            bounding_boxes.append(l1)
        
        #else :
            
            #print(f" Skipping a bounding box because the line is of height < 100 ")
        if h > 500:
            print(f" Possibly 2 lines are merged {h} ")

# Merge boxes with similar y coordinates (i.e., on the same line)
    if bounding_boxes:
        bounding_boxes = sorted(bounding_boxes, key=lambda b: b[1])  # sort by y
        merged_boxes = []
        current = bounding_boxes[0]
        for box in bounding_boxes[1:]:
            # If y is close (within 100 pixels), merge horizontally
            if abs(box[1] - current[1]) < 100:
                x1 = min(current[0], box[0])
                y1 = min(current[1], box[1])
                x2 = max(current[0] + current[2], box[0] + box[2])
                y2 = max(current[1] + current[3], box[1] + box[3])
                current = [x1, y1, x2 - x1, y2 - y1]
                #cv2.drawContours(img, [current], -1, (0, 0, 255), 2)
                #cv2.rectangle(img,(current[0],current[1]),(current[0]+current[2],current[1]+current[3]),color=(255, 255, 255))
            else:
                merged_boxes.append(current)
                current = box
        merged_boxes.append(current)
        sorted_boxes = sorted(merged_boxes, key=lambda b: b[1])
        
    else:
        sorted_boxes = []
    
    # Create output directory if not exists
    os.makedirs(output_dir, exist_ok=True)
    if len(sorted_boxes) == len(text_lines):
        #print(f"Number of lines in image {image_path} matches number of text lines: {len(sorted_boxes)}")
        pass
    else:
        print(f"Warning: Number of lines in image {image_path} ({len(sorted_boxes)}) does not match number of text lines ({len(text_lines)}).")
    # Extract and save each line
    for idx, (x, y, w, h) in enumerate(sorted_boxes, 1):
        print(f" line number {idx} at x={x} y={y} w={w} h={h}")
        x=0; w=width_image;
        line_img = img[y:y+h, x:x+w]
        out_path = os.path.join(output_dir, f"line_{idx:02d}.png")
        cv2.imwrite(out_path, line_img)
        cv2.rectangle(img, (x, y), (x + w, y + h), color=(0, 0, 255), thickness=2)
    out_path = os.path.join(output_dir, f"page_xx.png")
    cv2.imwrite(out_path, img)

def read_text_file_to_dict(file_path):
    """
    Reads a text file and returns a dictionary where the key is the page number (as string)
    and the value is a set of lines for that page.
    The text file contains lines of the pattern "XXX" where XXX is the page number.
    """
    page_dict = {}
    current_page = None
    pattern = r'__(\d+)__'
    with open(file_path, 'r', encoding='utf-8') as file:
        texts = file.read()
    for line in texts.splitlines():
        match = re.search(pattern, line)
        if match:
            current_page = match.group(1)
            if current_page not in page_dict:
                page_dict[current_page] = []
            continue
        elif current_page is not None and line.strip() :
            # If the line is not a page number, add it to the current page's set
            page_dict[current_page].append(line.strip())
        
        elif line.strip() == '':
            # Ignore empty lines
            continue
        
    return page_dict
if __name__ == "__main__":
    images_dir = "images"
    output_base_dir = "lines"
    textfile="output_text/output-layout.txt"
    # Find all images matching the pattern page_xxx.png
    text_dict= read_text_file_to_dict(textfile)
    image_paths = sorted(glob.glob(os.path.join(images_dir, "*.png")))
    exclude_list = [
        "images/page_1.png",
        "images/page_11.png",
        "images/page_119.png",
        "images/page_12.png",
        "images/page_129.png",
        "images/page_142.png",
        "images/page_144.png",
        "images/page_145.png",
        "images/page_148.png",
        "images/page_149.png",
        "images/page_150.png",
        "images/page_154.png",
        "images/page_155.png",
        "images/page_156.png",
        "images/page_157.png",
        "images/page_163.png",
        "images/page_173.png",
        "images/page_176.png",
        "images/page_180.png",
        "images/page_185.png",
        "images/page_186.png",
        "images/page_187.png",
        "images/page_188.png",
        "images/page_211.png",
        "images/page_219.png",
        "images/page_227.png",
        "images/page_240.png",
        "images/page_249.png",
        "images/page_274.png",
        "images/page_304.png",
        "images/page_339.png",
        "images/page_355.png",
        "images/page_37.png",
        "images/page_375.png",
        "images/page_378.png",
        "images/page_385.png",
        "images/page_413.png",
        "images/page_422.png",
        "images/page_428.png",
        "images/page_43.png",
        "images/page_45.png",
        "images/page_58.png",
        "images/page_66.png",
        "images/page_89.png",
    ]

    '''for image_path in image_paths:
        # Extract page number from filename
        base_name = os.path.basename(image_path)
        # print(f"Image name is {base_name}")
        page_num = base_name.split('_')[1].split('.')[0]
        output_dir = os.path.join(output_base_dir, f"page_{page_num}")
        if text_dict.get(page_num) is None:
            print(f"Skipping page {page_num} as it has no text in the layout file.")
            continue
        else:
            print(f"Processing page {page_num} with number of text lines : {len(text_dict[page_num])}")
            extract_lines_from_image(image_path, output_dir, text_dict[page_num])
         ''' 
    ''' 
    for image_path in image_paths:
        if image_path in exclude_list:
            print(f" Found {image_path} in exclude list")
            pass
        else:
            base_name = os.path.basename(image_path)
            # print(f"Image name is {base_name}")
            page_num = base_name.split('_')[1].split('.')[0]
            output_dir = os.path.join(output_base_dir, f"page_{page_num}")
            if text_dict.get(page_num) is None:
                print(f"Skipping page {page_num} as it has no text in the layout file.")
                continue
            else:
                print(f"Processing page {page_num} with number of text lines : {len(text_dict[page_num])}")
                process_line_images(image_path, output_dir, text_dict[page_num])
                
    '''
    test_combined_image=["lines/page_2/combined_09_10.png"]
    draw_box_around_second_line_char(test_combined_image[0])            
    '''# Split each extracted line into individual characters
    chars_base_dir = "chars"
    for image_path in image_paths:
        page_num = os.path.basename(image_path).split('_')[1].split('.')[0]
        lines_dir = os.path.join(output_base_dir, f"page_{page_num}")
        line_images = sorted(glob.glob(os.path.join(lines_dir, "line_*.png")))
        for line_idx, line_img_path in enumerate(line_images, 1):
            line_img = cv2.imread(line_img_path)
            gray_line = cv2.cvtColor(line_img, cv2.COLOR_BGR2GRAY)
            _, thresh_line = cv2.threshold(gray_line, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            # Dilate to connect character components
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            dilated_line = cv2.dilate(thresh_line, kernel, iterations=5)
            # Find contours (characters)
            contours, _ = cv2.findContours(dilated_line, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            char_boxes = [cv2.boundingRect(c) for c in contours]
            sorted_chars = sorted(char_boxes, key=lambda b: b[0])  # left-to-right
            chars_dir = os.path.join(chars_base_dir, f"page_{page_num}", f"line_{line_idx:02d}")
            os.makedirs(chars_dir, exist_ok=True)
            for char_idx, (x, y, w, h) in enumerate(sorted_chars, 1):
                char_img = line_img[y:y+h, x:x+w]
                char_path = os.path.join(chars_dir, f"char_{char_idx:02d}.png")
                cv2.imwrite(char_path, char_img)
                '''
