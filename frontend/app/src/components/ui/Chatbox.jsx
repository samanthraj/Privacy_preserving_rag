import React, { useState, useEffect, useRef } from "react";

const Chatbox = () => {
  const [text, setText] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  const username = localStorage.getItem("username");
  const user_id = localStorage.getItem("user_id");

  // 🔐 Protect route
  useEffect(() => {
    if (!user_id) {
      window.location.href = "/";
    }
  }, []);

  // 📥 Load history
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch(`http://localhost:5000/history/${user_id}`);
        const data = await res.json();

        console.log("HISTORY:", data); // 🔥 DEBUG

        setMessages(data);
      } catch (err) {
        console.error("History error:", err);
      }
    };

    if (user_id) fetchHistory();
  }, [user_id]);

  // 💬 Send message
  const handleSend = async () => {
    if (!text.trim()) return;

    const userMessage = { role: "user", content: text };

    setMessages((prev) => [...prev, userMessage]);
    setText("");

    try {
      setLoading(true);

      const res = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: text,
          user_id: user_id,
        }),
      });

      const data = await res.json();

      console.log("API RESPONSE:", data); // 🔥 DEBUG

      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content: data.reply || "No response from server",
        },
      ]);
    } catch (err) {
      console.error("Chat error:", err);
      setMessages((prev) => [
        ...prev,
        { role: "bot", content: "Error getting response" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // 🔄 Auto scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 🧹 Clear chat
  const clearChat = async () => {
    try {
      await fetch("http://localhost:5000/clear", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id }),
      });

      setMessages([]);
    } catch (err) {
      console.error("Clear error:", err);
    }
  };

  // 🚪 Logout
  const handleLogout = () => {
    localStorage.clear();
    window.location.href = "/";
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">

      {/* Header */}
      <div className="flex justify-between items-center px-6 py-4 border-b border-gray-700">
        <h2>Welcome, {username}</h2>

        <div className="flex gap-2">
          <button onClick={clearChat} className="bg-yellow-600 px-3 py-1 rounded">
            Clear
          </button>

          <button onClick={handleLogout} className="bg-red-600 px-3 py-1 rounded">
            Logout
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.map((msg, index) => {
          console.log("MSG:", msg); // 🔥 DEBUG

          return (
            <div
              key={index}
              className={`max-w-2xl px-4 py-3 rounded-xl ${
                msg.role === "user"
                  ? "bg-blue-600 ml-auto"
                  : "bg-gray-700"
              }`}
            >
              {/* 🔥 SAFE RENDER */}
              {typeof msg.content === "string"
                ? msg.content
                : JSON.stringify(msg.content)}
            </div>
          );
        })}

        {loading && (
          <div className="bg-gray-700 px-4 py-2 rounded-xl w-fit">
            Thinking...
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-700 p-4">
        <div className="flex items-center gap-2 bg-gray-800 rounded-xl px-3 py-2">
          <input
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask something..."
            className="flex-1 bg-transparent text-white placeholder-gray-400 focus:outline-none"
          />

          <button
            onClick={handleSend}
            className="bg-blue-600 px-4 py-2 rounded-lg"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chatbox;