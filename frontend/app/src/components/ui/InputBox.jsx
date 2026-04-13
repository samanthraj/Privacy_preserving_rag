import { useState } from "react";

function InputBox({ onSend }) {
  const [text, setText] = useState("");

  const handleSend = () => {
    if (!text.trim()) return;
    onSend(text);
    setText("");
  };
   const handleClick = () => {
    console.log(text);   // 👉 prints input value
  };
 
  return (
    <div style={{
      display: "flex",
      padding: "10px",
      background: "#40414f"
    }}>
       <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ask something..."
        id="input-box"
        className="bg-gray-700 text-white rounded-md px-4 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
       />
      <button onClick={handleSend} style={{
        marginLeft: "10px",
        padding: "10px 20px",
        background: "#10a37f",
        color: "white",
        border: "none",
        borderRadius: "5px"
      }}>
        Send
      </button>
    </div>
  );
}

export default InputBox;