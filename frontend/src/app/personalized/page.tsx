'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { Send, User, Brain, Code, Briefcase, GraduationCap, Rocket, ShieldCheck } from 'lucide-react';
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
  id?: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  sampleQuestions: string[];
}

interface InsightCategoryResponse {
  id?: string;
  title: string;
  description: string;
  sampleQuestions?: string[];
}

interface TenantInfo {
  tenant_id: string;
  name?: string;
  profession?: string;
  bio?: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const getCategoryIcon = (categoryId?: string) => {
  switch (categoryId) {
    case 'technical':
      return <Code className="w-5 h-5 text-purple-600" />;
    case 'projects':
      return <Rocket className="w-5 h-5 text-orange-600" />;
    case 'ai_innovation':
      return <Brain className="w-5 h-5 text-pink-600" />;
    case 'education':
      return <GraduationCap className="w-5 h-5 text-indigo-600" />;
    case 'experience':
      return <Briefcase className="w-5 h-5 text-green-600" />;
    default:
      return <User className="w-5 h-5 text-blue-600" />;
  }
};

const DEFAULT_CATEGORIES: DataCategory[] = [
  {
    id: 'bio',
    icon: <User className="w-5 h-5 text-blue-600" />,
    title: "Professional Bio",
    description: "Background and career focus",
    sampleQuestions: [
      "Give me a short professional summary.",
      "What motivates this person?",
      "Describe their background."
    ]
  },
  {
    id: 'experience',
    icon: <Briefcase className="w-5 h-5 text-green-600" />,
    title: "Experience Highlights",
    description: "Roles, responsibilities, and impact",
    sampleQuestions: [
      "Walk me through their recent roles.",
      "What did they accomplish in their last job?",
      "Share a leadership example."
    ]
  },
  {
    id: 'technical',
    icon: <Code className="w-5 h-5 text-purple-600" />,
    title: "Technical Skills",
    description: "Tools, languages, and frameworks",
    sampleQuestions: [
      "List their core technical strengths.",
      "How strong are they with Python?",
      "What technologies do they use daily?"
    ]
  },
  {
    id: 'projects',
    icon: <Rocket className="w-5 h-5 text-orange-600" />,
    title: "Projects & Impact",
    description: "Notable work and measurable outcomes",
    sampleQuestions: [
      "Share a project with tangible impact.",
      "What research have they contributed to?",
      "Describe a complex problem they solved."
    ]
  },
  {
    id: 'ai_innovation',
    icon: <Brain className="w-5 h-5 text-pink-600" />,
    title: "AI & Innovation",
    description: "Automation, ML, and experimentation",
    sampleQuestions: [
      "What AI/ML projects have they led?",
      "How do they approach innovation?",
      "Have they automated any workflows?"
    ]
  },
  {
    id: 'education',
    icon: <GraduationCap className="w-5 h-5 text-indigo-600" />,
    title: "Education & Credentials",
    description: "Academic background and certifications",
    sampleQuestions: [
      "Summarize their education.",
      "What did they study?",
      "Do they hold any certifications?"
    ]
  }
];

export default function PersonalizedProfileGPT() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [mode, setMode] = useState<'short' | 'detailed' | 'star'>('detailed');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [tenantInfo, setTenantInfo] = useState<TenantInfo | null>(null);
  const [activeTenantId, setActiveTenantId] = useState('demo-tenant');
  const [tenantSource, setTenantSource] = useState<'demo' | 'local' | 'query'>('demo');
  const [tenantReady, setTenantReady] = useState(false);
  const [hasIntroMessage, setHasIntroMessage] = useState(false);
  const [categories, setCategories] = useState<DataCategory[]>(DEFAULT_CATEGORIES);
  const [topSkills, setTopSkills] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const stored = localStorage.getItem('profilegpt_tenant');
    if (stored) {
      const parsed = JSON.parse(stored);
      setTenantInfo(parsed);
      setActiveTenantId(parsed.tenant_id);
      setTenantSource('local');
    }

    const params = new URLSearchParams(window.location.search);
    const tenantParam = params.get('tenant');
    if (tenantParam) {
      setActiveTenantId(tenantParam);
      if (!stored) {
        setTenantSource('query');
      }
    }

