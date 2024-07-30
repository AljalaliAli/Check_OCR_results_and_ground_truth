# This module crops images using the images folder and the config files where the templates and configurations are stored.
# The output is cropped images where each image is cropped based on parameters specified in the config file.
# The name of the cropped image is the standard image name plus the parameter name.

import configparser
import sqlite3
from detect_pattern import *
from Image_functions import *

# Create a ConfigParser object
config = configparser.ConfigParser()
# Read the INI file
config.read('config.ini')

 





def read_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def get_parameters(file_path, image_id):
    json_data = read_json_file(file_path)
    parameters = json_data['images'][str(image_id)]['parameters']
    result = {}
    for key, value in parameters.items():
        result[value['name'].lower()] = value['position']
    return result


 
   

 

def main():
    print('crop_imges called!')
    # Retrieve variables from the INI file
    configFiles_dir = config.get('Paths', 'configFiles_dir')
    mde_config_file_name = config.get('Paths', 'mde_config_file_name')
    templates_dir_name = config.get('Paths', 'templates_dir_name')
    img_dir = config.get('Paths', 'img_dir')
    db_dir = config.get('Paths', 'db_dir')
    cropped_imgs_dir = config.get('Paths', 'cropped_imgs_dir')
    # Initialize the ImageMatcher
    matcher = ImageMatcher(configFiles_dir, mde_config_file_name, templates_dir_name)

    img_dir_empty=is_nested_directory_empty(img_dir)
    print(img_dir_empty)
    img_dir_has_images=does_nested_directory_have_images(img_dir)
    print(img_dir_has_images)
    images_list = get_image_files_in_directory(img_dir)
   
    for img_dir, img_name in images_list:
       ts=extract_ts_from_img_name(img_name)
      # Initialize the ImageMatcher
       matcher = ImageMatcher(configFiles_dir, mde_config_file_name, templates_dir_name)
      # Perform image matching
       match_values, temp_img_id = matcher.match_images(cv2.imread(os.path.join(img_dir, img_name)))

       

       # Process the matching results
       if int(temp_img_id) > 0:
            #print(f"Best template match found: {temp_img_id}")
      
            par_names_and_positions_dic =get_parameters(os.path.join(configFiles_dir, mde_config_file_name), temp_img_id)
            #print(par_names_and_positions_dic)
            ## loop throw the cropped images ..................... 
          #  print( "par_names_and_positions_dic: ", par_names_and_positions_dic )
            for par_name, par_pos in par_names_and_positions_dic.items():
                print(par_name)  
                img=cv2.imread(os.path.join(img_dir, img_name))
                cropped_image = crop_image(img, par_pos['x1'], par_pos['x2'], par_pos['y1'], par_pos['y2'])
                 
                # Extract the base img and extension
                base_name, ext = os.path.splitext(os.path.basename(img_name))
                # Create the new img_name with "par_name" added as a prefix
                cropped_image_name = f"{base_name}_{par_name}{ext}"
              #  print(f"cropped_image_name: {cropped_image_name}")
                save_image_cv(cropped_image,cropped_imgs_dir,cropped_image_name)
               # show_image(cropped_image)
     
     
       else:
             print("No matching template found.")   
             move_specific_image(img_dir, 'No_Match_imgs', img_name)
    
            

main()