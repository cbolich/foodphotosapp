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

def save_image_mod(file_path, gfs):
    category = None
    tags = []
    angle = None
    zoom = None

    with open("info.csv") as i:
        info = i.readlines()[file_path]
        category = info.split(',')[7]
        angle = info.split(',')[4]
        zoom = info.split(',')[5]
        tags.append(info.split(',')[3])
        for field in info.split(',')[8].strip().split(','):
           tags.append(field)

    with open("/Users/jacob/Desktop/hundreds/"+str(file_path)+".jpeg", "rb") as f:
        image_data = f.read()
        filename = str(file_path) + ".jpeg"
        gfs.insert_one({"img": image_data, "filename": filename, "content_type": "image/jpeg", "category": category,
        "tags": tags, "angle": angle, "zoom": zoom})

    print(f"Image saved successfully: {filename}") 
