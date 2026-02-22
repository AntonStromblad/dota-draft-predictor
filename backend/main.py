import bottle
from bottle import request, response, run
import torch
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ROOT_DIR)

from ml_model.model import DotaDraftPredictor

app = bottle.Bottle()

@app.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

NUM_HEROES = 156
model = DotaDraftPredictor(num_heroes=NUM_HEROES)

model_path = os.path.join(os.path.dirname(__file__), '..', 'ml_model', 'saved_models', 'dota_model.pth')
model.load_state_dict(torch.load(model_path, weights_only=True))


model.eval() 

@app.route('/predict', method=['OPTIONS', 'POST'])
def predict():
    if request.method == 'OPTIONS':
        return {}
        
    data = request.json
    radiant_ids = data.get('radiant', []) 
    dire_ids = data.get('dire', [])        
    
    radiant_tensor = torch.zeros(NUM_HEROES)
    dire_tensor = torch.zeros(NUM_HEROES)
    
    for h_id in radiant_ids:
        if h_id < NUM_HEROES:
            radiant_tensor[h_id] = 1
            
    for h_id in dire_ids:
        if h_id < NUM_HEROES:
            dire_tensor[h_id] = 1
            
    radiant_batch = radiant_tensor.unsqueeze(0)
    dire_batch = dire_tensor.unsqueeze(0)
    
    with torch.no_grad():
        prediction = model(radiant_batch, dire_batch)
        win_prob = prediction.item()
        
    return {
        "radiant_win_prob": win_prob,
        "dire_win_prob": 1.0 - win_prob
    }

if __name__ == '__main__':
    run(app, host='localhost', port=8080, reloader=True)