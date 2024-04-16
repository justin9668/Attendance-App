import React, { useState } from 'react'
import './App.css'

function App() {
  const [code, setCode] = useState('')
  const [qrCodeUrl, setQrCodeUrl] = useState('')

  const fetchCode = () => {
    fetch('http://127.0.0.1:5000/api/code')
      .then(response => response.text())
      .then(data => {
        setCode(data)
        setQrCodeUrl('')
      })
      .catch(error => console.error('Error fetching code:', error))
  }

  const fetchQRCode = () => {
    fetch('http://127.0.0.1:5000/api/qrcode')
      .then(response => {
        if (response.ok) {
          return response.blob()
        }
        throw new Error('Failed to generate QR code.')
      })
      .then(blob => {
        const url = URL.createObjectURL(blob)
        setQrCodeUrl(url);
      })
      .catch(error => console.error('Error:', error))
  }

  return (
    <div className="App">
      <button onClick={fetchCode}>Generate Code</button>
      {code && <p>Code: {code}</p>}
      {code && !qrCodeUrl && <button onClick={fetchQRCode}>Generate QR Code</button>}
      {qrCodeUrl && <img src={qrCodeUrl} alt="QR Code" />}
    </div>
  )
}

export default App