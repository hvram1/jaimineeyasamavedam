import cv2
import numpy as np
import os
import glob
from extract_pdf_text import process_text
import re
import grapheme
def natural_sort_key(s):
        # Split string into list of strings and integers for natural sorting
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
def get_grantha_character_positions(word):
    # just returning the unicode characters does not work 
    return 

def get_char_position(word_img, box, word_position,word, num_chars,image_path):
    cx, cy, cw, ch = box
    
    if num_chars==1:
        return 1
    position=1
    gray_line = cv2.cvtColor(word_img, cv2.COLOR_BGR2GRAY)
    _, thresh_line = cv2.threshold(gray_line, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # Dilate to connect character components
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated_line = cv2.dilate(thresh_line, kernel, iterations=5)
    # Find contours (characters)
    contours, _ = cv2.findContours(dilated_line, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    char_boxes = [cv2.boundingRect(c) for c in contours]
    sorted_chars = sorted(char_boxes, key=lambda b: b[0])  # left-to-right
      
    for (x, y, w, h) in sorted_chars:
        cv2.rectangle(word_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        pass
    print(f" There are {len(sorted_chars)} characters in the word image at position {word_position} with box {box}")
    #cv2.imshow("Characters", word_img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    
    for i, (x, y, w, h) in enumerate(sorted_chars):
        if  ( x+w > cx and x+w < cx + cw) or (x >cx and x < cx + cw) :
            #print(f" Character {i} at position x={x}, y={y}, w={w}, h={h} intersects with the word box {box}")
            grapheme_list = list(grapheme.graphemes(word))
            chr_len = 0
            grapheme_position = 0
            for g_count,item in enumerate(grapheme_list):
                #print(f" Grapheme {g_count} {item} with length {len(item)}")
                chr_len += len(item)
                if chr_len >= i:
                    grapheme_position = g_count
                    break 
                    
            #cv2.rectangle(word_img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            #char_img = word_img[y:y+h, x:x+w]
            #dirname=os.path.dirname(image_path)
            #basename=os.path.basename(image_path).replace(".png","")
            #char_path = os.path.join(dirname, f"{basename}_word_{word_position:02d}.png")
            #print(f" Writing the file {char_path}")
            #cv2.imwrite(char_path, char_img)
            #cv2.imshow("Word Image", word_img)
            #cv2.waitKey(0)
            #cv2.destroyAllWindows()
            #position.append((word_position, i))
            #print(f" Character position {i} Grapheme position {grapheme_position} for word {word} with chr_len {chr_len} ")
            #return i
            return grapheme_position + 1  # Return 1-based index
            #break
    print(f" No intersecting character found for word image at position {sorted_chars} with box {box}")
    return position

def extract_words_from_image(image_path, output_dir, mantra_word_lengths=[], swara_word_lengths=[]):
    base_name = os.path.basename(image_path)
    directory_name = os.path.dirname(image_path)
    img_names=base_name.split('_')
    if len(img_names) < 3:
        print(f"Skipping {image_path} as it does not have 2 images.")
        return
    first_image=os.path.join(directory_name, "line_" + img_names[1].split('.')[0]+ ".png")
    second_image=os.path.join(directory_name, "line_" + img_names[2].split('.')[0]+ ".png")
    if not os.path.exists(first_image) or not os.path.exists(second_image):
        print(f"Skipping {image_path} as one of the line images {first_image} or {second_image} does not exist.")
        return
    
    img1 = cv2.imread(first_image)
    img2 = cv2.imread(second_image)
    # Resize to same width if needed
    if img1.shape[1] != img2.shape[1]:
        width = min(img1.shape[1], img2.shape[1])
        img1 = cv2.resize(img1, (width, img1.shape[0]))
        img2 = cv2.resize(img2, (width, img2.shape[0]))
        
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    dilated = cv2.dilate(thresh, kernel, iterations=10)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = [cv2.boundingRect(c) for c in contours]
    # Sort by y (top to bottom), then x (left to right)
    boxes = sorted(boxes, key=lambda b: (b[0], b[1]))
    #print(f"Found {len(boxes)} words in the image.{image_path}")

    # Find contours for words (external contours)
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    _, thresh1 = cv2.threshold(gray1, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    dilated1 = cv2.dilate(thresh1, kernel1, iterations=20)
    contours, _ = cv2.findContours(dilated1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes1 = [cv2.boundingRect(c) for c in contours]
    # Sort by y (top to bottom), then x (left to right)
    boxes1 = sorted(boxes1, key=lambda b: (b[0]))
    #print(f"Found {len(boxes1)} mantra words in the image.{first_image}")
    if (len(mantra_word_lengths) !=0 ):
        if len(boxes1) == len(mantra_word_lengths):
            pass
        else:
            print(f"Mantra word lengths differ: Text {len(mantra_word_lengths)} Image {len(boxes1)}")
            return []

    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    _, thresh2 = cv2.threshold(gray2, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    dilated2 = cv2.dilate(thresh2, kernel2, iterations=15)
    contours2, _ = cv2.findContours(dilated2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes2 = [cv2.boundingRect(c) for c in contours2]
    # Sort by y (top to bottom), then x (left to right)
    boxes2 = sorted(boxes2, key=lambda b: (b[0]))
    if (len(swara_word_lengths) !=0 ):
        if len(boxes2) == len(swara_word_lengths):
            pass
        else:
            print(f"Swara word lengths differ: Text {len(swara_word_lengths)} Image {len(boxes2)}")
            return[]
    #print(f"Found {len(boxes2)} swara words in the image.{second_image}")

    #print(f"Line 1 has {len(line1)} words and Line 2 has {len(line2)} words.")
    # For each word in line1, find the horizontally overlapping words in line2
    # newboxes is the boxes in line2 extending to line1
    newboxes = []
    for (x1,y1,w1,h1) in boxes2:
        newbox=[x1,y1,x1+w1,img.shape[0]]
        newboxes.append(newbox)
    #print(f"New boxes created: {newboxes} and boxes1 {boxes1}")
        
    line1_height = img1.shape[0]
    line1 = [b for b in boxes if b[1] < line1_height]

    #print(f"line1 boxes created are {line1}")
    intersecting_indices = []
    # Find intersecting indices: for each box in newboxes, find index of boxes1 that intersects horizontally
    for i, (x1, y1, x2, y2) in enumerate(newboxes):
        #cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        #cv2.imshow("Word Image",img)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        for j, (bx, by, bw, bh) in enumerate(boxes1):
            # Check if boxes overlap horizontally
            # Calculate horizontal overlap between newbox (x1, y1, x2, y2) and boxes1 (bx, by, bw, bh)
            overlap_start = max(x1, bx)
            overlap_end = min(x2, bx + bw)
            overlap_width = max(0, overlap_end - overlap_start)
            newbox_width = x2 - x1
            if newbox_width > 0 and (overlap_width / newbox_width) >= 0.5:
                # At least 50% of newbox overlaps horizontally with boxes1[j]
                #char_img = img[y1:y2, x1:x2]
                #dirname=os.path.dirname(image_path)
                #basename=os.path.basename(image_path).replace(".png","")
                #char_path = os.path.join(dirname, f"{basename}_word_{i:02d}_{j:02d}.png")
                #print(f" Writing the file {char_path}")
                #cv2.imwrite(char_path, char_img)
                if j >=len(mantra_word_lengths):
                    print(f" This seems to be an error case . Skipping")
                    continue
                word_position, word,num_chars = mantra_word_lengths[j]
                #print(f" Intersecting word at {word_position} contains {num_chars} characters based on grapheme counts")
                if num_chars == 1:
                    tup_le = (word_position, 1)
                    intersecting_indices.append(tup_le)
                else:
                    mask = np.zeros_like(gray)
                    mask[by:by+bh, bx:bx+bw] = 255
                    word_img = cv2.bitwise_and(img, img, mask=mask)
                    #cv2.rectangle(img, (bx, by), (bx+bw, by+bh), (255, 0, 0), 2)
                    #cv2.imshow("Word Image", word_img)
                    #cv2.waitKey(0)
                    #cv2.destroyAllWindows()
                    ## The original image is used to get the character position
                    pos = get_char_position(img1, (bx, by, bw, bh), word_position, word, num_chars,image_path)
                    tup_le = (word_position, pos)
                    intersecting_indices.append(tup_le)
                break  # Only take the first intersecting box for each newbox
    #print("Indices in boxes2 that intersect with newboxes:", intersecting_indices)

    
    image_dir = os.path.dirname(image_path)
    base_name = os.path.basename(image_path)
    #print(f"Directory of the image: {image_dir}")
    new_base_name = f"boxed_{base_name}"
    out_path = os.path.join(image_dir, new_base_name)
    cv2.imwrite(out_path, img)
    return intersecting_indices

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
        print(f"Image name is {base_name}")
        line_num = base_name.split('_')[1].split('.')[0]
        line_index=int(line_num)-1
        if line_index >= len(translated_lines):
            print(f" This is an error . So not processing")
            continue
        text_line=translated_lines[line_index]
        match1=re.search(header_pattern,text_line)
        match2=text_line.isnumeric()
        if text_line in pattern_to_ignore:
            print(f" Ignoring line {line_num} since these are generic and no swaras")
            continue
        elif match1:
            print(f" Ignoring line {line_num} since these are headers and no swaras ")
            continue
        if match2 == True:
            print(f" Matching page number {line_num} ")
            continue
        images_to_combine.append(line_image)
        #print(f" Line number is {line_num} Text is {translated_lines[line_index]}")
    print(f" Images to combine are {images_to_combine}")
    combine_images(image_path,output_dir,text_lines,images_to_combine)
    return 

def extract_lines_from_image(image_path, output_dir, text_lines,num_terations=10):
    # Read image
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold to get binary image
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Dilate to connect text lines
    #print(f" The structuring element size is {img.shape[1]//30} and 5")
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (img.shape[1]//30, 5))
    height_image,width_image = gray.shape
    dilated = cv2.dilate(thresh, kernel, iterations=num_iterations) #8 iterations works for some
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
        #print(f" bounding box at x={x} y={y} w={w} h={h} aspect_ratio={aspect_ratio} length={length}")


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
    output_base_dir = "output_text"
    #images_dir = f"{output_base_dir}/lines/*/"
    
    textfile="output_text/output-layout.txt"
    #textfile="output_text/output_grantha.txt"
    # Find all images matching the pattern page_xxx.png
    text_dict= read_text_file_to_dict(textfile)
    
    image_paths = sorted(
        #glob.glob(os.path.join(images_dir, "combined*.png")),
        glob.glob(os.path.join(images_dir, "page_*.png")),
        key=natural_sort_key
    )
    #image_paths=["images/page_155.png","images/page_211.png","images/page_422.png"]
    
    exclude_list = [
        "images/page_1.png",
        "images/page_62.png",#:10,# Not working
        "images/page_66.png",#:16,# Not working
        "images/page_73.png",#:10,#Not working
        "images/page_89.png",#:10 #Not working
        "images/page_144.png",#:9,  # Not working
        "images/page_148.png",#:3, # Not working
        "images/page_149.png",#:14, # Not working 
        "images/page_156.png",#:7, # Not working
        "images/page_227.png",#:6, #Not working
        "images/page_249.png",#:16, #Not workng
        "images/page_274.png",#:9, #Not working
        "images/page_381.png",#:9, #Not working
        "images/page_402.png",#:10 #not working
        
        
    ]
    combine_images_dict = {
        "images/page_62.png":[(2,3),(4,5),(8,9),(10,11),(12,13),(15,16),(17,18),(19,20),(22,23)],
        "images/page_66.png":[(3,4),(7,8),(9,10),(11,12),(13,14),(15,16),(17,18),(19,20),(21,22)],
        "images/page_73.png":[(4,5),(6,7),(8,9),(11,12),(13,14),(15,16),(19,20),(21,22)],
        "images/page_89.png":[(3,4),(5,6),(7,8),(11,12),(13,14),(15,16),(20,21)],
        "images/page_144.png":[(4,5),(6,7),(8,9),(10,11),(12,13),(14,15),(16,17),(18,19),(20,21),(23,24),(25,26)],
        "images/page_148.png":[(2,3),(5,6),(7,8),(9,10),(12,13),(14,15),(16,17),(18,19),(21,22),(23,24)],
        "images/page_149.png":[(2,3),(4,5),(7,8),(9,10),(11,12),(13,14),(15,16),(17,18),(20,21),(22,23)],
        "images/page_156.png":[(2,3),(5,6),(7,8),(9,10),(11,12),(13,14),(15,16),(17,18),(19,20),(21,22),(23,24)],
        "images/page_227.png":[(2,3),(6,7),(8,9),(10,11),(12,13),(14,15),(16,17),(18,19),(20,21),(22,23)],
        "images/page_249.png":[(2,3),(4,5),(7,8),(9,10),(11,12),(13,14),(15,16),(17,18),(19,20),(22,23),(24,25)],
        "images/page_274.png":[(2,3),(4,5),(6,7),(8,9),(10,11),(12,13),(14,15),(16,17),(20,21),(22,23),(24,25)],
        "images/page_381.png":[(2,3),(4,5),(6,7),(8,9),(11,12),(13,14),(15,16),(17,18),(19,20),(21,22)],
        "images/page_402.png":[(2,3),(4,5),(6,7),(8,9),(11,12),(13,14),(15,16),(18,19),(20,21),(22,23)]
    }
    page_hash_map_and_iterations={
"images/page_5.png":8,
"images/page_11.png":15,
"images/page_12.png":12,
"images/page_37.png":16,
"images/page_58.png":16, 
"images/page_75.png":2,  
"images/page_119.png":5,
"images/page_129.png":6, 
"images/page_142.png":9,
"images/page_145.png":9,
"images/page_150.png":8,
"images/page_154.png":9,
"images/page_155.png":9,
"images/page_157.png":9,
"images/page_163.png":4,
"images/page_173.png":8,
"images/page_176.png":8,
"images/page_180.png":2,
"images/page_185.png":2,
"images/page_186.png":8,
"images/page_187.png":7,
"images/page_188.png":8,
"images/page_211.png":7,
"images/page_220.png":8,
"images/page_225.png":12,
"images/page_240.png":15,
"images/page_264.png":12,
"images/page_375.png":8,
"images/page_413.png":9, 
"images/page_422.png":15,   
    }
    
    '''for i, image_path in enumerate(image_paths):
        print(f"Processing image {i}: {image_path}")
        extract_words_from_image(image_path, output_base_dir)
        if i>9:
            break
        '''
    
    for image_path in image_paths:
        # Extract page number from filename
        base_name = os.path.basename(image_path)
        print(f"Image name is {base_name}")
        page_num = base_name.split('_')[1].split('.')[0]
        output_dir = os.path.join(output_base_dir, "lines",f"page_{page_num}")
        if text_dict.get(page_num) is None:
            print(f"Skipping page {page_num} as it has no text in the layout file.")
            continue
        else:
            if image_path in exclude_list:
                continue
            num_iterations=page_hash_map_and_iterations.get(image_path,10) #make the default as 10
            
            print(f"Processing page {page_num} with number of text lines : {len(text_dict[page_num])}")
            #extract_lines_from_image(image_path, output_dir, text_dict[page_num],num_iterations)
            #break
    
    for key in combine_images_dict.keys():
        image_path = key
        list_of_tuples = combine_images_dict[key]
        for tup in list_of_tuples:
            first_image = f"line_{tup[0]:02d}.png"
            second_image = f"line_{tup[1]:02d}.png"
            output_dir=os.path.join(output_base_dir, "lines", f"page_{os.path.basename(image_path).split('_')[1].split('.')[0]}")
            first_image_path = os.path.join(output_base_dir, "lines", f"page_{os.path.basename(image_path).split('_')[1].split('.')[0]}", first_image)
            second_image_path = os.path.join(output_base_dir, "lines", f"page_{os.path.basename(image_path).split('_')[1].split('.')[0]}", second_image)
            if not os.path.exists(first_image_path) or not os.path.exists(second_image_path):
                print(f"Skipping {image_path} as one of the line images {first_image_path} or {second_image_path} does not exist.")
                continue
            #print(f"key is {key} output_dir {output_dir} first_image_path is {first_image_path} second {second_image_path}")
            combine_images("", output_dir, "", [first_image_path, second_image_path])
             
     
    