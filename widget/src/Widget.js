import React, { useState } from 'react';
import './styles.css';

import WidgetWindow from './WidgetWindow';
import WidgetButton from './WidgetButton';

const Widget = ({ introMessage, onClick, sessionId }) => {
    const [open, setOpen] = useState(false);
    const [hasEngaged, setHasEngaged] = useState(false);

    const handleButtonClick = () => {
        if (typeof onClick === 'function') onClick();
        setOpen(!open);
        if (!hasEngaged) setHasEngaged(true);
    }

    return (
        <div className='complete-widget__container'>
            <WidgetWindow introMessage={introMessage} sessionId={sessionId} open={open} />
            <WidgetButton open={open} handleButtonClick={handleButtonClick} hasEngaged={hasEngaged} />
        </div>
    )
}

export default Widget;