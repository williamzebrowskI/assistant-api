import React, { useState } from 'react';
import './styles.css';

import WidgetWindow from './WidgetWindow';
import WidgetButton from './WidgetButton';

const Widget = ({ introMessage, onClick, sessionId }) => {
    const [open, setOpen] = useState(false);

    const handleButtonClick = () => {
        console.log('handling button click open state');
        if (typeof onClick === 'function') onClick();
        setOpen(!open);
    }

    console.log(open, 'open state')

    return <div className='complete-widget__container'>
        <WidgetWindow introMessage={introMessage} sessionId={sessionId} open={open} />
        <WidgetButton open={open} handleButtonClick={handleButtonClick} />
    </div>;
}

export default Widget;