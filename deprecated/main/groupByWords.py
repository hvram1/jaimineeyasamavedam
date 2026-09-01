import cv2
import numpy as np
import os
import glob

import re
import grapheme
import json

def extract_words_from_image(image_path):
    NEARNESS_THRESHOLD=85 # 90 does not work . 
    base_name = os.path.basename(image_path)
    parent_directory = os.path.basename(os.path.dirname(image_path))
    parent_directory_names = parent_directory.split('_')
    relative_path = os.path.dirname(os.path.dirname(image_path))
    page_number=int(parent_directory_names[1]) 
    directory_name = os.path.dirname(image_path)
    img_names=base_name.split('_')
    if len(img_names) <3:
        print(f" This is a mantra only line and no positions")
        return False
    first_image=os.path.join(directory_name, "line_" + img_names[1].split('.')[0]+ ".png")
    first_prefix=int(img_names[1])
    second_prefix=int(img_names[2].split('.')[0])
    if second_prefix < first_prefix:
        page_number=page_number+1
        second_image = os.path.join(relative_path, f"page_{page_number}","line_" + img_names[2].split('.')[0]+ ".png")
    else:
    
    
        second_image=os.path.join(directory_name, "line_" + img_names[2].split('.')[0]+ ".png")
    if not os.path.exists(first_image) or not os.path.exists(second_image) or not os.path.exists(image_path):
        print(f"Skipping {image_path} as one of the line images {first_image} or {second_image} does not exist or the {image_path} does not exist")
        return True

    image_full = cv2.imread(image_path)
    image_mantra = cv2.imread(first_image)
    image_swara = cv2.imread(second_image)
    width = min(image_mantra.shape[1], image_swara.shape[1])
    # Resize to same width if needed
    if image_mantra.shape[1] != image_swara.shape[1]:
        #width = min(img1.shape[1], img2.shape[1])
        image_mantra = cv2.resize(image_mantra, (width, image_mantra.shape[0]))
        image_swara = cv2.resize(image_swara, (width, image_swara.shape[0]))

    # Group characters into words and draw rectangles around each word
    gray = cv2.cvtColor(image_mantra, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Combine bounding boxes of nearby contours to form words
    bounding_boxes = [cv2.boundingRect(contour) for contour in contours]
    bounding_boxes.sort(key=lambda box: box[0])  # Sort by x-coordinate

    combined_mantra_boxes = []
    for b,box in enumerate(bounding_boxes):
        x, y, w, h = box
        if not combined_mantra_boxes:
            combined_mantra_boxes.append(box)
        else:
            prev_x, prev_y, prev_w, prev_h = combined_mantra_boxes[-1]
            #print(f" box {b} x,{x} y,{y} w,{w} h,{h} ")
            #print(f" prev-box {b-1} x,{prev_x} y,{prev_y} w,{prev_w} h,{prev_h} ")
            # Check if the current box is under the previous box vertically and overlapping horizontally
            #if prev_y <= y <= prev_y + prev_h and x <= prev_x + prev_w and x + w >= prev_x:
            #box 3 x,1137 y,172 w,44 h,45 
            #prev-box 2 x,891 y,20 w,245 h,361
            if (x <= prev_x and x + w > prev_x + prev_w) or (x >= prev_x and x + w <= prev_x + prev_w):
                #print(f" {b} and {b-1} have a vertical alignment")
                # Merge the boxes
                new_x = min(prev_x, x)
                new_y = min(prev_y, y)
                new_w = max(prev_x + prev_w, x + w) - new_x
                new_h = max(prev_y + prev_h, y + h) - new_y
                combined_mantra_boxes[-1] = (new_x, new_y, new_w, new_h)
            # If no vertical overlap, check horizontal closeness
            elif x <= prev_x + prev_w + NEARNESS_THRESHOLD :#and abs(y - prev_y) <= NEARNESS_THRESHOLD:
                #print(f" {b} and {b-1} have a horizontal alignment")
                # Merge the boxes
                new_x = min(prev_x, x)
                new_y = min(prev_y, y)
                new_w = max(prev_x + prev_w, x + w) - new_x
                new_h = max(prev_y + prev_h, y + h) - new_y
                combined_mantra_boxes[-1] = (new_x, new_y, new_w, new_h)
            else:
                #print(f" {b} and {b-1} do not have a horizontal alignment or vertical alignment")
                combined_mantra_boxes.append(box)

    # Draw rectangles around each word with alternating colors (red and green)
    for i, (x, y, w, h) in enumerate(combined_mantra_boxes):
        color = (0, 0, 255) if i % 2 == 0 else (0, 255, 0)  # Red for even, Green for odd
        cv2.rectangle(image_mantra, (x, y), (x + w, y + h), color, 2)
        
    #print(f"{image_path} has {len(bounding_boxes)} characters and {len(combined_mantra_boxes)} words")
    # Save or display the image with rectangles
    

    # Create a dictionary mapping combined_box index to bounding box indices
    mantra_word_to_char_mapping = {}
    for combined_index, combined_box in enumerate(combined_mantra_boxes):
        combined_x, combined_y, combined_w, combined_h = combined_box
        mantra_word_to_char_mapping[combined_index] = []
        for bounding_index, bounding_box in enumerate(bounding_boxes):
            x, y, w, h = bounding_box
            # Check if the bounding box is inside the combined box
            if combined_x <= x and combined_y <= y and combined_x + combined_w >= x + w and combined_y + combined_h >= y + h:
                mantra_word_to_char_mapping[combined_index].append(bounding_index)

    #print("Mantra Combined box mapping:", mantra_word_to_char_mapping)
    
    # Process image_swara similarly to image_mantra
    gray_swara = cv2.cvtColor(image_swara, cv2.COLOR_BGR2GRAY)
    _, binary_swara = cv2.threshold(gray_swara, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours for swara
    contours_swara, _ = cv2.findContours(binary_swara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Combine bounding boxes of nearby contours to form words for swara
    bounding_boxes_swara = [cv2.boundingRect(contour) for contour in contours_swara]
    bounding_boxes_swara.sort(key=lambda box: box[0])  # Sort by x-coordinate

    combined_swara_boxes = []
    for b, box in enumerate(bounding_boxes_swara):
        x, y, w, h = box
        if not combined_swara_boxes:
            if h< 20:
                print(f"{image_path} has a ghost swara can be ignored -0 Swara 0 ")
            else:
                combined_swara_boxes.append(box)
        else:
            prev_x, prev_y, prev_w, prev_h = combined_swara_boxes[-1]
            if (x <= prev_x and x + w > prev_x + prev_w) or (x >= prev_x and x + w <= prev_x + prev_w):
                new_x = min(prev_x, x)
                new_y = min(prev_y, y)
                new_w = max(prev_x + prev_w, x + w) - new_x
                new_h = max(prev_y + prev_h, y + h) - new_y
                if new_h < 20:
                    print(f"{image_path} has a ghost swara can be ignored -1 Swara {len(combined_swara_boxes)}")
                else:
                    combined_swara_boxes[-1] = (new_x, new_y, new_w, new_h)
            elif x <= prev_x + prev_w + NEARNESS_THRESHOLD and abs(y - prev_y) <= NEARNESS_THRESHOLD:
                new_x = min(prev_x, x)
                new_y = min(prev_y, y)
                new_w = max(prev_x + prev_w, x + w) - new_x
                new_h = max(prev_y + prev_h, y + h) - new_y
                if new_h < 20:
                    print(f"{image_path} has a ghost swara can be ignored -2 Swara {len(combined_swara_boxes)}")
                else:
                    combined_swara_boxes[-1] = (new_x, new_y, new_w, new_h)
            else:
                if h <20:
                    print(f"{image_path} has a ghost swara can be ignored -3 Swara {len(combined_swara_boxes)} ")
                else:
                    combined_swara_boxes.append(box)

    # Draw rectangles around each word with alternating colors (red and green)
    for i, (x, y, w, h) in enumerate(combined_swara_boxes):
        color = (0, 0, 255) if i % 2 == 0 else (0, 255, 0)  # Red for even, Green for odd  
        cv2.rectangle(image_swara, (x, y), (x + w, y + h), color, 2)
        
    
    #print(f"{image_path} has {len(bounding_boxes_swara)} swara characters and {len(combined_swara_boxes)} swara words")

    # Create a dictionary mapping combined_box index to bounding box indices for swara
    swara_word_to_char_mapping = {}
    for combined_index, combined_box in enumerate(combined_swara_boxes):
        combined_x, combined_y, combined_w, combined_h = combined_box
        swara_word_to_char_mapping[combined_index] = []
        for bounding_index, bounding_box in enumerate(bounding_boxes_swara):
            x, y, w, h = bounding_box
            if combined_x <= x and combined_y <= y and combined_x + combined_w >= x + w and combined_y + combined_h >= y + h:
                swara_word_to_char_mapping[combined_index].append(bounding_index)

    #print("Swara combined box mapping:", swara_word_to_char_mapping)
    
    # Find intersecting mantra boxes for each swara box
    swara_mantra_intersections = {}
    for swara_index, swara_box in enumerate(combined_swara_boxes):
        swara_x, swara_y, swara_w, swara_h = swara_box
        intersecting_mantra_indices = []
        tuple_lists=[]
        for mantra_index, mantra_box in enumerate(combined_mantra_boxes):
            mantra_x, mantra_y, mantra_w, mantra_h = mantra_box
            # Check if the swara box intersects with the mantra box
            if not (swara_x + swara_w < mantra_x or swara_x > mantra_x + mantra_w or
                    swara_y + swara_h < mantra_y or swara_y > mantra_y + mantra_h):
                intersecting_mantra_indices.append(mantra_index)
                if len(mantra_word_to_char_mapping[mantra_index]) > 3:
                    #print(f"Mantra box {mantra_index} contains more than 3 characters. Intersecting character positions:")
                    #print(mantra_word_to_char_mapping[mantra_index])
                    intersecting_characters = []
                    starting_char=0
                    if len(mantra_word_to_char_mapping[mantra_index])>1:
                        starting_char=mantra_word_to_char_mapping[mantra_index][0]
                    for char_index in mantra_word_to_char_mapping[mantra_index]:
                        char_box = bounding_boxes[char_index]
                        char_x, char_y, char_w, char_h = char_box
                        # Check if the character box intersects with the swara box
                        if not (swara_x + swara_w < char_x or swara_x > char_x + char_w or
                                swara_y + swara_h < char_y or swara_y > char_y + char_h):
                            intersecting_characters.append(char_index-starting_char)
                    #print(f"Swara box {swara_index} intersects with characters: {intersecting_characters}")
                else:
                    intersecting_characters = []
                if len(intersecting_characters) > 0:
                    intersect_tuple= (mantra_index, {"intersecting_characters": intersecting_characters})
                else:
                    intersect_tuple=(mantra_index)
                tuple_lists.append(intersect_tuple)

        #print(f"Swara box {swara_index} intersects with mantra boxes: {intersecting_mantra_indices}")

        key=f'swara-{swara_index}'
        swara_mantra_intersections[key] = tuple_lists

    return_hash={}
    return_hash["swara_mantra_intersections"] = swara_mantra_intersections
    swara_word_char_hash={}
    for i,item in enumerate(combined_swara_boxes):
        key=f'swara-{i}'
        swara_word_char_hash[key]=item
    mantra_word_char_hash={}
    for j,item in enumerate(combined_mantra_boxes):
        key=f'mantra-{j}'
        mantra_word_char_hash[key]=item
    return_hash["swara_word_char_mapping"]=swara_word_char_hash
    return_hash["mantra_word_char_mapping"]=mantra_word_char_hash
    return_hash["image_name"]=image_path
    # Save the image_swara with bounding boxes
    # Combine image_mantra and image_swara into image_full
    image_full = np.vstack((image_mantra, image_swara))
    swara_output_path = os.path.join(directory_name, f"boxed_swara_{base_name}")
    cv2.imwrite(swara_output_path, image_full)
    #cv2.imshow("Mantra", image_mantra)
    # Position the windows so they don't overlap
    #cv2.imshow("Swara", image_swara)
    #cv2.moveWindow("Mantra", 0, 0)  # Move Mantra window to top-left corner
    #cv2.moveWindow("Swara", 0, image_mantra.shape[0] + 1)  # Move Swara window just below the Mantra window
    

    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    return return_hash
def reg_test():
    test_images = [
        #"output_text/lines/page_4/combined_14_15.png",
        #"output_text/lines/page_5/combined_03_04.png",
        #"output_text/lines/page_5/combined_05_06.png",
        #"output_text/lines/page_5/combined_10_11.png", # Is an error 
        "output_text/lines/page_243/combined_03_04.png",
        "output_text/lines/page_243/combined_05_06.png",
        "output_text/lines/page_243/combined_07_08.png",
        "output_text/lines/page_243/combined_09_10.png",
        "output_text/lines/page_243/combined_11_12.png",
        "output_text/lines/page_243/combined_13_14.png",
        "output_text/lines/page_243/combined_15_16.png",
        "output_text/lines/page_243/combined_17_18.png",
        "output_text/lines/page_243/combined_19_20.png",
        "output_text/lines/page_243/combined_21_22.png",
    ]
    for image_path in test_images:
        test_specific_image(image_path)
    
def test_specific_image(image_path):
    if not os.path.exists(image_path):
        print(f"Image {image_path} does not exist.")
        return
    result = extract_words_from_image(image_path)
    print(f"Result for {image_path}:")
    print(json.dumps(result, indent=4, ensure_ascii=False))
def main():
    # Find all files under output_text/lines/* that start with the pattern combined_*.png
    # Only include files under page_243 to page_307
    base_path = "output_text/lines"
    pattern = os.path.join(base_path, "*", "combined_*.png")
    combined_files = glob.glob(pattern)
    #combined_files = []
    #for page_num in range(241, 329):
    #    page_dir = os.path.join(base_path, f"page_{page_num}")
    #    pattern = os.path.join(page_dir, "combined_*.png")
    #    combined_files.extend(glob.glob(pattern))

    # Sort files by page_nn numerically and then by xx
    def extract_page_and_combined(file_path):
        match = re.search(r"page_(\d+)/combined_(\d+)_", file_path)
        if match:
            page_num = int(match.group(1))
            combined_xx = int(match.group(2))
            return page_num, combined_xx
        return float('inf'), float('inf')  # Default for unmatched files

    combined_files.sort(key=extract_page_and_combined)
    hash_of_hash={}
    print(f"Found {len(combined_files)} files:")
    for file in combined_files:
        my_rerun_hash=extract_words_from_image(file)
        hash_of_hash[file]=my_rerun_hash
    output_file = "output_text/image-properties.json"
    with open(output_file, "w") as json_file:
        json.dump(hash_of_hash, json_file, indent=4)
    print(f"Data written to {output_file}")
if __name__ == "__main__":
    main()
    #reg_test()
    