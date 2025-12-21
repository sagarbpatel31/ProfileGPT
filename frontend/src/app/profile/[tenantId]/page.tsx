'use client';

import React, { useState, useRef, useEffect, useMemo } from 'react';
import { ChevronDown, Send, User, Briefcase, Code, Rocket, Brain, GraduationCap, Clock, MessageSquare } from 'lucide-react';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  sources?: string[];
  note?: string;
}

interface DataCategory {
  id?: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  sampleQuestions: string[];
}

interface TenantInfo {
  tenant_id: string;
  name?: string;
  profession?: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

const DEFAULT_CATEGORIES: DataCategory[] = [
  {
    id: 'bio',
    icon: <User className="w-5 h-5 text-blue-600" />,
    title: "Professional Background",
    description: "Career overview and experience",
    sampleQuestions: [
      "Give me a professional summary.",
      "What is their background?",
      "Describe their career focus."
    ]
  },
  {
    id: 'experience',
    icon: <Briefcase className="w-5 h-5 text-green-600" />,
    title: "Work Experience",
    description: "Roles, responsibilities, and achievements",
    sampleQuestions: [
      "Walk me through their recent roles.",
      "What are their key accomplishments?",
      "Tell me about their experience."
    ]
  },
  {
    id: 'technical',
    icon: <Code className="w-5 h-5 text-purple-600" />,
    title: "Core Skills",
    description: "Key competencies and expertise",
    sampleQuestions: [
      "List their core technical strengths.",
      "What skills do they have?",
      "What are their specializations?"
    ]
  },
  {
    id: 'projects',
    icon: <Rocket className="w-5 h-5 text-orange-600" />,
    title: "Projects & Achievements",
    description: "Notable work and accomplishments",
    sampleQuestions: [
      "Share their most significant projects.",
      "What notable achievements do they have?",
      "Describe their impactful work."
    ]
  },
  {
    id: 'tools',
    icon: <Brain className="w-5 h-5 text-pink-600" />,
    title: "Tools & Technologies",
    description: "Software, equipment, and methodologies",
    sampleQuestions: [
      "What tools and technologies do they use?",
      "Describe their technical toolkit.",
      "What methodologies do they employ?"
    ]
  },
  {
    id: 'education',
    icon: <GraduationCap className="w-5 h-5 text-indigo-600" />,
    title: "Education & Credentials",
    description: "Academic background and certifications",
    sampleQuestions: [
      "Summarize their education.",
      "What credentials do they hold?",
      "Describe their academic background."
    ]
  }
];

function getCategoryIcon(id?: string): React.ReactNode {
  switch (id) {
    case 'bio': return <User className="w-5 h-5 text-blue-600" />;
    case 'experience': return <Briefcase className="w-5 h-5 text-green-600" />;
    case 'technical': return <Code className="w-5 h-5 text-purple-600" />;
    case 'projects': return <Rocket className="w-5 h-5 text-orange-600" />;
    case 'ai_innovation': return <Brain className="w-5 h-5 text-pink-600" />;
    case 'education': return <GraduationCap className="w-5 h-5 text-indigo-600" />;
    default: return <MessageSquare className="w-5 h-5 text-gray-600" />;
  }
}

interface PageParams {
  params: { tenantId: string }
}

export default function PublicProfile({ params }: PageParams) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [mode, setMode] = useState<'short' | 'detailed' | 'star'>('detailed');
  const [tenantInfo, setTenantInfo] = useState<TenantInfo | null>(null);
  const [categories, setCategories] = useState<DataCategory[]>(DEFAULT_CATEGORIES);
  const [topSkills, setTopSkills] = useState<string[]>([]);
  const [hasIntroMessage, setHasIntroMessage] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const tenantId = params.tenantId;

