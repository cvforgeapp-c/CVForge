'use client';

import React, { useState } from 'react';
import { LandingView } from './components/LandingView';
import { InteractiveUploadView } from './components/UploadView';
import { AuthRetentionModal } from './components/AuthModal';

type Step = 'landing' | 'upload';

export default function Home() {
  const [currentStep, setCurrentStep] = useState<Step>('landing');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [showAuthModal, setShowAuthModal] = useState<boolean>(false);

  const goToStep = (step: Step) => {
    setCurrentStep(step);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleExportClick = () => {
    if (!isAuthenticated) {
      setShowAuthModal(true);
    } else {
      // Trigger PDF download logic here
      alert(`Downloading PDF for session: ${sessionId}`);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased">
      {currentStep === 'landing' && (
        <LandingView onGetStarted={() => goToStep('upload')} />
      )}

      {currentStep === 'upload' && (
        <InteractiveUploadView 
          onSessionCreated={(id) => setSessionId(id)}
          onExportRequested={handleExportClick}
        />
      )}

      {showAuthModal && (
        <AuthRetentionModal 
          onClose={() => setShowAuthModal(false)}
          onSuccess={() => {
            setIsAuthenticated(true);
            setShowAuthModal(false);
            alert(`Authenticated! Downloading session: ${sessionId}`);
          }}
        />
      )}
    </main>
  );
}
