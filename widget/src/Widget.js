import React, { useState } from 'react';
import './styles.css';


const Widget = () => {
    const [question, setQuestion] = useState("");

    return (
        <div className="chat-container">
            <div className="chat-header">
                <h2>OpenAI Assistant Chat</h2>
            </div>
            <div className="chat-body">
                {/* <div className="chat-body" ref={chatBodyRef}> */}
                {/* {messages.map((msg, index) => (
                    <div key={index} className={msg.sender === "user" ? "message-user" : "message-assistant"}>
                        <p>{msg.message}</p>
                    </div>
                ))} */}
            </div>
            <div className="chat-footer">
                <form onSubmit={() => console.log('triggered submit') /* TODO: REPLACE WITH SUBMISSION HANDLER FUNCTION */}>
                    <input
                        type="text"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        placeholder="Type a message..."
                        required
                        style={{ width: "80%" }}
                    />
                    <input type="submit" value="Send" style={{ width: "18%" }} />
                </form>
            </div>
        </div>
    );
};

export default Widget;