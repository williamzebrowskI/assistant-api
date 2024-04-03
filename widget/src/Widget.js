import React, { useState, useRef, useEffect } from 'react';
import './styles.css';

import { setWyattCookies, getCookieValue } from '../helpers/uuidHelpers';

// TODO: move all style attributes to css file
// TODO: make TOU link dynamic

const Widget = ({ termsOfUseUrl }) => {
    const [question, setQuestion] = useState("");
    const [messages, setMessages] = useState([]);
    const chatBodyRef = useRef(null);

    useEffect(() => {
        setWyattCookies();
    }, []);

    const handleFormSubmit = async (e) => {
        e.preventDefault();

        const conversationUuid = getCookieValue('BDT_ChatBot_Conversation_UUID');
        const userUuid = getCookieValue('BDT_ChatBot_User_UUID');

        addMessageToChat("user", question);

        let apiUrl = `https://wyatt-openai-play.bdtrust.org/query/?conversation_uuid=${conversationUuid}&user_id=${userUuid}`;
        let threadId = localStorage.getItem("threadId");

        if (threadId) {
            apiUrl += `&thread_id=${threadId}`;
        }

        let payload = {
            question,
            conversation_uuid: conversationUuid,
            user_id: userUuid,
            thread_id: threadId,
        };

        try {
            let response = await fetch(apiUrl, {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            let jsonResponse = await response.json();
            addMessageToChat("assistant", jsonResponse.response);

            if (jsonResponse.thread_id) {
                threadId = jsonResponse.thread_id;
                localStorage.setItem("threadId", threadId);
            }
        } catch (error) {
            console.error('Error:', error);
            addMessageToChat("assistant", "Error: Could not fetch the response.");
        }
        setQuestion('');
    };

    const addMessageToChat = (sender, message) => {
        setMessages((prevMessages) => [...prevMessages, { sender, message }]);
        setTimeout(() => {
            if (chatBodyRef.current) {
                chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
            }
        }, 0);
    };

    return (
        <div className="chat-container">
            <div className="chat-header">
                <div className="chat-header__icon">
                    {/* TODO: PLACEHOLDER FOR WYATT ICON */}
                </div>
                <h2>Ask me your FAFSA questions!</h2>
            </div>
            <div className="chat-body" ref={chatBodyRef}>
                {messages.map((msg, i) => (
                    <div key={i} className={'message ' + (msg.sender === "user" ? "user-message" : "assistant-message")}>
                        <p>{msg.message}</p>
                    </div>
                ))}
            </div>
            <div className="chat-footer">
                <div className='chat-footer__form-container'>
                    <form onSubmit={(e) => handleFormSubmit(e)}>
                        <div className='chat-footer__input-wrapper'>
                            <input
                                type="text"
                                value={question}
                                onChange={(e) => setQuestion(e.target.value)}
                                placeholder="Ask your FAFSA questions..."
                            />
                            <button
                                type="submit"
                                disabled={question.length === 0}
                                className={question.length === 0 ? 'disabled' : ''}>
                                {/* TODO: REPLACE WITH ICON */}
                            </button>
                        </div>
                    </form>
                    {/* <button className='chat-footer__speech-to-text'></button> */}
                </div>
                <div className='chat-footer__tou'>
                    <p>By chatting with Wyatt you agree to the <a href={termsOfUseUrl} target='_blank'>Terms of Use</a>.</p>
                </div>
            </div>
        </div >
    );
};

export default Widget;