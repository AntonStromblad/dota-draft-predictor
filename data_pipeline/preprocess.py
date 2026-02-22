import torch
import json
from torch.utils.data import Dataset, DataLoader

with open('raw_data/pro_picks.json', 'r') as file:
    matches = json.load(file)


all_radiant_picks = []
all_dire_picks = []
labels = []
NUM_HEROES = 156

for match in matches:
    radiant_picks = torch.zeros([NUM_HEROES])
    dire_picks = torch.zeros([NUM_HEROES])
    for hero in match['players']:
        if hero['isRadiant']:
            radiant_picks[hero['heroId']] = 1
        else:
            dire_picks[hero['heroId']] = 1
    all_radiant_picks.append(radiant_picks)
    all_dire_picks.append(dire_picks)
    labels.append(1.0 if match['didRadiantWin'] else 0.0)

X_radiant = torch.stack(all_radiant_picks)
X_dire = torch.stack(all_dire_picks)
y_labels = torch.tensor(labels).view(-1, 1)

print(f"Radiant Tensor format: {X_radiant.shape}")  
print(f"Dire Tensor format: {X_dire.shape}")        
print(f"Labels format: {y_labels.shape}")

class DotaDataset(Dataset):
    def __init__(self, radiant_data, dire_data, labels_data):
        self.radiant = radiant_data
        self.dire = dire_data
        self.labels = labels_data

    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        return self.radiant[idx], self.dire[idx], self.labels[idx]
    
dataset = DotaDataset(X_radiant, X_dire, y_labels)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

print(len(dataset))