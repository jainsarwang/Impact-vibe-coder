import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [chatLog, setChatLog] = useState([]);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    // Scroll to bottom on new message
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatLog]);

  const sendMessage = async () => {
    if (message.trim() === '') return;

    setChatLog([...chatLog, { user: 'You', message }]);
    setMessage('');

    try {
      const response = await axios.post('http://127.0.0.1:5000/chat', { message });
      setChatLog(prevChatLog => [...prevChatLog, { user: 'Chatbot', message: response.data.reply, source: response.data.source }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setChatLog(prevChatLog => [...prevChatLog, { user: 'Chatbot', message: 'Error processing message.', source: 'Error' }]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  return(
    <div className="container">
      <header className="header">
        <h1>IntelliChat</h1>
        <p>Powered by Groq and Gemini</p>
      </header>

      <div className="chat-container" ref={chatContainerRef}>
        {chatLog.map((msg, index) => (
          <div key={index} className={`message-container ${msg.user === 'You' ? 'user-message' : 'chatbot-message'}`}>
            <div className="message">
              <span className="user">{msg.user}:</span> {msg.message}
              {msg.source && msg.source !== 'Error' && <span className="source"> (Source: {msg.source})</span>}
            </div>
          </div>
        ))}
      </div>

      <div className="input-area">
        <input
          type="text"
          className="message-input"
          placeholder="Type your message..."
          value={message}
          onChange={e => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button className="send-button" onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default App;
