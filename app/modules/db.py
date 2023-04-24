def save_image(file_path, gfs):
    with open(file_path, "rb") as f:
        image_data = f.read()
        filename = file_path.split("/")[-1]
        gfs.insert_one({"img": image_data, "filename": filename, "content_type": "image/jpeg"})

    print(f"Image saved successfully: {filename}")


def get_image(image_name, output_path, gfs):
    gridfs_file = gfs.find_one({"filename": image_name})

    if gridfs_file is None:
        print(f"Image not found: {image_name}")
        return

    with open(output_path, "wb") as f:
        f.write(gridfs_file["img"])

    print(f"Image retrieved successfully: {output_path}")
