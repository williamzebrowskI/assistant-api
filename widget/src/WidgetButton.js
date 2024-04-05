import React from 'react';

import wyattAvatar from './images/wyatt-chat-avatar.svg';
import closeIcon from './images/close-icon.svg';

const WidgetButton = ({ open, handleButtonClick }) => {

    return (
        <button className='widget-button' name={open ? 'Close chat' : 'Open chat'} onClick={handleButtonClick}>
            <div className='widget-button__wrapper'>
                {open ?
                    <div className='widget-button__close'>
                        <img className='widget-button__close' aria-hidden={true} src={closeIcon} />
                    </div>
                    :
                    <img aria-hidden={true} src={wyattAvatar} />
                }
            </div>
            {/* <div className='widget-button__pill-cta'>
                Chat Now
            </div> */}
        </button>
    )
}

export default WidgetButton;