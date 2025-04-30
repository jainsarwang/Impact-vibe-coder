import React, { useState } from 'react';
import RequestForm from './components/RequestForm';
import ResponseDisplay from './components/ResponseDisplay';

function App() {
  const [response, setResponse] = useState(null);

  const handleSendRequest = async (requestData) => {
    try {
      const response = await fetch('http://localhost:5000/api/send-request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();
      setResponse(data);
    } catch (error) {
      console.error(error);
      setResponse({ status: 'Error', body: error.message, headers: {} });
    }
  };

  return (
    <div>
      <h1>Webman</h1>
      <RequestForm onSendRequest={handleSendRequest} />
      <ResponseDisplay response={response} />
    </div>
  );
}

export default App;