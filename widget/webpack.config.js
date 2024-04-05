const path = require('path');

module.exports = {
  entry: {
    library: './src/index.js',
    example: './demo/src/App.js',
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name]_fafsa-chatgpt-assistant.js',
    library: '[name]',
    libraryTarget: 'umd',
    globalObject: 'this'
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react']
          }
        }
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
      {
        test: /\.(png|svg)$/,
        type: 'asset/resource',
      },
    ]
  },
  devServer: {
    static: {
      directory: path.join(__dirname, 'demo'),
    },
    compress: true,
    port: 3000,
  },
  externals: {
    react: 'react',
    'react-dom': 'react-dom',
  },
};