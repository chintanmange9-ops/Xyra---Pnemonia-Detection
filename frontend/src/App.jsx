import React, { useState, useCallback } from 'react'
import useScrollSpy from './hooks/useScrollSpy'

// Section Components
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import About from './components/About'
import HowItWorks from './components/HowItWorks'
import DiseaseAwareness from './components/DiseaseAwareness'
import Upload from './components/Upload'
import Dashboard from './components/Dashboard'
import BatchDashboard from './components/BatchDashboard'
import Team from './components/Team'
import Footer from './components/Footer'

const SECTION_IDS = ['home', 'upload', 'dashboard', 'about', 'how-it-works', 'awareness', 'team']

function App() {
  // Track which section is currently in viewport for navbar highlighting
  const activeSection = useScrollSpy(SECTION_IDS)

  // Analysis state — lifted here so Upload and Dashboard can communicate
  const [analysisResults, setAnalysisResults] = useState(null)
  const [uploadedImageUrl, setUploadedImageUrl] = useState(null)
  const [batchResults, setBatchResults] = useState(null)

  // Called by Upload when single analysis completes
  const handleAnalysisComplete = useCallback((results, imageUrl) => {
    setBatchResults(null)
    setAnalysisResults(results)
    setUploadedImageUrl(imageUrl)

    // Smooth scroll to dashboard after a brief delay
    setTimeout(() => {
      const dashboardEl = document.getElementById('dashboard')
      if (dashboardEl) {
        dashboardEl.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }, 300)
  }, [])

  // Called by Upload when folder batch completes
  const handleBatchComplete = useCallback((batch) => {
    setAnalysisResults(null)
    setUploadedImageUrl(null)
    setBatchResults(batch)
    setTimeout(() => {
      const el = document.getElementById('dashboard')
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 300)
  }, [])

  // Called by Dashboard "Analyze Another" button
  const handleReset = useCallback(() => {
    setAnalysisResults(null)
    setUploadedImageUrl(null)
    setBatchResults(null)

    // Scroll back to upload section
    setTimeout(() => {
      const uploadEl = document.getElementById('upload')
      if (uploadEl) {
        uploadEl.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }, 100)
  }, [])

  return (
    <div className="app">
      <Navbar activeSection={activeSection} />
      
      <main>
        <Hero />
        <Upload onAnalysisComplete={handleAnalysisComplete} onBatchComplete={handleBatchComplete} />
        {batchResults ? (
          <BatchDashboard batch={batchResults} onReset={handleReset} />
        ) : (
          <Dashboard 
            results={analysisResults} 
            imageUrl={uploadedImageUrl} 
            onReset={handleReset} 
          />
        )}
        <About />
        <HowItWorks />
        <DiseaseAwareness />
        <Team />
      </main>

      <Footer />
    </div>
  )
}

export default App
