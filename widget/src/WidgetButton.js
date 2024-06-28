import React, { useState, useEffect } from 'react';

import wyattAvatar from './images/wyatt-chat-avatar.svg';
import closeIcon from './images/close-icon.svg';

const WidgetButton = ({ open, handleButtonClick, hasEngaged }) => {
    const [pillVisible, setPillVisible] = useState(false);

    useEffect(() => {
        const toggleVisibility = () => {
            setPillVisible(true);
            setTimeout(() => {
                setPillVisible(false);
            }, 3000);
        };

        toggleVisibility();

        const interval = setInterval(toggleVisibility, 8000);

        return () => clearInterval(interval);
    }, []);

    return (
        <button className='widget-button' name={open ? 'Close chat' : 'Open chat'} onClick={handleButtonClick}>
            <div className='widget-button__container'>
                <div className='widget-button__wrapper'>
                    {open ?
                        <div className='widget-button__close'>
                            <img className='widget-button__close' aria-hidden={true} src={closeIcon} />
                        </div>
                        :
                        <img aria-hidden={true} src={wyattAvatar} />
                    }
                </div>
                {!hasEngaged &&
                    <div className={pillVisible ? `widget-button__pill-cta__visible widget-button__pill-cta widget-open__${open} ` : `widget-button__pill-cta widget-open__${open}`}>
                        <p>Chat Now</p>
                    </div>
                }
            </div>
        </button>
    )
}

export default WidgetButton;