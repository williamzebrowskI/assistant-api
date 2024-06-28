import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from managers.google.nlp.data.intents import intent_data
import numpy as np
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Neural network model definition for intent classification
class IntentClassifierModel(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(IntentClassifierModel, self).__init__()
        # Define a fully connected layer with input_dim inputs and 128 outputs
        self.fc1 = nn.Linear(input_dim, 128)
        # Define a ReLU activation function
        self.relu1 = nn.ReLU()
        # Define a fully connected layer with 128 inputs and 64 outputs
        self.fc2 = nn.Linear(128, 64)
        # Define a ReLU activation function
        self.relu2 = nn.ReLU()
        # Define a fully connected layer with 64 inputs and output_dim outputs
        self.fc3 = nn.Linear(64, output_dim)

    # Define the forward pass of the model
    def forward(self, x):
        # Pass input through the first layer and activation function
        out = self.fc1(x)
        out = self.relu1(out)
        # Pass output through the second layer and activation function
        out = self.fc2(out)
        out = self.relu2(out)
        # Pass output through the third layer
        out = self.fc3(out)
        return out

def train_and_save_model(intent_data, model_path):
    try:
        # Prepare data
        vectorizer = TfidfVectorizer()  # Initialize TF-IDF vectorizer
        texts = []  # List to store the training texts
        labels = []  # List to store the corresponding labels
        # Iterate over intent data to fill texts and labels
        for intent, phrases in intent_data.items():
            for phrase in phrases:
                texts.append(phrase)
                labels.append(intent)
        
        # Transform texts to TF-IDF features
        X_tfidf = vectorizer.fit_transform(texts).toarray()
        # Create a mapping from labels to indices
        label_to_index = {label: idx for idx, label in enumerate(intent_data.keys())}
        # Convert labels to corresponding indices
        y = np.array([label_to_index[label] for label in labels])
        input_dim = X_tfidf.shape[1]  # Number of input features
        output_dim = len(label_to_index)  # Number of output classes
        
        # Initialize the model
        model = IntentClassifierModel(input_dim, output_dim)
        criterion = nn.CrossEntropyLoss()  # Loss function for classification
        optimizer = optim.Adam(model.parameters(), lr=0.001)  # Adam optimizer with learning rate 0.001
        
        # Convert data to PyTorch tensors
        X_tensor = torch.tensor(X_tfidf, dtype=torch.float32)
        y_tensor = torch.tensor(y, dtype=torch.long)
        
        # Train the model
        num_epochs = 190  # Number of training epochs
        for epoch in range(num_epochs):
            model.train()  # Set the model to training mode
            optimizer.zero_grad()  # Zero the gradients
            outputs = model(X_tensor)  # Forward pass
            loss = criterion(outputs, y_tensor)  # Compute the loss
            loss.backward()  # Backward pass (compute gradients)
            optimizer.step()  # Update the weights
            
            # Calculate training accuracy
            _, predicted_train = torch.max(outputs.data, 1)  # Get the index of the max log-probability
            train_accuracy = accuracy_score(y_tensor, predicted_train)  # Calculate accuracy
            
            # Print the loss and accuracy every 10 epochs
            if (epoch + 1) % 10 == 0:
                logging.info(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}, Training Accuracy: {train_accuracy:.4f}')
        
        logging.info('Training completed')
        # Save the state dictionary of the model
        torch.save(model.state_dict(), model_path)
        logging.info(f'Model state dictionary saved to {model_path}')
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    SAVE_MODEL_PATH = os.getenv('SAVE_MODEL_PATH')
    train_and_save_model(intent_data, SAVE_MODEL_PATH)