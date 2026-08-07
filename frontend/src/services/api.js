/**
 * Real backend API service for X-Ray analysis.
 * Talks to the Flask backend (proxied via Vite dev server at /api).
 */

const progressSteps = [
  { step: 0, label: 'Uploading image and initializing pipeline...' },
  { step: 1, label: 'Preprocessing and normalizing image...' },
  { step: 2, label: 'Segmenting lung regions...' },
  { step: 3, label: 'Classifying with EfficientNet-B2...' },
  { step: 4, label: 'Generating Grad-CAM and SHAP maps...' },
  { step: 5, label: 'Retrieving context and generating report...' },
];

export async function analyzeXray(imageFile, onProgress) {
  const formData = new FormData();
  formData.append('xray', imageFile);

  onProgress({ step: 0, label: progressSteps[0].label, progress: 15 });

  // Animate progress steps while the backend processes the image.
  const request = fetch('/api/analyze', { method: 'POST', body: formData });
  (async () => {
    for (let i = 1; i <= 5; i++) {
      await new Promise((resolve) => setTimeout(resolve, 900));
      onProgress({ step: i, label: progressSteps[i].label, progress: 15 + (i / 5) * 85 });
    }
  })();

  const response = await request;
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Analysis failed');
  }
  return data.result;
}
