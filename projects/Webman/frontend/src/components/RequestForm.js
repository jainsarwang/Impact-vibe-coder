import React, { useState } from 'react';

function RequestForm({ onSendRequest }) {
  const [method, setMethod] = useState('GET');
  const [url, setUrl] = useState('');
  const [headers, setHeaders] = useState([{
    key: '',
    value: ''
  }]);
  const [body, setBody] = useState('');

  const handleAddHeader = () => {
    setHeaders([...headers, {
      key: '',
      value: ''
    }]);
  };

  const handleHeaderChange = (index, field, value) => {
    const newHeaders = [...headers];
    newHeaders[index][field] = value;
    setHeaders(newHeaders);
  };

  const handleRemoveHeader = (index) => {
    const newHeaders = [...headers];
    newHeaders.splice(index, 1);
    setHeaders(newHeaders);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const headersObject = {};
    headers.forEach(header => {
      if (header.key && header.value) {
        headersObject[header.key] = header.value;
      }
    });

    onSendRequest({
      method,
      url,
      headers: headersObject,
      body
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Method:</label>
        <select value={method} onChange={(e) => setMethod(e.target.value)}>
          <option value="GET">GET</option>
          <option value="POST">POST</option>
          <option value="PUT">PUT</option>
          <option value="DELETE">DELETE</option>
        </select>
      </div>
      <div>
        <label>URL:</label>
        <input type="text" value={url} onChange={(e) => setUrl(e.target.value)} />
      </div>
      <div>
        <label>Headers:</label>
        {headers.map((header, index) => (
          <div key={index}>
            <input
              type="text"
              placeholder="Key"
              value={header.key}
              onChange={(e) => handleHeaderChange(index, 'key', e.target.value)}
            />
            <input
              type="text"
              placeholder="Value"
              value={header.value}
              onChange={(e) => handleHeaderChange(index, 'value', e.target.value)}
            />
            <button type="button" onClick={() => handleRemoveHeader(index)}>Remove</button>
          </div>
        ))}
        <button type="button" onClick={handleAddHeader}>Add Header</button>
      </div>
      <div>
        <label>Body:</label>
        <textarea value={body} onChange={(e) => setBody(e.target.value)} />
      </div>
      <button type="submit">Send Request</button>
    </form>
  );
}

export default RequestForm;