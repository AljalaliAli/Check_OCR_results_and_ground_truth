import re
from datetime import datetime
import sqlite3
import os
import shutil
def extract_metadata_from_img_name(image_name):
    """
    Extracts the database name, timestamp, and parameter name from an image file name.
    
    The image file name should be in the format 'ID0008_MID0003_20240301_060433_par_name.ext'
    where 'ext' can be any file extension (e.g., tiff, jpg, png).

    Parameters:
    image_name (str): The image file name.

    Returns:
    tuple: A tuple containing the database name (str), timestamp (str), and parameter name (str).

    Raises:
    ValueError: If the image name format is incorrect.
    
    # Example usage
    image_name = 'ID0008_MID0003_20240301_060433_par_name.tiff'
    db_name, ts, par_name = extract_metadata_from_img_name(image_name)

    print(f"DB Name: {db_name}")
    print(f"Timestamp: {ts}")
    print(f"Parameter Name: {par_name}")

    """
    # Define the regex pattern for the image name format, allowing for different extensions
    pattern = r'^(ID\d+_MID\d+)_([0-9]{8})_([0-9]{6})_(\w+)\.\w+$'
    
    # Match the pattern with the image name
    match = re.match(pattern, image_name)
    if not match:
        raise ValueError("Image name format is incorrect")
    
    # Extract the components from the image name using groups
    db_name_prefix = match.group(1)  # Extracts 'ID0008_MID0003'
    date_str = match.group(2)        # Extracts '20240301'
    time_str = match.group(3)        # Extracts '060433'
    par_name = match.group(4)        # Extracts 'par_name'
    
    # Format the database name as 'ID0008_MID0003_MDE_2024.db'
    db_name = f"{db_name_prefix}_MDE_{date_str[:4]}.db"
    
    # Convert date and time strings to a datetime object
    dt = datetime.strptime(date_str + time_str, '%Y%m%d%H%M%S')
    
    # Format the datetime object to the required timestamp format 'YYYY-MM-DD HH:MM:SS'
    ts = dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return db_name, ts, par_name


def get_value_by_timestamp(db_name, table_name, timestamp, column_name):
    """
    Extracts a value from an SQLite database table where the timestamp matches the given value.
    
    Parameters:
    db_name (str): The name of the SQLite database file.
    table_name (str): The name of the table in the database.
    timestamp (str): The timestamp to match in 'YYYY-MM-DD HH:MM:SS' format.
    column_name (str): The name of the column to retrieve the value from.
    
    Returns:
    The value from the specified column where the timestamp matches, or None if no match is found.
    
    # Example usage
    db_name = r'D:\future link\AljalaliAli\DataGeneration\DataGeneration\db\ID0008_MID0003_MDE_2024.db'
    table_name = 'MDE'
    timestamp = '2024-02-21 06:32:53'
    column_name = 's'

    value = get_value_by_timestamp(db_name, table_name, timestamp, column_name)

    print(f"Value: {value}")

    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    try:
        # Define the SQL query
        query = f"SELECT {column_name} FROM {table_name} WHERE ts = '{timestamp}'"
        #print(query)
        # Execute the query with the given timestamp
        cursor.execute(query)
        
        # Fetch the result
        result = cursor.fetchone()
        
        # If a match is found, return the value; otherwise, return None
        return result[0] if result else None
    
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()



def move_image_tif(src_folder, dest_folder, image_name):
    """
    This function moves a specific image file from the source folder to the destination folder
    and changes the extension to '.tif'.

    Parameters:
    src_folder (str): The source folder path where the image is currently located.
    dest_folder (str): The destination folder path where the image will be moved.
    image_name (str): The name of the image file to be moved.

    Returns:
    None
    """
    # Check if source folder exists
    if not os.path.exists(src_folder):
        print(f"Source folder {src_folder} does not exist.")
        return

    # Check if destination folder exists, if not, create it
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    # Construct full file path
    src = os.path.join(src_folder, image_name)
    dest = os.path.join(dest_folder, os.path.splitext(image_name)[0] + '.tif')

    # Check if the file is an image
    if image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        # Check if the file exists in the source folder
        if os.path.exists(src):
            # Move the file and rename with new extension
            shutil.move(src, dest)
            print(f"The image file {image_name} has been moved and renamed to {os.path.basename(dest)} in {dest_folder}.")
        else:
            print(f"The image file {image_name} does not exist in the source folder {src_folder}.")
    else:
        print(f"The file {image_name} is not an image file or is not supported for conversion to .tif.")



def create_gt_text_file(img_dir, image_name, old_par_value, corrected_par_value, ground_truth_dir):
    if old_par_value ==  corrected_par_value:     
            move_image_tif(img_dir, 'Good_OCR', image_name)
    
    else:
        move_image_tif(img_dir, ground_truth_dir, image_name)
        # Ensure output directory exists, create if necessary
        os.makedirs(ground_truth_dir, exist_ok=True)

        # Split the image name to get the base name without extension
        base_name = os.path.splitext(os.path.basename(image_name))[0]

        # Create the output file name with .gt.txt extension
        output_file_name = os.path.join(ground_truth_dir, f"{base_name}.gt.txt")

        # Write the text to the output file
        with open(output_file_name, 'w') as file:
            file.write(corrected_par_value)

        print(f"Ground truth text file '{output_file_name}' created successfully.")
 


