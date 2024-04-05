import React, { useEffect, useState } from 'react';
import './styles.css';

import WidgetWindow from './WidgetWindow';
import WidgetButton from './WidgetButton';
import { getCookieValue } from '../helpers/uuidHelpers';

const Widget = ({ introMessage, onClick, sessionId }) => {
    const [open, setOpen] = useState(false);
    const [clickedOpen, setClickedOpen] = useState(false);
    const [hasEngaged, setHasEngaged] = useState(false);

    const handleButtonClick = () => {
        if (typeof onClick === 'function') onClick();
        setOpen(!open);
        if (!clickedOpen) setClickedOpen(true);
    }

    useEffect(() => {
        setHasEngaged(getCookieValue('BDT_ChatBot_User_UUID').length > 0)
    }, [clickedOpen])

    return (
        <div className='complete-widget__container'>
            <WidgetWindow introMessage={introMessage} sessionId={sessionId} open={open} clickedOpen={clickedOpen} />
            <WidgetButton open={open} handleButtonClick={handleButtonClick} hasEngaged={hasEngaged} />
        </div>
    )
}

export default Widget;