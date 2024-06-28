import React, { useState, useRef, useEffect } from 'react';

import io from 'socket.io-client';

import { setWyattCookies, getCookieValue } from '../helpers/uuidHelpers';

import sendIcon from './images/send-icon.svg';
import infoIcon from './images/info-icon.svg';
import wyattAvatar from './images/wyatt-chat-avatar.svg'

// TODO: beta tag hover action (?)
// TODO: add sessionId 

const WidgetWindow = ({ introMessage, open, sessionId, clickedOpen }) => {
    const [question, setQuestion] = useState("");
    const [messages, setMessages] = useState([{ sender: "assistant", message: introMessage }]);
    const [socket, setSocket] = useState({});
    const chatBodyRef = useRef(null);

    useEffect(() => {
        if (clickedOpen) {
            setWyattCookies();

            // const newSocket = io.connect('https://wyatt-openai-play.bdtrust.org/chat', {
            const newSocket = io.connect('http://localhost:8002/chat', {

                query: {
                    'userId': getCookieValue('BDT_ChatBot_User_UUID'), // KEY FOR CHAT PERSISTENCE
                    'conversationId': getCookieValue('BDT_ChatBot_Conversation_UUID'),
                    'referralUrl': window.location.search,
                    // 'sessionId': sessionId,
                }
            });

            console.log(newSocket, 'socket in useEffect')

            setSocket(newSocket);

            return () => {
                newSocket.disconnect();
            };
        }
    }, [clickedOpen]);

    useEffect(() => {
        if (socket.on) {
            console.log('socket.on')
            socket.on('assistant_message', (data) => {
                console.log(data, 'data from socket')
                addMessageToChat("assistant", data.text);
            });

            return () => {
                socket.off('assistant_message');
            };
        }
    }, [socket]);

    const convertImageLinksToImages = (inputText) => {
        const replacePatternImg = /<a href="(https?:\/\/\S+\.(?:png|jpg|jpeg|gif|svg))" target="_blank">(https?:\/\/\S+\.(?:png|jpg|jpeg|gif|svg))<\/a>/gim;
        return inputText.replace(replacePatternImg, '<a href="$1" target="_blank"><img src="$1" style="max-width:100%;height:auto;"></a>');
    };

    const handleFormSubmit = async (e) => {
        e.preventDefault();

        addMessageToChat("user", question);

        socket.emit('user_message', {
            text: question,
            userId: getCookieValue('BDT_ChatBot_User_UUID'),
            conversationId: getCookieValue('BDT_ChatBot_Conversation_UUID'),
            currentPageUrl: window.location.href,
            referralUrl: window.location.search,
        });

        setQuestion('');

    };

    const addMessageToChat = (sender, message) => {
        console.log('adding message to chat: ', message)
        if (sender === "assistant") {
            message = convertImageLinksToImages(message);
        }


        setMessages((prevMessages) => [...prevMessages, { sender, message }]);

        setTimeout(() => {
            if (chatBodyRef.current) {
                chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
            }
        }, 0);
    };

    return (
        <div className={open ? 'chat-container' : 'chat-container chat-container__closed'}>
            <div className="chat-header">
                {/* <div className='beta-tag'>Beta <img src={infoIcon} /></div> */}
                <div className="chat-header__icon">
                    <img src={wyattAvatar} />
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
                                <img src={sendIcon} />
                            </button>
                        </div>
                    </form>
                    {/* <button className='chat-footer__speech-to-text'></button> */}
                </div>
                <div className='chat-footer__tou'>
                    <p>Wyatt is still learning and can make mistakes.</p>
                    <p>Consider checking important information on <a href='https://studentaid.gov/' target='_blank'>studentaid.gov</a></p>
                </div>
            </div>
        </div>
    );
};

export default WidgetWindow;