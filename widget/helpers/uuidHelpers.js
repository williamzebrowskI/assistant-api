export const uuidv4 = () => {
    return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> c / 4)).toString(16)
    );
}

export const setWyattCookies = () => {
    const hasBdtChatBotUserCookie = document.cookie.split('; ').find(row => row.startsWith('BDT_ChatBot_User_UUID' + '='));
    if (!hasBdtChatBotUserCookie) {
        const userUuid = uuidv4();
        setCookie('BDT_ChatBot_User_UUID', userUuid, 2);
    }

    const hasBdtChatBotConversationCookie = document.cookie.split('; ').find(row => row.startsWith('BDT_ChatBot_Conversation_UUID' + '='));
    if (!hasBdtChatBotConversationCookie) {
        const conversationUuid = uuidv4();
        setCookie('BDT_ChatBot_Conversation_UUID', conversationUuid, 2);
    }
}

export const setCookie = (name, value, days) => {
    let expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/; Secure; SameSite=Lax";
}

export const getCookieValue = (cookieName) => {
    const name = cookieName + "=";
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) === 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

export const deleteCookie = (cookieName) => {
    const date = new Date();
    date.setTime(date.getTime() - (24 * 60 * 60 * 1000));
    document.cookie = `${cookieName}=; expires=${date.toUTCString()}; path=/`;
}