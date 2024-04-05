import React from 'react';

import wyattAvatar from './images/wyatt-chat-avatar.svg';

const WidgetButton = ({ open, handleButtonClick }) => {

    return (
        <button className='widget-button' name={open ? 'Close chat' : 'Open chat'} onClick={handleButtonClick}>
            <div className='widget-button__wrapper'>
                {open ?
                    <img aria-hidden={true} />
                    :
                    <img aria-hidden={true} src={wyattAvatar} />
                }
            </div>
            <div className='widget-button__pill-cta'>
                Chat Now
            </div>
        </button>
    )
}

export default WidgetButton;