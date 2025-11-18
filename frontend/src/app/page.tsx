'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface Message {
  id: string;
  question: string;
  answer: string;
  citations: Array<{
    index: number;
    title: string;
    section: string;
    url: string | null;
    relevance_score: number;
  }>;
  sources: Array<{
    chunk_id: string;
    title: string;
    source_type: string;
    text_preview: string;
    url: string | null;
  }>;
  timestamp: Date;
}

export default function ProfileGPT() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [mode, setMode] = useState<'short' | 'detailed' | 'star'>('detailed');
  const [tenantId, setTenantId] = useState('demo-tenant');
  const [showWelcome, setShowWelcome] = useState(true);

  useEffect(() => {
    // Get tenant from URL params (simpler approach)
    const urlParams = new URLSearchParams(window.location.search);
    const tenant = urlParams.get('tenant');
    if (tenant) {
      setTenantId(tenant);
      setShowWelcome(false); // Skip welcome screen if tenant is specified
    }
  }, []);

  const askQuestion = async () => {
    if (!currentQuestion.trim() || isLoading) return;

    setIsLoading(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: currentQuestion,
          mode: mode,
          tenant_id: tenantId,
        }),
      });

      const data = await response.json();

      const newMessage: Message = {
        id: Date.now().toString(),
        question: currentQuestion,
        answer: data.answer,
        citations: data.citations || [],
        sources: data.sources || [],
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, newMessage]);
      setCurrentQuestion('');
    } catch (error) {
      console.error('Error asking question:', error);

      const errorMessage: Message = {
        id: Date.now().toString(),
        question: currentQuestion,
        answer: 'Sorry, I encountered an error. Please make sure the backend server is running on localhost:8000.',
        citations: [],
        sources: [],
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      askQuestion();
    }
  };

  const sampleQuestions = [
    "What are your Python skills?",
    "Tell me about your experience",
    "What projects have you worked on?",
    "What technologies do you know?",
    "Describe your background"
  ];

  if (showWelcome && messages.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-4xl w-full">
          {/* Welcome Header */}
          <div className="text-center mb-12">
            <div className="w-20 h-20 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <span className="text-white font-bold text-3xl">P</span>
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Welcome to ProfileGPT</h1>
            <p className="text-xl text-gray-600 mb-8">AI-powered professional portfolio that answers questions about experience and skills</p>

            <div className="flex justify-center gap-4 mb-12">
              <Link
                href="/signup"
                className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Create Your ProfileGPT
              </Link>
              <Link
                href="/login"
                className="bg-white text-gray-800 px-8 py-3 rounded-lg font-semibold border border-gray-200 hover:bg-gray-50 transition-colors"
              >
                Log In
              </Link>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <div className="bg-white p-8 rounded-xl shadow-sm text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-blue-600 text-2xl">🤖</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Intelligent Q&A</h3>
              <p className="text-gray-600">Answers questions about your background using RAG technology</p>
            </div>

            <div className="bg-white p-8 rounded-xl shadow-sm text-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-green-600 text-2xl">📚</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Source Citations</h3>
              <p className="text-gray-600">Every answer includes citations from your documents</p>
            </div>

            <div className="bg-white p-8 rounded-xl shadow-sm text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-purple-600 text-2xl">🌐</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Embeddable Widget</h3>
              <p className="text-gray-600">Add to any website with one line of code</p>
            </div>
          </div>

          <div className="text-center">
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">P</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">ProfileGPT</h1>
                <p className="text-gray-600">Ask me anything about my background and experience</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/personalized" className="text-purple-600 hover:text-purple-500 text-sm font-medium">
                Personalized Chat
              </Link>
              <Link href="/login" className="text-gray-600 hover:text-gray-900 text-sm font-medium">
                Log In
              </Link>
              <Link href="/dashboard" className="text-blue-600 hover:text-blue-500 text-sm font-medium">
                Dashboard
              </Link>
              <Link href="/signup" className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">
                Create Account
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Response Mode Selector */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Response Style:
          </label>
          <div className="flex gap-2">
            {(['short', 'detailed', 'star'] as const).map((modeOption) => (
              <button
                key={modeOption}
                onClick={() => setMode(modeOption)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  mode === modeOption
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {modeOption === 'star' ? 'STAR Format' : modeOption.charAt(0).toUpperCase() + modeOption.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Chat Messages */}
        <div className="space-y-6 mb-8">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-blue-600 text-2xl">💬</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Start a conversation
              </h3>
              <p className="text-gray-600 mb-6">
                Try asking about skills, experience, or projects
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-w-2xl mx-auto">
                {sampleQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentQuestion(question)}
                  className="text-left p-3 bg-white rounded-lg border border-gray-200 hover:border-blue-300 transition-colors text-sm"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div key={message.id} className="space-y-4">
                {/* Question */}
                <div className="flex justify-end">
                  <div className="bg-blue-600 text-white px-4 py-3 rounded-lg max-w-2xl">
                    <p>{message.question}</p>
                  </div>
                </div>

                {/* Answer */}
                <div className="flex justify-start">
                  <div className="bg-white px-4 py-3 rounded-lg max-w-2xl shadow-sm">
                    <p className="whitespace-pre-wrap text-gray-900">
                      {message.answer}
                    </p>

                    {/* Citations */}
                    {message.citations.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <p className="text-xs font-medium text-gray-500 mb-2">
                          Sources:
                        </p>
                        <div className="space-y-1">
                          {message.citations.map((citation, index) => (
                            <div key={index} className="text-xs text-gray-600">
                              [{citation.index}] {citation.title} - {citation.section}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Input Area */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex gap-3">
            <textarea
              value={currentQuestion}
              onChange={(e) => setCurrentQuestion(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about my background..."
              rows={3}
              className="flex-1 border-0 bg-transparent resize-none focus:outline-none text-black placeholder-gray-500"
              disabled={isLoading}
            />
            <button
              onClick={askQuestion}
              disabled={!currentQuestion.trim() || isLoading}
              className="self-end px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? '...' : 'Ask'}
            </button>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Press Enter to send, Shift+Enter for new line
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-sm text-gray-500">
          <p>
            Powered by ProfileGPT - 100% Free RAG Implementation
          </p>
          <p className="mt-1">
            Built with Next.js + FastAPI + SQLite
          </p>
        </footer>
      </main>
    </div>
  );
}
