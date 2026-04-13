import { useState } from 'react'
import { Login } from './components/ui/Login'
import { Registration } from './components/ui/Registration'
import Chatbox from './components/ui/Chatbox';
import { BrowserRouter, Routes, Route } from "react-router-dom";



import './App.css'


function App() {
  const [count, setCount] = useState(0)
 

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Registration />} />
        <Route path="/chat" element={<Chatbox />} />
      </Routes>
    </BrowserRouter>
  
  );
  }
 
 export default App
