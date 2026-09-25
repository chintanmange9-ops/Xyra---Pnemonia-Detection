const pipelineSteps = [
  {
    id: 'upload',
    title: 'Image Upload',
    description: 'The user uploads a chest X-ray image in standard formats (JPEG, PNG). The system validates the image and prepares it for processing.',
    details: [
      'Format validation and file size checks',
      'Client-side image preview rendering',
      'Secure transfer to the backend processing queue'
    ],
    icon: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>'
  },
  {
    id: 'preprocessing',
    title: 'Preprocessing',
    description: 'The raw X-ray is resized to 384×384 and normalized with ImageNet mean [0.485,0.456,0.406] / std [0.229,0.224,0.225] to match EfficientNet-B2 training; CLAHE is available for visualization.',
    details: [
      'Resizing to 384×384 via LANCZOS (matches training)',
      'ImageNet normalization (not plain [0,1])',
      'CLAHE available for visualization only — not used in classification path'
    ],
    icon: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 2a10 10 0 0 0 0 20"></path></svg>'
  },
  {
    id: 'enhancement',
    title: 'Quality Check',
    description: 'Image quality and dimensions are validated before classification to ensure reliable input.',
    details: [
      'Dimension check: Poor &lt;200px → Fair &lt;500px → Good (orchestrator._assess_quality)',
      'EXIF orientation correction + RGB conversion',
      'Rejects non-image or unsupported formats (JPEG/PNG/WEBP/BMP/TIFF)'
    ],
    icon: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12h4l3-9 5 18 3-9h5"></path></svg>'
  },
  {
    id: 'classification',
    title: 'Classification',
    description: 'The core AI model analyzes the preprocessed X-ray images to detect patterns indicative of specific diseases.',
    details: [
      'EfficientNet-B2 deep learning model',
      '3-class prediction: Normal, Bacterial, Viral',
      'Softmax output for probability distributions'
    ],
    icon: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="3" x2="9" y2="21"></line></svg>'
  },
  {
    id: 'explainability',
    title: 'Explainability',
    description: 'Advanced interpretability techniques generate visual and quantitative evidence of the model\'s decision-making process.',
    details: [
      'SHAP (SHapley Additive exPlanations) for feature importance',
      'SHAP attribution maps with lung masking',
      'Visual overlays highlighting potential lesions/infiltrates'
    ],
    icon: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>'
  },
  {
    id: 'report',
    title: 'Report Generation',
    description: 'Retrieval-Augmented Generation (RAG) produces a comprehensive, medically accurate report based on the findings.',
    details: [
      'Querying FAISS vector database of medical literature',
      'LLM synthesis of visual findings and retrieved context',
      'Structured output with diagnosis, confidence, and references'
    ],
    icon: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>'
  }
];

export default pipelineSteps;
