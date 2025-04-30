import React from 'react';

function ResponseDisplay({ response }) {
  if (!response) {
    return <p>No response yet.</p>;
  }

  return (
    <div>
      <h2>Response</h2>
      <div>
        <strong>Status:</strong> {response.status}
      </div>
      <div>
        <strong>Headers:</strong>
        <pre>{JSON.stringify(response.headers, null, 2)}</pre>
      </div>
      <div>
        <strong>Body:</strong>
        <pre>{response.body}</pre>
      </div>
    </div>
  );
}

export default ResponseDisplay;