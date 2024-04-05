import React from 'react';
import './styles.css';

import WidgetWindow from './WidgetWindow';

const Widget = ({ introMessage, sessionId }) => {
    return <WidgetWindow introMessage={introMessage} sessionId={sessionId} />;
}

export default Widget;