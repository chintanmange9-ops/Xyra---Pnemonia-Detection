const diseaseInfo = {
  overview: {
    id: 'overview',
    title: 'What is Pneumonia?',
    content: 'Pneumonia is an infection that inflames the air sacs in one or both lungs. The air sacs may fill with fluid or pus (purulent material), causing cough with phlegm or pus, fever, chills, and difficulty breathing. A variety of organisms, including bacteria, viruses and fungi, can cause pneumonia. It can range in seriousness from mild to life-threatening.',
    icon: '🫁'
  },
  types: {
    id: 'types',
    title: 'Types of Pneumonia',
    items: [
      {
        name: 'Bacterial Pneumonia',
        description: 'The most common cause of bacterial pneumonia in the U.S. is Streptococcus pneumoniae. This type of pneumonia can occur on its own or after you\'ve had a viral cold or the flu.',
        symptoms: 'High fever, profuse sweating, rapid breathing, and a cough that produces thick, greenish, or blood-tinged mucus.',
        xrayPattern: 'Typically presents as lobar consolidation, where an entire section (lobe) of the lung appears opaque and white on the X-ray.'
      },
      {
        name: 'Viral Pneumonia',
        description: 'Viruses that infect the respiratory tract can cause pneumonia. Viruses are the most common cause of pneumonia in children younger than 5 years.',
        symptoms: 'Often begins with flu-like symptoms (fever, dry cough, headache, muscle pain, and weakness). Symptoms typically worsen over 12 to 36 hours.',
        xrayPattern: 'Usually shows diffuse, bilateral, interstitial infiltrates—often appearing as patchy or streaky opacities spread across both lungs.'
      }
    ]
  },
  symptoms: {
    id: 'symptoms',
    title: 'Common Symptoms',
    items: [
      { name: 'Fever', description: 'Fever, sweating and shaking chills — often the first sign', icon: '🤒' },
      { name: 'Cough', description: 'Persistent cough which may produce greenish, yellow or blood-tinged phlegm', icon: '🗣️' },
      { name: 'Shortness of Breath', description: 'Difficult or labored breathing, breathlessness even at rest or on light exertion', icon: '😮‍💨' },
      { name: 'Chest Pain', description: 'Sharp or stabbing chest pain that worsens when you breathe deeply or cough', icon: '⚡' },
      { name: 'Fatigue', description: 'Extreme tiredness and weakness, general feeling of being unwell', icon: '🥱' },
      { name: 'Confusion', description: 'Changes in mental awareness — notably in adults age 65+ (ATS/IDSA)', icon: '🧠' }
    ]
  },
  prevention: {
    id: 'prevention',
    title: 'Prevention',
    items: [
      { name: 'Get Vaccinated', description: 'Vaccines are available to prevent some types of pneumonia and the flu.' },
      { name: 'Practice Good Hygiene', description: 'Wash your hands regularly or use an alcohol-based hand sanitizer.' },
      { name: 'Don\'t Smoke', description: 'Smoking damages your lungs\' natural defenses against respiratory infections.' },
      { name: 'Keep Your Immune System Strong', description: 'Get enough sleep, exercise regularly, and eat a healthy diet.' },
      { name: 'Avoid Sick People', description: 'Stay away from people who have infections that could lead to pneumonia.' }
    ]
  }
};

export default diseaseInfo;
