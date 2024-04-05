import React, { useEffect, useState } from 'react';
import './styles.css';

import WidgetWindow from './WidgetWindow';
import WidgetButton from './WidgetButton';

import { getCookieValue } from '../helpers/uuidHelpers';

const Widget = ({ introMessage, onClick, sessionId }) => {
    const [open, setOpen] = useState(false);
    const [hasEngaged, setHasEngaged] = useState(false);

    const handleButtonClick = () => {
        console.log('handling button click open state');
        if (typeof onClick === 'function') onClick();
        setOpen(!open);
    }

    useEffect(() => {
        setHasEngaged(getCookieValue('BDT_ChatBot_User_UUID').length > 0);
    }, [])

    console.log(open, 'open state')

    return <div className='complete-widget__container'>
        <WidgetWindow introMessage={introMessage} sessionId={sessionId} open={open} />
        <WidgetButton open={open} handleButtonClick={handleButtonClick} hasEngaged={hasEngaged} />
    </div>;
}

export default Widget;