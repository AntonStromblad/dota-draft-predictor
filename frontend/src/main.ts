import './style.css'

const predictBtn = document.getElementById('predict-btn') as HTMLButtonElement;
const radiantInput = document.getElementById('radiant-picks') as HTMLInputElement;
const direInput = document.getElementById('dire-picks') as HTMLInputElement;
const predictionText = document.getElementById('prediction-text') as HTMLHeadingElement;
const radiantBar = document.getElementById('radiant-bar') as HTMLDivElement;
const direBar = document.getElementById('dire-bar') as HTMLDivElement;

predictBtn.addEventListener('click', async () => {
  const radiant = radiantInput.value.split(',').map(n => parseInt(n.trim())).filter(n => !isNaN(n));
  const dire = direInput.value.split(',').map(n => parseInt(n.trim())).filter(n => !isNaN(n));

  predictionText.innerText = "Laddar AI:ns gissning... 🧠";

  try {
    const response = await fetch('http://localhost:8080/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ radiant, dire })
    });

    const data = await response.json();
    
    const radProb = Math.round(data.radiant_win_prob * 100);
    const direProb = Math.round(data.dire_win_prob * 100);

    predictionText.innerText = `Radiant vinstchans: ${radProb}% | Dire vinstchans: ${direProb}%`;
    radiantBar.style.width = `${radProb}%`;
    direBar.style.width = `${direProb}%`;

  } catch (error) {
    console.error(error);
    predictionText.innerText = "Något gick fel! Är Python-servern igång?";
  }
});