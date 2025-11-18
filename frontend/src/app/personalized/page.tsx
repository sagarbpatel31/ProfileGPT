'use client';

import { useEffect, useRef, useState } from 'react';
import { Send, User, Brain, Code, Briefcase, GraduationCap, Rocket } from 'lucide-react';
import Link from 'next/link';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  citations?: Array<{
    index: number;
    title: string;
    section: string;
    url: string | null;
  }>;
  timestamp: Date;
}

interface DataCategory {
  icon: React.ReactNode;
  title: string;
  description: string;
  sampleQuestions: string[];
}

export default function PersonalizedProfileGPT() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [mode, setMode] = useState<'short' | 'detailed' | 'star'>('detailed');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const tenantId = 'tenant_ed07408a'; // Your tenant ID

  const dataCategories: DataCategory[] = [
    {
      icon: <User className="w-5 h-5 text-blue-600" />,
      title: "Professional Bio",
      description: "Background and current role",
      sampleQuestions: [
        "Who are you?",
        "Tell me about yourself",
        "What's your background?"
      ]
    },
    {
      icon: <Briefcase className="w-5 h-5 text-green-600" />,
      title: "Work Experience",
      description: "Career history and roles",
      sampleQuestions: [
        "What's your work experience?",
        "Tell me about Cisco",
        "What do you do at R-Tek?"
      ]
    },
    {
      icon: <Code className="w-5 h-5 text-purple-600" />,
      title: "Technical Skills",
      description: "Programming and technologies",
      sampleQuestions: [
        "What are your Python skills?",
        "What technologies do you know?",
        "Tell me about your coding experience"
      ]
    },
    {
      icon: <Rocket className="w-5 h-5 text-orange-600" />,
      title: "Projects & Research",
      description: "Notable work and achievements",
      sampleQuestions: [
        "What projects have you built?",
        "Tell me about your drone project",
        "What AI research have you done?"
      ]
    },
    {
      icon: <Brain className="w-5 h-5 text-pink-600" />,
      title: "AI & Machine Learning",
      description: "Deep learning and research",
      sampleQuestions: [
        "What's your AI experience?",
        "Tell me about machine learning",
        "What deep learning models have you built?"
      ]
    },
    {
      icon: <GraduationCap className="w-5 h-5 text-indigo-600" />,
      title: "Education",
      description: "Academic background",
      sampleQuestions: [
        "What's your education?",
        "Tell me about UC Irvine",
        "What did you study?"
      ]
    }
  ];

  const askQuestion = async (question: string) => {
    if (!question.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      text: question,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question,
          mode: mode,
          tenant_id: tenantId,
        }),
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        text: data.answer,
        citations: data.citations || [],
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error asking question:', error);

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        text: 'Sorry, I encountered an error. Please make sure the backend server is running on localhost:8000.',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = () => {
    askQuestion(input);
  };

  const handleCategoryClick = (category: DataCategory) => {
    setSelectedCategory(category.title);
    // Automatically ask the first sample question
    if (category.sampleQuestions.length > 0) {
      askQuestion(category.sampleQuestions[0]);
    }
  };

  const handleSampleQuestionClick = (question: string) => {
    askQuestion(question);
  };

  useEffect(() => {
    // Auto-scroll to bottom when messages change
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Welcome message
  useEffect(() => {
    if (messages.length === 0) {
      const welcomeMessage: Message = {
        id: 'welcome',
        role: 'assistant',
        text: "Hi there! 👋 I'm Sagar's AI assistant. I can answer questions about his professional background, technical skills, projects, and experience. Click on any category on the left to get started, or just ask me anything!",
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  }, []);

  return (
    <div className="flex h-screen w-full bg-gray-50">
      {/* Side Panel */}
      <aside className="w-80 bg-white border-r shadow-sm flex flex-col">
        {/* Header */}
        <div className="p-6 border-b">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-lg">S</span>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Sagar's Profile</h2>
              <p className="text-sm text-gray-600">Embedded Software Engineer</p>
            </div>
          </div>

          {/* Mode Selector */}
          <div className="mt-4">
            <label className="block text-xs font-medium text-gray-700 mb-2">
              Response Style:
            </label>
            <div className="flex gap-1">
              {(['short', 'detailed', 'star'] as const).map((modeOption) => (
                <button
                  key={modeOption}
                  onClick={() => setMode(modeOption)}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                    mode === modeOption
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {modeOption === 'star' ? 'STAR' : modeOption.charAt(0).toUpperCase() + modeOption.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Data Categories */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Explore Topics</h3>
          {dataCategories.map((category, index) => (
            <div key={index}>
              <button
                onClick={() => handleCategoryClick(category)}
                className={`w-full p-4 rounded-xl shadow-sm text-left transition-all hover:shadow-md ${
                  selectedCategory === category.title
                    ? 'bg-blue-50 border-2 border-blue-200'
                    : 'bg-gray-50 hover:bg-gray-100'
                }`}
              >
                <div className="flex items-start gap-3">
                  {category.icon}
                  <div className="flex-1">
                    <div className="font-medium text-gray-900 text-sm">{category.title}</div>
                    <div className="text-xs text-gray-600 mt-1">{category.description}</div>
                  </div>
                </div>
              </button>

              {/* Sample Questions for Selected Category */}
              {selectedCategory === category.title && (
                <div className="mt-2 ml-8 space-y-1">
                  {category.sampleQuestions.slice(1).map((question, qIndex) => (
                    <button
                      key={qIndex}
                      onClick={() => handleSampleQuestionClick(question)}
                      className="block w-full text-left px-3 py-2 text-xs text-blue-600 hover:bg-blue-50 rounded-lg"
                    >
                      "{question}"
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Bottom Navigation */}
        <div className="p-4 border-t">
          <Link
            href="/"
            className="block w-full text-center px-4 py-2 text-sm text-gray-600 hover:text-blue-600 border border-gray-300 rounded-lg hover:border-blue-300 transition-colors"
          >
            ← Back to Simple Chat
          </Link>
        </div>
      </aside>

      {/* Chat Section */}
      <main className="flex flex-col flex-1">
        {/* Header */}
        <header className="px-6 py-4 border-b bg-white shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-lg font-medium text-gray-900">
                Chat with Sagar's AI Assistant
              </h1>
              <p className="text-sm text-gray-600">
                Ask anything about his professional background and experience
              </p>
            </div>
            <div className="text-xs text-gray-500">
              Mode: <span className="font-medium">{mode}</span>
            </div>
          </div>
        </header>

        {/* Chat Messages */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4 flex flex-col">
          <div className="flex-1 space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`max-w-3xl p-4 rounded-2xl shadow-sm text-sm ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white self-end ml-auto'
                    : 'bg-white border'
                }`}
              >
                <div className="whitespace-pre-wrap">{msg.text}</div>

                {/* Citations */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs font-medium text-gray-500 mb-2">Sources:</p>
                    <div className="space-y-1">
                      {msg.citations.map((citation, index) => (
                        <div key={index} className="text-xs text-gray-600">
                          [{citation.index}] {citation.title} - {citation.section}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="max-w-3xl p-4 rounded-2xl bg-white border shadow-sm">
                <div className="flex items-center space-x-2">
                  <div className="animate-pulse flex space-x-1">
                    <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-sm text-gray-500">Thinking...</span>
                </div>
              </div>
            )}
          </div>
          <div ref={messagesEndRef} />
        </div>

        {/* Input Box */}
        <div className="p-4 border-t bg-white flex items-center gap-3">
          <input
            className="flex-1 p-3 rounded-2xl border shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about Sagar's experience, skills, projects..."
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="p-3 rounded-2xl shadow bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            aria-label="Send message"
          >
            <Send size={18} />
          </button>
        </div>
      </main>
    </div>
  );
}