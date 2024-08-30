const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 8001;

// Serve static files from the current directory
app.use(express.static(__dirname));

// Serve the chat widget HTML file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Node.js server is running on port ${PORT}`);
});