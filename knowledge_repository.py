import os
import torch
from transformers import CLIPProcessor, CLIPModel
from utils import get_image_from_base64, get_image_as_base64

class KnowledgeRepository:
    def __init__(self):
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def get_clip_embedding(self, image):
        if isinstance(image, str):
            image = get_image_from_base64(image)
        inputs = self.processor(images=image, return_tensors="pt")
        outputs = self.model.get_image_features(**inputs)
        return outputs

    def find_closest_images(self, base_image, example_images, top_k=10):
        base_image_embedding = self.get_clip_embedding(base_image)
        similarities = []
        for example_image_base64 in example_images:
            try:
                example_image_base64_string = get_image_as_base64(f"examples/{example_image_base64}")
                example_image = get_image_from_base64(example_image_base64_string)
                example_image_embedding = self.get_clip_embedding(example_image)
                similarity = torch.cosine_similarity(base_image_embedding, example_image_embedding).item()
                similarities.append((similarity, example_image_base64))
            except ValueError as e:
                print(f"Error processing example image: {e}")
                continue

        similarities.sort(reverse=True, key=lambda x: x[0])
        return [base64_image for _, base64_image in similarities[:top_k]]

    def get_example_prompt(self, filename):
        text_filename = filename.replace(".png", ".txt")
        try:
            with open(f"examples/{text_filename}", "r") as file:
                return file.read()
        except Exception as e:
            raise ValueError(f"Error reading example prompt file: {e}")

    def get_relevant_examples(self, base64_image):
        example_files = sorted([f for f in os.listdir("examples") if f.endswith(".png")])
        closest_examples = self.find_closest_images(base64_image, example_files)

        closest_examples_data = []
        for example_file in closest_examples:
            try:
                closest_examples_data.append({
                    "filename": example_file,
                    "base64_image": get_image_as_base64(f'examples/{example_file}'),
                    "example_prompt": self.get_example_prompt(example_file)
                })
            except ValueError as e:
                print(f"Error processing example file '{example_file}': {e}")
                continue

        return closest_examples_data
