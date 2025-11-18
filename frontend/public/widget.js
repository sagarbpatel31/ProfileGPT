/**
 * ProfileGPT Embeddable Widget
 * A lightweight chat widget that can be embedded in any website
 * Usage: <script src="https://profilegpt.com/widget.js" data-tenant="your-tenant-id"></script>
 */

(function() {
  'use strict';

  // Configuration
  const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://api.profilegpt.com';

  // Get tenant ID from script tag
  const scriptTag = document.querySelector('script[data-tenant]');
  const TENANT_ID = scriptTag ? scriptTag.getAttribute('data-tenant') : 'demo-tenant';

  // Widget state
  let isOpen = false;
  let messages = [];
  let isLoading = false;

  // Create widget HTML
  function createWidget() {
    const widgetHTML = `
      <div id="profilegpt-widget" style="
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      ">
        <!-- Chat Button -->
        <button id="profilegpt-toggle" style="
          width: 60px;
          height: 60px;
          border-radius: 50%;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border: none;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 24px;
          transition: transform 0.2s;
        ">
          💬
        </button>

        <!-- Chat Window -->
        <div id="profilegpt-window" style="
          position: absolute;
          bottom: 80px;
          right: 0;
          width: 350px;
          height: 500px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 8px 25px rgba(0,0,0,0.15);
          display: none;
          flex-direction: column;
          overflow: hidden;
        ">
          <!-- Header -->
          <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px;
            font-weight: 600;
            position: relative;
          ">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="font-size: 18px;">💼</span>
              <span>Ask about my experience</span>
            </div>
            <button id="profilegpt-close" style="
              position: absolute;
              top: 12px;
              right: 12px;
              background: none;
              border: none;
              color: white;
              font-size: 20px;
              cursor: pointer;
              width: 24px;
              height: 24px;
              display: flex;
              align-items: center;
              justify-content: center;
            ">×</button>
          </div>

          <!-- Messages -->
          <div id="profilegpt-messages" style="
            flex: 1;
            padding: 16px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: #f8fafc;
          ">
            <div style="
              background: #e2e8f0;
              padding: 12px;
              border-radius: 8px;
              font-size: 14px;
              text-align: center;
              color: #475569;
            ">
              👋 Hi! Ask me anything about my background and experience.
            </div>
          </div>

          <!-- Input -->
          <div style="
            padding: 16px;
            border-top: 1px solid #e2e8f0;
            background: white;
          ">
            <div style="display: flex; gap: 8px;">
              <input id="profilegpt-input" type="text" placeholder="Ask about skills, experience..." style="
                flex: 1;
                padding: 8px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
                outline: none;
                transition: border-color 0.2s;
              " />
              <button id="profilegpt-send" style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: opacity 0.2s;
              ">Send</button>
            </div>
          </div>
        </div>
      </div>
    `;

    document.body.insertAdjacentHTML('beforeend', widgetHTML);
  }

  // Add message to chat
  function addMessage(message, isUser = false) {
    const messagesContainer = document.getElementById('profilegpt-messages');

    const messageDiv = document.createElement('div');
    messageDiv.style.cssText = `
      max-width: 80%;
      padding: 10px 12px;
      border-radius: 12px;
      font-size: 14px;
      line-height: 1.4;
      word-wrap: break-word;
      ${isUser ? `
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        align-self: flex-end;
        margin-left: auto;
      ` : `
        background: white;
        color: #1f2937;
        border: 1px solid #e5e7eb;
        align-self: flex-start;
      `}
    `;

    messageDiv.textContent = message;
    messagesContainer.appendChild(messageDiv);

    // Auto scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // Send message to API
  async function sendMessage(question) {
    if (isLoading) return;

    isLoading = true;
    addMessage(question, true);

    // Show typing indicator
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.style.cssText = `
      background: white;
      color: #6b7280;
      padding: 10px 12px;
      border-radius: 12px;
      font-size: 14px;
      border: 1px solid #e5e7eb;
      align-self: flex-start;
      font-style: italic;
    `;
    typingDiv.textContent = 'Thinking...';

    const messagesContainer = document.getElementById('profilegpt-messages');
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
      const response = await fetch(`${API_BASE}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question,
          mode: 'short', // Use short mode for widget
          tenant_id: TENANT_ID
        }),
      });

      const data = await response.json();

      // Remove typing indicator
      typingDiv.remove();

      // Add response
      let answer = data.answer || 'Sorry, I could not process your question.';

      // Add citations if available
      if (data.citations && data.citations.length > 0) {
        const sources = data.citations.map(c => c.title).join(', ');
        answer += `\n\nSources: ${sources}`;
      }

      addMessage(answer);

    } catch (error) {
      console.error('ProfileGPT Widget Error:', error);
      typingDiv.remove();
      addMessage('Sorry, there was an error connecting to the service. Please try again.');
    } finally {
      isLoading = false;
    }
  }

  // Initialize widget
  function init() {
    createWidget();

    const toggle = document.getElementById('profilegpt-toggle');
    const window = document.getElementById('profilegpt-window');
    const close = document.getElementById('profilegpt-close');
    const input = document.getElementById('profilegpt-input');
    const send = document.getElementById('profilegpt-send');

    // Toggle widget
    toggle.addEventListener('click', () => {
      isOpen = !isOpen;
      window.style.display = isOpen ? 'flex' : 'none';
      if (isOpen) {
        input.focus();
      }
    });

    // Close widget
    close.addEventListener('click', () => {
      isOpen = false;
      window.style.display = 'none';
    });

    // Send message
    function handleSend() {
      const question = input.value.trim();
      if (question && !isLoading) {
        sendMessage(question);
        input.value = '';
      }
    }

    send.addEventListener('click', handleSend);

    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        handleSend();
      }
    });

    // Focus styles
    input.addEventListener('focus', () => {
      input.style.borderColor = '#667eea';
    });

    input.addEventListener('blur', () => {
      input.style.borderColor = '#d1d5db';
    });

    // Hover effects
    toggle.addEventListener('mouseenter', () => {
      toggle.style.transform = 'scale(1.05)';
    });

    toggle.addEventListener('mouseleave', () => {
      toggle.style.transform = 'scale(1)';
    });

    send.addEventListener('mouseenter', () => {
      if (!isLoading) {
        send.style.opacity = '0.9';
      }
    });

    send.addEventListener('mouseleave', () => {
      send.style.opacity = '1';
    });

    console.log('✅ ProfileGPT Widget loaded for tenant:', TENANT_ID);
  }

  // Load when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();