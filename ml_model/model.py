import torch
import torch.nn as nn

NUM_HEROES = 156 

class DotaDraftPredictor(nn.Module):
    def __init__(self, num_heroes=NUM_HEROES):
        super(DotaDraftPredictor, self).__init__()

        input_size = num_heroes * 2
        self.layer1 = nn.Linear(input_size, 128)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(0.2)

        self.layer2 = nn.Linear(128, 64)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(0.2)

        self.output_layer = nn.Linear(64, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, radiant_picks, dire_picks):
        x = torch.cat((radiant_picks, dire_picks), dim=1)
        x = self.layer1(x)
        x = self.relu1(x)
        x = self.dropout1(x)

        x = self.layer2(x)
        x = self.relu2(x)
        x = self.dropout2(x)

        x = self.output_layer(x)
        win_probability = self.sigmoid(x)

        return win_probability
    
if __name__ == "__main__":
    fake_radiant = torch.zeros((5, 156))
    fake_dire = torch.zeros((5, 156))

    model = DotaDraftPredictor()
    predictions = model(fake_radiant, fake_dire)
    print(predictions)