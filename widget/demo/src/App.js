import React from 'react';
import ReactDOM from 'react-dom';
import { Widget } from '../../src';

import './styles.css';

const App = () => (
    <div className='widget__wrapper'>
        <Widget termsOfUseUrl='/' />
    </div>
);

ReactDOM.render(<App />, document.getElementById('app'));

