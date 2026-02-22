import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import json
import os

from torch.utils.data import Dataset, DataLoader, random_split
from model import DotaDraftPredictor

class DotaDataset(Dataset):
    def __init__(self, radiant_data, dire_data, labels_data):
        self.radiant = radiant_data
        self.dire = dire_data
        self.labels = labels_data
        
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        return self.radiant[idx], self.dire[idx], self.labels[idx]

print("Laddar json-data...")

with open('../data_pipeline/raw_data/pro_picks.json', 'r', encoding='utf-8') as file:
    matches = json.load(file)

NUM_HEROES = 156
all_radiant, all_dire, all_labels = [], [], []

for match in matches:
    radiant_picks = torch.zeros(NUM_HEROES)
    dire_picks = torch.zeros(NUM_HEROES)
    
    for player in match['players']:
        hero_id = player['heroId']
        if player['isRadiant']:
            radiant_picks[hero_id] = 1
        else:
            dire_picks[hero_id] = 1
            
    all_radiant.append(radiant_picks)
    all_dire.append(dire_picks)
    all_labels.append(1.0 if match['didRadiantWin'] else 0.0)

X_radiant = torch.stack(all_radiant)
X_dire = torch.stack(all_dire)
y_labels = torch.tensor(all_labels).view(-1, 1)

dataset = DotaDataset(X_radiant, X_dire, y_labels)

total_matches = len(dataset)
train_size = int(0.8 * total_matches) 
test_size = total_matches - train_size 

train_dataset, test_dataset = random_split(dataset, [train_size, test_size])

train_dataloader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_dataloader = DataLoader(test_dataset, batch_size=32, shuffle=False)

print(f"Tränar på {train_size} matcher, sparar {test_size} matcher för det 'riktiga provet'.")

model = DotaDraftPredictor(num_heroes=NUM_HEROES)

criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001) 
EPOCHS = 20 

print(f"Börjar träna på {len(dataset)} matcher i {EPOCHS} epoker...\n")

for epoch in range(EPOCHS):
    model.train() 
    running_loss = 0.0
    
    for batch_radiant, batch_dire, batch_labels in train_dataloader:
       
        optimizer.zero_grad()
        
        
        predictions = model(batch_radiant, batch_dire)
        
       
        loss = criterion(predictions, batch_labels)
        
       
        loss.backward()
        
        
        optimizer.step()
        
        running_loss += loss.item()
        
    
    avg_loss = running_loss / len(train_dataloader)
    print(f"Epok [{epoch+1}/{EPOCHS}] | Snitt-Loss: {avg_loss:.4f}")

model.eval() 
correct_guesses = 0
total_guesses = 0

print("\nKör test på osedd data...")
with torch.no_grad(): 
    for batch_radiant, batch_dire, batch_labels in test_dataloader:
        predictions = model(batch_radiant, batch_dire)
        
        predicted_winners = (predictions >= 0.50).float()
        
        correct_guesses += (predicted_winners == batch_labels).sum().item()
        total_guesses += batch_labels.size(0)

accuracy = (correct_guesses / total_guesses) * 100

print(f"{accuracy:.2f} %")

torch.save(model.state_dict(), "saved_models/dota_model.pth")
