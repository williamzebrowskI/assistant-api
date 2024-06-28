import React from 'react';
import ReactDOM from 'react-dom';
import { Widget } from '../../src';

import './styles.css';

const App = () => (
    <div className='widget__wrapper'>
        <Widget termsOfUseUrl='/' introMessage={introMessage} />
    </div>
);

const introMessage = <>
    <p>Hello, I'm Wyatt, your digital FAFSA advisor! What can I help you with today? By chatting with me, you agree to the <a href='/'>Terms of Use.</a></p>
</>

ReactDOM.render(<App />, document.getElementById('app'));

