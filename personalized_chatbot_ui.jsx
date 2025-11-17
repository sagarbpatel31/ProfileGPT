import { useEffect, useRef, useState } from "react";
import { Send } from "lucide-react";

export default function PersonalizedChatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [data, setData] = useState([]);
  const messagesEndRef = useRef(null);

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages((prev) => [...prev, { role: "user", text: input }]);
    setInput("");
  };

  useEffect(() => {
    // Auto-scroll to bottom when messages change
    if (messagesEndRef.current) {
      // @ts-ignore - DOM element
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  // Mock API fetch
  useEffect(() => {
    let mounted = true;
    async function fetchData() {
      // Simulate network delay
      await new Promise((res) => setTimeout(res, 500));
      if (!mounted) return;
      setData([
        "Bio summary",
        "Professional background",
        "Projects & publications",
        "Personal preferences",
        "Fun facts",
      ]);
    }
    fetchData();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="flex h-screen w-full bg-gray-100">
      {/* Side Panel */}
      <aside className="w-64 bg-white border-r shadow-sm p-4 flex flex-col">
        <h2 className="text-xl font-semibold mb-4">Dalina's Data</h2>
        <div className="flex-1 overflow-y-auto space-y-3">
          {data && data.length > 0 ? (
            data.map((item, index) => (
              <div key={index} className="p-3 bg-gray-50 rounded-xl shadow-sm">
                {typeof item === "string" ? item : JSON.stringify(item)}
              </div>
            ))
          ) : (
            <div className="p-3 text-sm text-gray-500">No data available.</div>
          )}
        </div>
      </aside>

      {/* Chat Section */}
      <main className="flex flex-col flex-1">
        {/* Header */}
        <header className="px-6 py-4 border-b bg-white shadow-sm text-lg font-medium">
          What do you want to know about Dalina?
        </header>

        {/* Chat Messages */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4 flex flex-col">
          <div className="flex-1 space-y-4">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`max-w-xl p-4 rounded-2xl shadow-md text-sm whitespace-pre-wrap ${
                  msg.role === "user" ? "bg-blue-100 self-end ml-auto" : "bg-white"
                }`}
              >
                {msg.text}
              </div>
            ))}
          </div>
          <div ref={messagesEndRef} />
        </div>

        {/* Input Box */}
        <div className="p-4 border-t bg-white flex items-center gap-3">
          <input
            className="flex-1 p-3 rounded-2xl border shadow-sm focus:outline-none"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask something..."
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSend();
            }}
          />
          <button
            onClick={handleSend}
            className="p-3 rounded-2xl shadow bg-blue-500 text-white hover:bg-blue-600"
            aria-label="Send message"
          >
            <Send size={18} />
          </button>
        </div>
      </main>
    </div>
  );
}
