import os
import json
import pickle

from skimage.io import imread
from skimage.transform import resize
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score


# Creates a jsonfile from directory.
# Used to make a file with categories from dataset
def make_json() -> None:
    def get_folder_names(directory):
        # Get a list of folder names in the specified directory
        folder_names = [folder for folder in os.listdir(directory) if os.path.isdir(os.path.join(directory, folder))]
        return folder_names

    def save_to_json(folder_names, output_file):
        # Save the folder names as JSON
        with open(output_file, 'w') as json_file:
            json.dump(folder_names, json_file, indent=4)

    directory_path = 'fruits-360_dataset/fruits-360/Test'
    output_file = 'folder_names.json'
    folder_names = get_folder_names(directory_path)
    save_to_json(folder_names, output_file)
    print(f'Folder names saved to {output_file}.')


def import_json_to_list(json_file) -> list:
    # Initialize an empty list to store the imported data
    data_list = []

    try:
        # Open the JSON file for reading
        with open(os.path.join(os.path.dirname(__file__) + "/" + json_file), 'r') as json_file:
            # Load the JSON data into the list
            data_list = json.load(json_file)
    except FileNotFoundError:
        print(f"The file '{json_file}' was not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from '{json_file}'.")

    return data_list


# Code to itereate through a dataset with training and testdata (images). Creates a model.p
# This can take a long time depending on the size of your dataset. 
def make_model(path, input_dir, sets, categories) -> None:

    # Prepare data
    path = os.path.dirname(__file__)
    input_dir = 'fruits-360_dataset/fruits-360/' # Folder that contains training and test data.
    sets = ['Training', 'Test'] # Foldernames for the two different sets.
    categories = [fruit for fruit in os.listdir(os.path.join(path, input_dir, sets[0])) if fruit[-9:] != ".DS_Store"]


    data = []
    labels = []

    # Load data and resize images. The larger the images the better the model.
    print("Loading data...")
    for fruit_set in sets:
        for category_idx, category in enumerate(categories):
            for file in os.listdir(os.path.join(path, input_dir, fruit_set, category)):
                img_path = os.path.join(path, input_dir, fruit_set, category, file)

                # print(img_path)

                img = imread(img_path)
                img = resize(img, (15, 15))
                data.append(img.flatten())
                labels.append(category_idx)


    # Setting up arrays and splitting before sending to SVC.
    print("Creating arrays...")
    data = np.asarray(data)
    labels = np.asarray(labels)
    print("Splitting data...")
    x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.33, shuffle=True, stratify=labels)


    
    # This point takes the longest.
    print("Training classifier...")
    classifier = SVC()

    parameters = [{'gamma': [0.01, 0.001, 0.0001], 'C': [1, 10, 100, 1000]}]

    grid_search = GridSearchCV(classifier, parameters)

    grid_search.fit(x_train, y_train)

    # Testing performance
    print("Testing performance...")
    best_estimator = grid_search.best_estimator_
    y_prediction = best_estimator.predict(x_test)
    score = accuracy_score(y_prediction, y_test)
    print('{}% of samples were correctly classified'.format(str(score * 100)))

    # Writing to file.
    print("Writing model...")
    pickle.dump(best_estimator, open('./model.p', 'wb'))
    print("Done!")

def search_pr_model(image) -> str:
    
    # Prepare data
    path = os.path.dirname(__file__)

    categories = import_json_to_list("static/pr_models/categories.json")

    MODEL = pickle.load(open(os.path.join(path, "static/pr_models/model.p"), "rb"))
    
    img_resized =  resize(image, (15, 15, 3))
    flat_data = []
    flat_data.append(img_resized.flatten())
    flat_data    = np.array(flat_data)

    y_output = MODEL.predict(flat_data)

    return categories[y_output[0]]