  useEffect(() => {
    // Set basic tenant info
    setTenantInfo({
      tenant_id: tenantId,
      name: tenantId.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      profession: "Professional"
    });

    // Try to get dynamic categories based on uploaded documents
    fetch(`${API_BASE}/analyze-field`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then(res => res.json())
      .then(data => {
        if (data.categories && data.categories.length > 0) {
          const adaptiveCategories = data.categories.map((category: any) => ({
            id: category.id,
            title: category.title,
            description: category.description,
            sampleQuestions: category.sampleQuestions || [],
            icon: getCategoryIcon(category.id)
          }));
          setCategories(adaptiveCategories);
        }

        const skills = data.topSkills || [];
        setTopSkills(skills.slice(0, 8));
      })
      .catch(err => {
        console.error('Failed to analyze field:', err);
      });
  }, [tenantId]);

  useEffect(() => {
    if (!hasIntroMessage && tenantInfo) {
      const subjectLabel = tenantInfo.name || 'this professional';

      setMessages([{
        id: '1',
        text: `Hi there! 👋 Ask me anything about ${subjectLabel}'s experience, skills, or education. I'll respond with detailed information based on their uploaded documents.`,
        isUser: false,
        timestamp: new Date()
      }]);

      setHasIntroMessage(true);
    }
  }, [tenantInfo, hasIntroMessage]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const askQuestion = async (question: string) => {
    if (!question.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: question,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setInput('');

    try {
      const response = await fetch(`${API_BASE}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question, mode, tenantId }),
      });

      const data = await response.json();

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.answer || 'I apologize, but I encountered an error processing your question.',
        isUser: false,
        timestamp: new Date(),
        sources: data.sources || [],
        note: data.note
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'I apologize, but I encountered a network error. Please try again.',
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    askQuestion(input);
  };

  const handleSend = () => {
    askQuestion(input);
  };

  const handleCategoryClick = (category: DataCategory) => {
    if (category.sampleQuestions.length > 0) {
      askQuestion(category.sampleQuestions[0]);
    }
  };

  const tenantDisplayName = tenantInfo?.name || 'Professional';
  const professionLabel = tenantInfo?.profession || 'AI-powered professional profile';

  return (
    <div className="flex h-screen w-full bg-slate-50">
      {/* Side Panel - No dashboard access */}
      <aside className="w-80 bg-white border-r shadow-sm flex flex-col">
        <div className="p-6 border-b">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold text-lg">
              {tenantDisplayName.charAt(0)}
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">{tenantDisplayName}</h2>
              <p className="text-sm text-gray-600">{professionLabel}</p>
            </div>
          </div>

          <div className="mt-4">
            <label className="block text-xs font-medium text-gray-700 mb-2">
              Response Style
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

          {topSkills.length > 0 && (
            <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-xl space-y-3">
              <div>
                <p className="text-xs uppercase tracking-wide text-gray-500 font-semibold mb-2">Top Skills</p>
                <div className="flex flex-wrap gap-2">
                  {topSkills.map(skill => (
                    <span key={skill} className="px-2 py-1 bg-white text-gray-800 rounded-full text-xs border border-gray-200">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Ask About</h3>
          {categories.map((category, index) => (
            <button
              key={index}
              onClick={() => handleCategoryClick(category)}
              className="w-full p-4 rounded-xl text-left transition-all border bg-white border-gray-200 hover:shadow"
            >
              <div className="flex items-start gap-3">
                {category.icon}
                <div className="flex-1">
                  <div className="font-medium text-gray-900 text-sm">{category.title}</div>
                  <div className="text-xs text-gray-600 mt-1">{category.description}</div>
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* No dashboard access for recruiters */}
        <div className="p-4 border-t">
          <div className="text-xs text-gray-500 text-center">
            Professional AI Assistant
          </div>
        </div>
      </aside>

      <main className="flex flex-col flex-1 bg-slate-50">
        <header className="px-6 py-4 border-b bg-white shadow-sm">
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div>
              <h1 className="text-lg font-semibold text-gray-900">Chat with {tenantDisplayName}</h1>
              <p className="text-sm text-gray-600">Ask questions about experience, skills, or achievements</p>
            </div>
            <div className="text-xs text-gray-500">Mode: <span className="font-medium">{mode}</span></div>
          </div>
        </header>

        <div className="flex-1 p-6 overflow-y-auto space-y-4 flex flex-col">
          <div className="flex-1 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-3xl rounded-2xl px-4 py-3 ${
                  message.isUser
                    ? 'bg-blue-600 text-white ml-8'
                    : 'bg-white text-gray-900 border shadow-sm mr-8'
                }`}>
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>

                  {!message.isUser && (message.sources?.length || message.note) && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      {message.sources && message.sources.length > 0 && (
                        <div className="mb-2">
                          <p className="text-xs font-medium text-gray-500 mb-1">Sources:</p>
                          <div className="flex flex-wrap gap-1">
                            {message.sources.map((source, idx) => (
                              <span key={idx} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                                {source}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {message.note && (
                        <p className="text-xs text-gray-500 italic">{message.note}</p>
                      )}
                    </div>
                  )}

                  <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                    <Clock className="w-3 h-3" />
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-3xl bg-white text-gray-900 border shadow-sm mr-8 rounded-2xl px-4 py-3">
                  <div className="flex items-center space-x-2">
                    <div className="animate-pulse flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-sm text-gray-500">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="p-4 border-t bg-white flex items-center gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 p-3 rounded-2xl border shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black placeholder-gray-500"
            placeholder={`Ask about ${tenantDisplayName.toLowerCase()}'s experience, skills, or achievements...`}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="p-3 rounded-2xl shadow bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            aria-label="Send message"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </main>
    </div>
  );
}