    setTenantReady(true);
  }, []);

  useEffect(() => {
    if (!tenantReady) return;

    fetch(`${API_BASE}/tenant/${activeTenantId}/insights`)
      .then(res => res.json())
      .then(data => {
        const remoteCategories = (data.categories || []).map((category: InsightCategoryResponse) => ({
          id: category.id,
          title: category.title,
          description: category.description,
          sampleQuestions: category.sampleQuestions || [],
          icon: getCategoryIcon(category.id)
        }));

        if (remoteCategories.length) {
          setCategories(remoteCategories);
        } else {
          setCategories(DEFAULT_CATEGORIES);
        }

        setTopSkills(data.top_skills || []);
      })
      .catch(() => {
        setCategories(DEFAULT_CATEGORIES);
        setTopSkills([]);
      });
  }, [tenantReady, activeTenantId]);

  const tenantDisplayName = useMemo(() => {
    if (tenantInfo?.name) return tenantInfo.name;
    if (tenantSource === 'query') return 'Guest Profile';
    if (tenantSource === 'demo') return 'Demo Professional';
    return 'ProfileGPT User';
  }, [tenantInfo, tenantSource]);

  const professionLabel = tenantInfo?.profession || 'AI-powered professional profile';

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
      const response = await fetch(`${API_BASE}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          mode,
          tenant_id: activeTenantId,
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
        text: 'Sorry, I could not reach the API. Please verify the backend server is running and try again.',
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
    if (category.sampleQuestions.length > 0) {
      askQuestion(category.sampleQuestions[0]);
    }
  };

  const handleSampleQuestionClick = (question: string) => {
    askQuestion(question);
  };

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  useEffect(() => {
    if (!tenantReady || hasIntroMessage) return;

    const subjectLabel = tenantInfo?.name
      ? `${tenantInfo.name}'s`
      : tenantSource === 'demo'
        ? 'this demo'
        : 'this';

    const welcomeMessage: Message = {
      id: 'welcome',
      role: 'assistant',
      text: `Hi there! 👋 Ask me anything about ${subjectLabel} experience, skills, or education. I'll respond with concise bullet points, STAR stories, and citations so recruiters can trust every answer.`,
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
    setHasIntroMessage(true);
  }, [tenantInfo, tenantSource, tenantReady, hasIntroMessage]);

  const renderBoldText = (content: string) => {
    const parts = content.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={index}>{part.slice(2, -2)}</strong>;
      }
      return <span key={index}>{part}</span>;
    });
  };

  const renderMessageContent = (text: string) => {
    const lines = text.split('\n').map(line => line.trim()).filter(Boolean);
    const segments: Array<{ type: 'paragraph'; text: string } | { type: 'list'; items: string[] }> = [];
    let currentList: string[] = [];

    const flushList = () => {
      if (currentList.length) {
        segments.push({ type: 'list', items: currentList });
        currentList = [];
      }
    };

    lines.forEach(line => {
      const isBullet = /^(\d+\.)|[-*•–]\s/.test(line);
      if (isBullet) {
        const cleaned = line.replace(/^(\d+\.)\s*|[-*•–]\s*/, '');
        currentList.push(cleaned);
      } else {
        flushList();
        segments.push({ type: 'paragraph', text: line });
      }
    });

    flushList();

    if (!segments.length) {
      return (
        <p className="leading-relaxed text-gray-900 text-base">{renderBoldText(text)}</p>
      );
    }

    return segments.map((segment, index) =>
      segment.type === 'paragraph' ? (
        <p key={`p-${index}`} className="leading-relaxed text-gray-900 text-base mb-2">
          {renderBoldText(segment.text)}
        </p>
      ) : (
        <ul key={`list-${index}`} className="list-disc pl-5 space-y-1 text-gray-900 text-base mb-2">
          {segment.items.map((item, itemIndex) => (
            <li key={`li-${index}-${itemIndex}`}>{renderBoldText(item)}</li>
          ))}
        </ul>
      )
    );
  };

  const placeholder = tenantInfo?.name
    ? `Ask about ${tenantInfo.name}'s experience, skills, or achievements...`
    : 'Ask about this professional’s experience, skills, or achievements...';

  return (
    <div className="flex h-screen w-full bg-slate-50">
      {/* Side Panel */}
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
          <div className="flex items-center gap-2 text-xs text-gray-500 bg-gray-100 rounded-lg p-3">
            <ShieldCheck className="w-4 h-4 text-green-600" />
            Responses include citations taken directly from your uploaded sources.
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

        {(tenantInfo?.profession || topSkills.length > 0) && (
          <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-xl space-y-3">
            {tenantInfo?.profession && (
              <div>
                <p className="text-xs uppercase tracking-wide text-gray-500 font-semibold">Profession</p>
                <p className="text-sm text-gray-800">{tenantInfo.profession}</p>
              </div>
            )}
            {topSkills.length > 0 && (
              <div>
                <p className="text-xs uppercase tracking-wide text-gray-500 font-semibold mb-2">Top strengths</p>
                <div className="flex flex-wrap gap-2">
                  {topSkills.map(skill => (
                    <span key={skill} className="px-2 py-1 bg-white text-gray-800 rounded-full text-xs border border-gray-200">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Explore Topics</h3>
          {categories.map((category, index) => (
            <div key={index}>
              <button
                onClick={() => handleCategoryClick(category)}
                className={`w-full p-4 rounded-xl text-left transition-all border ${
                  selectedCategory === category.title
                    ? 'bg-blue-50 border-blue-200 shadow-sm'
                    : 'bg-white border-gray-200 hover:shadow'
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

              {selectedCategory === category.title && (
                <div className="mt-2 ml-8 space-y-1">
                  {category.sampleQuestions.slice(1).map((question, qIndex) => (
                    <button
                      key={qIndex}
                      onClick={() => handleSampleQuestionClick(question)}
                      className="block w-full text-left px-3 py-2 text-xs text-blue-600 hover:bg-blue-50 rounded-lg"
                    >
                      <span>&ldquo;{question}&rdquo;</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="p-4 border-t space-y-2">
          {tenantInfo ? (
            <>
              <Link
                href="/dashboard"
                className="block w-full text-center px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition"
              >
                Open Dashboard
              </Link>
              <Link
                href="/"
                className="block w-full text-center px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:border-blue-300 transition"
              >
                Back to Landing
              </Link>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="block w-full text-center px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition"
              >
                Log In to Manage
              </Link>
              <Link
                href="/signup"
                className="block w-full text-center px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:border-blue-300 transition"
              >
                Create Account
              </Link>
            </>
          )}
        </div>
      </aside>

      {/* Chat Section */}
      <main className="flex flex-col flex-1 bg-slate-50">
        <header className="px-6 py-4 border-b bg-white shadow-sm">
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div>
              <h1 className="text-lg font-semibold text-gray-900">
                Chat with this AI Resume Assistant
              </h1>
              <p className="text-sm text-gray-600">
                Ask anything about {tenantInfo?.name ? `${tenantInfo.name}'s` : 'this professional\'s'} experience, skills, or achievements.
              </p>
            </div>
            <div className="text-xs text-gray-500">
              Mode: <span className="font-medium">{mode}</span>
            </div>
          </div>
          {!tenantInfo && tenantSource === 'demo' && (
            <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50 text-amber-900 text-sm px-4 py-2">
              You&apos;re viewing the public demo. <Link href="/login" className="underline">Log in</Link> to chat with your own data.
            </div>
          )}
        </header>

        <div className="flex-1 p-6 overflow-y-auto space-y-4 flex flex-col">
          <div className="flex-1 space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`max-w-3xl p-5 rounded-2xl text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-blue-100 text-gray-900 border border-blue-200 self-end ml-auto shadow'
                    : 'bg-white text-gray-900 border border-gray-200 shadow-sm'
                }`}
              >
                {renderMessageContent(msg.text)}

                {msg.citations && msg.citations.length > 0 && (
                  <div className={`mt-4 flex flex-wrap gap-2 ${msg.role === 'user' ? 'text-gray-800' : 'text-gray-700'}`}>
                    {msg.citations.map((citation) => (
                      <span
                        key={`${msg.id}-${citation.index}`}
                        className={`inline-flex items-center rounded-full px-3 py-1 text-xs ${
                          msg.role === 'user'
                            ? 'bg-blue-200 text-blue-900 border border-blue-300'
                            : 'bg-gray-100 text-gray-700 border border-gray-200'
                        }`}
                      >
                        [{citation.index}] {citation.title}
                        {citation.section ? ` • ${citation.section}` : ''}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="max-w-3xl p-4 rounded-2xl bg-white border border-gray-200 shadow-sm">
                <div className="flex items-center space-x-2 text-gray-600 text-sm">
                  <div className="flex space-x-1">
                    <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span>Preparing a recruiter-friendly response...</span>
                </div>
              </div>
            )}
          </div>
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 border-t bg-white flex items-center gap-3">
          <input
            className="flex-1 p-3 rounded-2xl border shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black placeholder-gray-500"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={placeholder}
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
